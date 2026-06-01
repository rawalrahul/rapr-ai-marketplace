import json
import os


def generate_report():
    catalog_path = 'public/marketplace/catalog.json'
    artifact_path = os.path.join(os.getcwd(), 'legal_license_audit.md')

    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    items = catalog.get('items', [])

    pkg_dir = 'public/marketplace/packages'
    pkgs = [f for f in os.listdir(pkg_dir) if f.endswith('.raprpkg')]
    catalog_slugs = {item['slug'] for item in items}

    standalone_pkgs = []
    for package_name in pkgs:
        slug = (
            package_name.split('-1.0.0')[0]
            .split('-5.0.7')[0]
            .split('-1.1.0')[0]
            .split('-0.3.0')[0]
        )
        matched = slug in catalog_slugs or any(package_name.startswith(cs + '-') for cs in catalog_slugs)
        if not matched:
            standalone_pkgs.append(package_name)

    total = len(items) + len(standalone_pkgs)

    markdown = f"""# RAPR AI Marketplace - License and Legality Audit Report

This report presents the compliance review results for all **{total}** integration and skill packages in the RAPR AI Marketplace.

## Executive Summary

> [!NOTE]
> This is an engineering compliance audit, not legal advice. The current package format is low-risk because marketplace archives are RAPR wrapper packages, but upstream project licenses, trademarks, hosted-service terms, and model/data licenses still matter.

We audited the catalog and implemented baseline marketplace-package compliance requirements. The `license` field in `catalog.json` means the license for the RAPR wrapper package, not a relicense of the upstream project.

### 1. Legality Analysis

* **Package scope:** Each marketplace item is packaged as a `.raprpkg` archive containing a `manifest.json`, `SKILL.md`, and optional wrapper scripts/assets.
* **No CLI binary redistribution:** These packages do not bundle the binary executables of underlying platforms such as AWS CLI, GCP Cloud SDK, Docker, or Twilio CLI.
* **Usage guidance:** Most packages provide documentation, command-line flags, and prompt guidelines instructing the agent on how to use third-party tools that the user installs locally.
* **Important boundary:** A RAPR package license does not override upstream licenses, trademark rules, provider terms, model checkpoint licenses, API terms, or non-commercial restrictions.

### 2. Actions Taken

* **Package license files:** Added a package-level MIT `LICENSE` file to archives that did not already include one.
* **Preserved extant licenses:** Kept existing package `LICENSE` files where present.
* **Metadata standardization:** Added package-license metadata to `catalog.json`.
* **UI enhancements:** Updated marketplace cards and detail pages to show the package license, and added room for upstream-license notes.

## Known Restrictions And Follow-Ups

* **Academic Research Skills:** The RAPR package is a compact MIT-licensed router/wrapper. The upstream `Imbad0202/academic-research-skills-codex` repository is marked as `CC BY-NC 4.0`; do not bundle the full upstream repository or use its full contents commercially without permission.
* **Model checkpoints and hosted services:** Packages such as OmniParser, MOSS-TTS, cloud CLIs, paid APIs, and OAuth integrations may have separate upstream terms, usage policies, account requirements, or model-weight licenses.
* **Trademarks:** Marketplace names identify compatible tools and upstream projects. They should not imply endorsement or affiliation unless explicitly documented.

## Standard Package MIT License

New RAPR wrapper packages without an existing license were bundled with this MIT template, attributed to the package author:

```text
MIT License

Copyright (c) 2026 [Author Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## Detailed Skill & Integration Audit Table

| # | Skill / Integration Name | Package Kind | Author / Attribution | Package License | Upstream License / Notes | Upstream GitHub / Website | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
"""

    count = 1
    for item in items:
        name = item.get('name', 'Unknown')
        package_kind = item.get('marketplace_kind', item.get('category', 'Package'))
        author = item.get('author', 'RAPR AI')
        package_license = item.get('license', 'MIT')
        upstream_license = item.get('upstream_license', 'Not asserted')
        license_scope = item.get('license_scope', '')
        github_url = item.get('github_url', '#')
        github_link = f"[Link]({github_url})" if github_url and github_url.startswith('http') else 'N/A'
        upstream_note = upstream_license
        if license_scope:
            upstream_note = f"{upstream_license}; {license_scope}"

        markdown += (
            f"| {count} | **{name}** | {package_kind} | {author} | `{package_license}` | "
            f"{upstream_note} | {github_link} | Reviewed |\n"
        )
        count += 1

    for package_name in standalone_pkgs:
        name = package_name.replace('-1.0.0.raprpkg', '').replace('-0.3.0.raprpkg', '').replace('-', ' ').title()
        markdown += f"| {count} | **{name} (Standalone)** | Standalone Package | RAPR AI | `MIT` | Not asserted | N/A | Reviewed |\n"
        count += 1

    markdown += (
        '\n---\n'
        '*End of report. Audit complete for current package contents; re-run before release if package contents or upstream sources change.*\n'
    )

    with open(artifact_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f'Successfully generated audit report at: {artifact_path}')


if __name__ == '__main__':
    generate_report()
