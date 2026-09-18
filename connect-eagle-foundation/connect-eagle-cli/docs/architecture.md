# Architecture and safety boundaries

- `repository.py`: read-only Git discovery, URL normalization, lightweight metadata inference. Does not import or execute project code.
- `metadata.py`: bounded YAML parser (64 KiB), duplicate-key/alias rejection and canonical Draft 2020-12 JSON Schema.
- `github.py`: GitHub CLI transport. Reads registry state, validates slug ownership, forks when necessary, creates one-file trees and commits, then opens a PR. Never force-pushes or moves an existing ref.
- `registry.py`: collection-level uniqueness checks and deterministic JSON export.
- `cli.py`: Typer presentation and explicit local/remote actions.

The public v1 contract is `.connect-eagle.yml`, not any GitHub organization name. Registry location is explicitly configured, allowing organization renames and deployment under another owner without releasing a new CLI.

The schema is packaged inside the wheel, so validation works offline. The registry vendors the small validation subset; `test_schema_sync.py` verifies that the subset and schema match the canonical CLI source while these projects are staged together. Later releases should sync this versioned contract through a reviewed update PR.

No contributor code is uploaded. Authentication stays with `gh`; the application never asks for or stores a token. Remote errors suppress raw subprocess output so credentials embedded in a remote cannot leak into diagnostics. Public metadata URLs cannot contain credentials or query strings. Private datasets should be represented only by a public descriptive landing page.

v0.1 GitHub submission uses github.com. GitHub Enterprise hosting, remote merge-status reconciliation, arbitrary nested registry directories and automatic source-metadata verification are deferred. An organization administrator must enforce required checks and review policies outside this CLI.
