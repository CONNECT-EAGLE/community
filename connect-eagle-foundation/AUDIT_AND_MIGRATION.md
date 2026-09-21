# CONNECT-SBG audit and migration decision

Audit date: 2026-09-18. Connected GitHub identity: `falhezaimi`.

## Evidence

| Asset | Observed state | Decision |
| --- | --- | --- |
| `CONNECT-SBG/testrepo` | Public; initial branch creation returned HTTP 403, resolved by installing the connector on the organization. Audited `main` at `c11d82179bb19bac5c0399dfcaaaab3a4d140600`; latest commit 2025-10-29. Sixteen files including drought notebooks, backup/filtered variants, a report, a comparison artifact and requirements. No README, license, citation, workflow or community files in the inspected tree. | Preserve every existing path and blob. Foundation published on `feat/connect-eagle-foundation` through [PR #2](https://github.com/CONNECT-EAGLE/community/pull/2). |
| `inthisclimate/CONNECT-SBG` | Public; read-only through the connection. Default `main` at `56a4588eead7beab8a842405c2e3b5eae5bc4492`; latest commit 2025-11-12. Intertidal-Cabrera research, ECOSTRESS/EMIT tutorials, Python utilities, README and Apache-2.0 license. | Preserve in place. Link to it as historical research; do not rebrand or move another owner's work. |
| Original organization inventory | Organization-scoped repository search returned `CONNECT-SBG/testrepo`. The general organization-membership/listing endpoints returned no memberships, despite repository-level write/admin permissions. | Treat repository permissions as evidence of access to this repository only. Inventory may exclude private/inaccessible assets; do not claim the organization was exhaustively audited. |

Sources: [original repository](https://github.com/CONNECT-EAGLE/community), [historical research repository](https://github.com/inthisclimate/CONNECT-SBG). Trees, recent commit lists, the historical README/subproject README and original requirements were inspected. Scientific notebooks were inventoried, not executed or scientifically revalidated.

## Preserve and reuse

Keep all notebook revisions, author attribution, existing branches and commit history. The historical repository has useful research descriptions, examples and tutorials to link from a future showcase. No legacy scientific code is required by the registration CLI, so copying it would create unnecessary maintenance and attribution work.

The original requirements are an old environment snapshot containing Conda internals, platform-specific packages and development builds. Preserve it with its analysis history; use a new lightweight `pyproject.toml` for the CLI. Notebook checkpoints, backup variants and platform metadata are candidates for later cleanup only after their owners determine which analyses are canonical. Nothing is deleted or archived now.

## Staging architecture

The connector exposes branch/commit/PR operations but does not expose repository or organization creation/renaming. The six logical repositories are therefore staged under `connect-eagle-foundation/` in the existing repository. Initial publication failed with HTTP 403 because the connected app lacked organization access; installing the connector on CONNECT-SBG resolved that failure. The feature branch and PR are now published. The root GitHub Actions workflow runs the new CLI tests and registry validation. Legacy analyses are never executed by it.

This is a staging arrangement, not a claim that six live repositories or organization defaults already exist. Split each prepared directory after repository creation becomes available. Keep the original repository as the historical source. The registry must be published with `projects/` at its root before the CLI's live submission workflow can target it.

No organization rename, repository transfer, archival, history rewrite, direct commit to `main`, or historical-file overwrite is performed. The new MIT license applies within the new foundation components; it does not relicense the pre-existing drought material.

## Launch sequence

1. Review the foundation PR and its checks.
2. Create `connect-eagle-cli`, `project-registry`, `templates`, `community`, `.github` and `website` under the chosen organization. Keeping `CONNECT-SBG` as the slug initially avoids unnecessary migration; use the new community display name in documentation.
3. Split prepared directories through new branches, retaining meaningful component commit history; publish via PRs.
4. Configure registry branch protection, maintainer review and actual moderation/security contacts.
5. Run authenticated live registration with consenting project maintainers, then invite the first cohort.

Any eventual organization rename should have its own short redirect/link audit and owner decision. Scientific projects never need to transfer into the organization to participate.

## Publication result

Published [PR #2](https://github.com/CONNECT-EAGLE/community/pull/2) from `feat/connect-eagle-foundation` into `main`. The four initial component commits reproduce the prepared local source tree exactly; follow-up changes document publication and address CI findings. Historical paths and blobs remain unchanged. No merge, repository creation, organization rename or repository-settings change is included. Current automation results are available in the [PR checks](https://github.com/CONNECT-EAGLE/community/pull/2/checks).
