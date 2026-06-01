# Contributing

Thanks for helping improve the RAPR AI Marketplace.

## What To Add

Good marketplace entries are useful, specific, and honest about what they contain.

Accepted package types:

- RAPR-authored skills
- Curated public GitHub repo wrappers
- CLI connectors that call locally installed tools
- OAuth/service connector metadata
- Built-in RAPR integration metadata

## Contribution Rules

- Do not include secrets, tokens, private URLs, or credentials.
- Do not bundle upstream binaries unless the license clearly permits redistribution and the package includes the required notices.
- Do not imply upstream endorsement or affiliation unless it is documented.
- Keep package descriptions factual and avoid exaggerated legal or performance claims.
- Include a `LICENSE` file in every `.raprpkg`.
- Use `license` for the RAPR wrapper package license.
- Use `upstream_license` when the upstream project has a material license users should know about.
- Use `license_scope` to clarify whether the package is a wrapper, CLI connector, or bundled work.

## Package Classification

Choose the narrowest accurate `marketplace_kind`:

- `RAPR Skill` for RAPR-authored reusable agent instructions and workflow guidance.
- `Curated Public Repo` for public GitHub/project discovery wrappers.
- `CLI Connector` for RAPR-authored guidance around a locally installed command-line tool.
- `OAuth Connector` for RAPR-authored metadata around account connection flows.
- `Built-in Integration` for product functionality shipped directly in RAPR AI.

CLI and OAuth entries should describe RAPR's connector flow, not copy upstream binaries, SDK source code, private docs, or provider branding beyond factual names and links.

## Validation

Run:

```bash
python scripts/validate_marketplace.py
```

The validator checks catalog shape, package existence, package manifests, license files, and download URLs.
