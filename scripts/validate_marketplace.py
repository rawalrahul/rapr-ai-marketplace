import json
import os
import sys
import zipfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, 'catalog.json')
PACKAGE_DIR = os.path.join(ROOT, 'packages')
VALID_KINDS = {
    'RAPR Skill',
    'Curated Public Repo',
    'CLI Connector',
    'OAuth Connector',
    'Built-in Integration',
}


def fail(errors, message):
    errors.append(message)


def main():
    errors = []

    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    items = catalog.get('items', [])
    seen = set()

    for item in items:
        slug = item.get('slug')
        if not slug:
            fail(errors, 'Item missing slug')
            continue
        if slug in seen:
            fail(errors, f'Duplicate slug: {slug}')
        seen.add(slug)

        for field in ['name', 'description', 'long_description', 'category', 'author', 'version', 'github_url', 'license']:
            if not item.get(field):
                fail(errors, f'{slug}: missing {field}')

        kind = item.get('marketplace_kind')
        if kind not in VALID_KINDS:
            fail(errors, f'{slug}: invalid marketplace_kind {kind!r}')

        download_url = item.get('download_url')
        if download_url:
            package_name = download_url.rsplit('/', 1)[-1]
            package_path = os.path.join(PACKAGE_DIR, package_name)
            if not os.path.exists(package_path):
                fail(errors, f'{slug}: missing package file {package_name}')
                continue

            try:
                with zipfile.ZipFile(package_path, 'r') as zf:
                    names = zf.namelist()
                    lower_names = [name.lower() for name in names]
                    if 'manifest.json' not in lower_names:
                        fail(errors, f'{slug}: package missing manifest.json')
                    if 'skill.md' not in lower_names:
                        fail(errors, f'{slug}: package missing SKILL.md')
                    if not any('license' in name or 'notice' in name for name in lower_names):
                        fail(errors, f'{slug}: package missing LICENSE/NOTICE')
            except zipfile.BadZipFile:
                fail(errors, f'{slug}: package is not a valid zip archive')

    if errors:
        print('Marketplace validation failed:')
        for error in errors:
            print(f'- {error}')
        return 1

    print(f'Marketplace validation passed: {len(items)} catalog items')
    return 0


if __name__ == '__main__':
    sys.exit(main())

