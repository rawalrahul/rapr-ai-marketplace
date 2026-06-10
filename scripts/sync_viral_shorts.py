import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.json"
PACKAGES_DIR = ROOT / "packages"
SLUG = "viral-shorts"
DEFAULT_REPO = "rawalrahul/viral-shorts-skill"
DEFAULT_REF = "main"
CATALOG_DESCRIPTION = (
    "Creative-director video skill for retention shorts, podcast cutdowns, "
    "footage-led hybrids, and animated explainers with Remotion."
)

INCLUDE_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "SKILL.md",
    "manifest.json",
}
INCLUDE_DIRS = (
    "assets/remotion-viral-short/",
    "references/",
)
EXCLUDE_PARTS = {
    ".git",
    ".github",
    ".next",
    "dist",
    "node_modules",
    "out",
    "tmp",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def short_description(description):
    text = " ".join(description.split())
    if len(text) <= 220:
        return text
    return text[:217].rstrip() + "..."


def download_repo_zip(repo, ref, target_dir):
    archive_url = f"https://github.com/{repo}/archive/refs/heads/{ref}.zip"
    archive_path = target_dir / "source.zip"
    urllib.request.urlretrieve(archive_url, archive_path)

    extract_dir = target_dir / "source"
    with zipfile.ZipFile(archive_path, "r") as zf:
        zf.extractall(extract_dir)

    roots = [path for path in extract_dir.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one extracted root in {extract_dir}, found {len(roots)}")
    return roots[0]


def git_tracked_files(source_dir):
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=source_dir,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    files = result.stdout.decode("utf-8", errors="replace").split("\0")
    return [path for path in files if path]


def should_include(relative_path):
    path = relative_path.replace("\\", "/")
    parts = set(path.split("/"))
    if parts & EXCLUDE_PARTS:
        return False
    return path in INCLUDE_FILES or any(path.startswith(prefix) for prefix in INCLUDE_DIRS)


def source_files(source_dir):
    tracked = git_tracked_files(source_dir)
    if tracked is None:
        candidates = [
            str(path.relative_to(source_dir)).replace("\\", "/")
            for path in source_dir.rglob("*")
            if path.is_file()
        ]
    else:
        candidates = tracked

    return sorted(path for path in candidates if should_include(path) and (source_dir / path).is_file())


def latest_changelog(changelog_text):
    lines = changelog_text.splitlines()
    start = None
    end = None

    for index, line in enumerate(lines):
        if line.startswith("## "):
            if start is None:
                start = index
            else:
                end = index
                break

    if start is None:
        return "Synced from upstream viral-shorts-skill repository."

    section = "\n".join(lines[start:end]).strip()
    return section or "Synced from upstream viral-shorts-skill repository."


def update_catalog(source_dir, package_name, package_size):
    catalog = read_json(CATALOG_PATH)
    manifest = read_json(source_dir / "manifest.json")
    readme = (source_dir / "README.md").read_text(encoding="utf-8")
    changelog_path = source_dir / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
    today = date.today().isoformat()

    item = next((entry for entry in catalog.get("items", []) if entry.get("slug") == SLUG), None)
    if item is None:
        raise RuntimeError(f"Could not find {SLUG} in catalog.json")

    keywords = manifest.get("keywords", item.get("keywords", []))
    item.update(
        {
            "name": manifest.get("name", item.get("name", "Viral Shorts")),
            "description": CATALOG_DESCRIPTION,
            "long_description": readme,
            "author": manifest.get("author", item.get("author", "RAPR AI")),
            "version": manifest.get("version", item.get("version", "1.0.0")),
            "min_app_version": manifest.get("min_app_version", item.get("min_app_version", "2.0.0")),
            "github_url": f"https://github.com/{DEFAULT_REPO}",
            "download_url": f"/marketplace/packages/{package_name}",
            "file_size": format_file_size(package_size),
            "keywords": keywords,
            "updated_at": today,
            "category": "skill",
            "marketplace_kind": "RAPR Skill",
            "license": item.get("license", "MIT"),
            "license_scope": "This package contains RAPR-authored skill instructions, references, workflow guidance, setup metadata, and bundled assets.",
        }
    )

    if changelog:
        item["release_notes"] = latest_changelog(changelog)

    catalog["updated_at"] = today
    write_json(CATALOG_PATH, catalog)


def build_package(source_dir, package_name):
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    package_path = PACKAGES_DIR / package_name
    files = source_files(source_dir)

    required = {"manifest.json", "SKILL.md", "LICENSE"}
    missing = [path for path in required if path not in files]
    if missing:
        raise RuntimeError(f"Skill source is missing required package files: {', '.join(missing)}")

    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for relative_path in files:
            zf.write(source_dir / relative_path, relative_path)

    return package_path


def remove_old_packages(keep_name):
    for package_path in PACKAGES_DIR.glob(f"{SLUG}-*.raprpkg"):
        if package_path.name != keep_name:
            package_path.unlink()


def parse_args():
    parser = argparse.ArgumentParser(description="Sync the Viral Shorts marketplace package from its source repo.")
    parser.add_argument(
        "--source",
        default=os.environ.get("VIRAL_SHORTS_SKILL_PATH"),
        help="Local viral-shorts-skill checkout. Defaults to downloading from GitHub.",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("VIRAL_SHORTS_SKILL_REPO", DEFAULT_REPO),
        help=f"GitHub owner/repo to download when --source is omitted. Default: {DEFAULT_REPO}",
    )
    parser.add_argument(
        "--ref",
        default=os.environ.get("VIRAL_SHORTS_SKILL_REF", DEFAULT_REF),
        help=f"Branch name to download when --source is omitted. Default: {DEFAULT_REF}",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    temp_dir = None

    try:
        if args.source:
            source_dir = Path(args.source).resolve()
            if not source_dir.exists():
                raise RuntimeError(f"Source path does not exist: {source_dir}")
        else:
            temp_dir = Path(tempfile.mkdtemp(prefix="viral-shorts-sync-"))
            source_dir = download_repo_zip(args.repo, args.ref, temp_dir)

        manifest = read_json(source_dir / "manifest.json")
        version = manifest.get("version")
        if not version:
            raise RuntimeError("manifest.json is missing version")

        package_name = f"{SLUG}-{version}.raprpkg"
        package_path = build_package(source_dir, package_name)
        remove_old_packages(package_name)
        update_catalog(source_dir, package_name, package_path.stat().st_size)

        print(f"Synced {SLUG} {version} from {source_dir}")
        print(f"Wrote {package_path.relative_to(ROOT)}")
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
