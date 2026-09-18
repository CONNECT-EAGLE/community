CONNECT-SBG needs a low-friction way for contributors to register existing work without moving repositories. This adds the C.O.N.N.E.C.T. EAGLE Git foundation while preserving every historical file and its history.

Changes:

- Python/Typer CLI v0.1 with `init`, `status`, `doctor`, `submit`, and registry validate/export commands.
- Packaged metadata schema v1, strict YAML validation, safe Git discovery, and a GitHub PR registration adapter.
- Independent Git-backed registry validator and validation workflow.
- Five starter templates, community governance/guidance, organization-profile files, and a website scope placeholder.
- Migration audit, verification report and continuation instructions.

Validation:

- 57 local automated tests pass on Linux/Python 3.12; lint passes.
- Three real repositories passed disposable-clone offline onboarding and submission preparation with tracked files unchanged.
- Five template examples validate; source and wheel distributions build; a clean wheel installation passes the smoke workflow.
- The workflow matrix prepares Windows/macOS/Linux tests on Python 3.11/3.12. Remote CI must be checked after this PR is created.

Limits:

- The six logical repositories are staged in directories, awaiting separate repository creation.
- `submit --push` is contract-tested; live authenticated CLI fork/PR/merge acceptance remains a launch check.
- Organization defaults, moderation contacts, branch protection and a PyPI release are not activated by this staging PR.

No existing scientific file is modified, removed, renamed or relicensed. No source repository transfer is required. The website remains a placeholder.
