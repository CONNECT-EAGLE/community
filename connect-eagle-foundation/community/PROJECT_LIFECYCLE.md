# Project lifecycle and naming

| Status | Meaning |
| --- | --- |
| `planning` | Scope defined; implementation or data collection has not begun |
| `active` | Work and maintenance are ongoing |
| `maintenance` | Stable project accepting fixes with limited new development |
| `completed` | Intended study or deliverable is complete; outputs remain available |
| `archived` | No active maintenance; retained for attribution and reproducibility |

Update status through a metadata PR. Archiving a registry record does not archive, delete or transfer the source repository. Stale projects remain visible with an accurate status; do not remove history to improve appearance.

Use readable kebab-case repository names. Registry slugs are lowercase ASCII letters/digits separated by single hyphens. Choose stable names based on the project, not the current maintainer or year unless scientifically meaningful. Slug collisions require a descriptive qualifier. Repository links must remain the source of truth across organization changes.
