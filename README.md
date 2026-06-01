# RAPR AI Marketplace

Open-source marketplace catalog for RAPR AI.

This repo collects RAPR skills, curated public GitHub repo wrappers, CLI connector metadata, OAuth connector metadata, and built-in integration metadata in one place so users do not have to hunt across the internet for setup instructions.

Most packages are lightweight convenience wrappers. They contain metadata, links, install commands, prompts, and agent instructions. Unless a package explicitly says otherwise, it does not bundle or relicense the upstream project.

## Package Types

- **RAPR Skill**: RAPR-authored skill instructions and workflow guidance.
- **Curated Public Repo**: A convenience wrapper around a useful public project, with links and setup guidance.
- **CLI Connector**: RAPR-authored connector guidance for using a command-line tool the user installs locally.
- **OAuth Connector**: RAPR connector metadata and authentication guidance for a service the user connects directly.
- **Built-in Integration**: Product metadata for functionality shipped in RAPR AI.

## Product Boundary

The catalog intentionally separates product connectors from curated open-source picks.

- **RAPR product connectors** include CLI connectors, OAuth connectors, and built-in integrations. These entries describe RAPR's own setup flow, connector metadata, and agent guidance. They do not ship the upstream CLI binary or replace provider terms.
- **Curated open-source picks** are discovery wrappers for public repositories. They provide attribution, source links, install commands, and license context so users can choose either RAPR Marketplace installation or the upstream project directly.
- **RAPR skills** are RAPR-authored instruction packages that can be installed into the app as reusable agent workflows.

## Structure

```text
catalog.json              Marketplace source of truth
packages/*.raprpkg        Installable marketplace packages
schemas/catalog.schema.json
scripts/                  Audit and validation helpers
legal_license_audit.md    Engineering compliance audit
```

## Legal Boundary

The package license applies to the RAPR marketplace wrapper package. It does not override upstream licenses, trademarks, provider terms, API terms, model checkpoint licenses, or non-commercial restrictions.

Users can install from this marketplace or go directly to the upstream public source linked by each package.
