# Verification report

Verification date: 2026-09-18. Local environment: Linux, Python 3.12.

## Automated checks

- 57 unit/integration/contract tests passed locally.
- Ruff lint passed.
- Five project-template metadata examples validated.
- Empty production registry validated and its JSON export path is tested.
- Wheel and source distribution built successfully. A clean virtual environment installed the wheel; packaged schema lookup and all five smoke commands passed. The source archive includes documentation and test fixtures.

Tests cover Git discovery, subdirectories and linked worktrees; Python/JavaScript/R inference; non-GitHub and multiple remotes; credential stripping; required fields and schema versions; duplicate keys, unsafe YAML, filenames and URL collisions; missing license/citation; detached HEAD; in-progress merge; read-only dry-run; PR/fork construction, collision rejection, idempotent PR lookup and interrupted-submit recovery.

## Real-repository dogfood

Disposable local clones were used. No upstream project was modified or registered. All tracked files remained unchanged. The new metadata file and submission packets existed only in the disposable copies.

| Repository | Observed commit | Commands | Result |
| --- | --- | --- | --- |
| `inthisclimate/CONNECT-SBG` | `56a4588eead7` | init, status, doctor, submit --dry-run, submit | All returned 0; tracked files unchanged |
| `falhezaimi/DIAG3d` | `2c7220c66e29` | init, status, doctor, submit --dry-run, submit | All returned 0; tracked files unchanged |
| `falhezaimi/demo-branching` | `aafbeffda45a` | init, status, doctor, submit --dry-run, submit | All returned 0; tracked files unchanged |

The original intertidal repository exercised scientific README/license discovery with a missing citation. DIAG3d exercised a small existing software repository. demo-branching exercised a sparse repository. Additional synthetic fixtures cover an otherwise complete repository, absence of licensing/citation, ambiguous remotes, GitLab URLs, and worktrees. The exact clone snapshots above are the evidence; no claim is made about their general maintenance quality.

## Limits and deployment status

- `submit --push` is implemented and contract-tested, but has not been exercised with a live authenticated `gh` process in this environment. Fork/PR failures may leave a branch/fork for inspection; retries never force-update it.
- Separate destination repositories are prepared, not yet created. The staged registry is nested; live CLI submission expects a standalone registry with `projects/` at its root.
- Organization defaults, Discussions, branch protections and named moderation/security contacts are not yet active.
- No PyPI release is published.
- No live project is enrolled without its maintainer's review.
- GitHub publication is blocked: branch creation returned HTTP 403, `Resource not accessible by integration`. No remote branch or PR was created, so GitHub Actions has not run. Only the Linux/Python 3.12 local test results are verified; Windows/macOS and Python 3.11 are configured, not yet verified.
