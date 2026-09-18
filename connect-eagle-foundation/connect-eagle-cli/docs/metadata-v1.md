# Metadata schema v1

Canonical schema: `src/connect_eagle/schemas/project-v1.schema.json` (included in the wheel).

```yaml
schema: 1
project:
  name: Example thermal project
  slug: example-thermal-project
  description: A reproducible workflow for thermal observations.
eagle:
  mission: [TIR]
  topics: [remote-sensing, thermal-infrared]
project_type: research
status: active
collaboration:
  open: true
  looking_for: [researcher, developer]
repository: https://github.com/example/example-thermal-project
```

This is an illustrative record, not a registered project.

Required fields are exactly those above. `mission` is a nonempty list of `VSWIR`, `TIR`, or `supporting-technology`; represent both instruments with `[VSWIR, TIR]`. Topics and project slugs use lowercase ASCII letters, digits and hyphens. A slug is at most 80 characters. Descriptions are one sentence or a short paragraph (maximum 500 characters).

| Optional field | Shape |
| --- | --- |
| `maintainers`, `contributors` | List of objects with required `name`, optional `github` and `orcid` |
| `links.documentation`, `links.demo` | HTTPS URL |
| `links.datasets` | List of public HTTPS landing-page URLs |
| `publications` | List of objects with required `title`, optional `url` and `doi` |
| `license` | SPDX identifier when known, or `LicenseRef-…` for a detected custom license |
| `citation` | Object with optional relative `.cff` path (`cff`), citation `text`, or `doi` |

`project_type`: `research`, `software`, `dataset`, `tutorial`, `working-group`.

`status`: `planning`, `active`, `maintenance`, `completed`, `archived`. These describe the project, not its review status or a quality ranking.

`collaboration.open` controls whether the project welcomes collaboration. `looking_for` contains short role descriptions and may be empty. It never signs anyone up or creates invitations.

The schema rejects unknown fields and unsupported versions. YAML keys must be strings and unique; aliases are disallowed. Metadata must be no larger than 64 KiB. Links must use HTTPS and omit credentials/query parameters. Registration checks filename-to-slug consistency and duplicate repository identities, normalizing case, `.git`, and trailing slashes.

Breaking changes require a new schema version, migration guidance and a CLI capable of validating it. A registry stores complete metadata snapshots. Future catalogs wrap a sorted project list in `{"schema": 1, "projects": [...]}`. It is intentionally separate from any future website's internal schema.
