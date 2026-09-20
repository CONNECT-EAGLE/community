# C.O.N.N.E.C.T. EAGLE project registry

A Git-backed catalog of participating projects. Each record follows schema v1, and projects keep their existing repositories and ownership.

## Validate and export

```sh
python -m pip install -r requirements.txt
python validate_registry.py projects
python validate_registry.py projects --output catalog.json
```

The validator checks every record, filename/slug alignment and duplicate repository URLs. It rejects unsupported versions, duplicate YAML keys, aliases and symlinks. Errors identify the offending record and field. Export only succeeds after the entire collection validates.

No fictional memberships are included. The catalog is intentionally empty until project owners submit records.

## Review a registration

1. Confirm the submitting account has authority to represent the linked project; inspect the source repository and its maintainers. CI alone cannot establish ownership.
2. Check that project name, description, mission area, collaboration preferences and license match the public source.
3. Run the validation command above, regenerate the root `PROJECTS.md`, and confirm `community-directory` and `eagle-foundation` pass in the hub and resolve any slug/URL conflict.
4. Merge through review. Corrections use the same filename and another PR; archival changes `status`, preserving history.

Maintain the vendored schema and validation modules through reviewed updates from the CLI. Organization admins should require this validation check and review before merge. Restrict changes to `validation/`, `requirements.txt`, the validator and workflows to maintainers through branch protection/CODEOWNERS after a real maintainer team is configured.

The standalone workflow validates PR data with validation code checked out from the base commit. It never uses `pull_request_target`, privileged tokens, or secrets. Push validation permits reviewed validator changes to take effect.
