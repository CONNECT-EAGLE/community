# Engineering handoff

The implemented v0.1 is published under `connect-eagle-foundation/` on `feat/connect-eagle-foundation` in `CONNECT-SBG/testrepo`: [PR #2](https://github.com/CONNECT-SBG/testrepo/pull/2). Installing the connector on the organization resolved the initial HTTP 403. Historical scientific files remain intact. Start with `VERIFICATION.md` for current evidence and `AUDIT_AND_MIGRATION.md` for migration decisions.

## Run now

```sh
cd connect-eagle-foundation/connect-eagle-cli
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check src tests
python -m build
```

Run `connect-eagle init` inside a disposable project, followed by `doctor`, `status` and `submit`. `submit` prepares local metadata; `--push` requires an actual registry repository with `projects/` on its default branch and GitHub CLI authentication.

## Next launch work

1. PR #2 is merged after all six platform/version checks passed. Use the public hub's [Start here](../START_HERE.md) and [community launch checklist](../COMMUNITY_SETUP.md) for the current contributor rollout. The earlier delivery archive records a pre-publication snapshot; use GitHub's default branch for current source and guidance.
2. Create six destination repositories under the chosen owner: `connect-eagle-cli`, `project-registry`, `templates`, `community`, `.github`, `website`. The current connector cannot create them; creation can be done in an authenticated GitHub session. Do not rename or archive legacy assets as part of this step.
3. From a clean clone with the feature branch checked out, use `git subtree split --prefix=connect-eagle-foundation/COMPONENT -b split/COMPONENT` for each directory. `org-profile` maps to `.github`. This creates new split history without changing the original repository's history. Push each split to a feature branch in its initialized destination and open a PR against the destination's bootstrap `main`.
4. Merge the reviewed registry foundation so `projects/README.md` exists on its default branch. Configure `CONNECT_EAGLE_REGISTRY=OWNER/project-registry` for contributor instructions.
5. Run live `submit --push` once with a registry maintainer and once with an external collaborator; confirm fork creation, review, CI, merge, catalog export and a subsequent update. The present GitHub API mutation tests are simulated, not live CLI authentication tests.
6. Assign real maintainers/moderators, a private reporting contact, registry ownership review, and branch protections. Publish `org-profile` as `.github` to activate defaults; enable Discussions and set the community display name.
7. Check package-name availability, create a release tag and publish a reviewed wheel to PyPI. Until then, install from source/feature branch. No package release has been published.

## v0.2 priorities

- Confirm metadata against the source repository and verify submitter authority while keeping manual review.
- Show actual registry acceptance/update status and reconcile local receipts against GitHub.
- Add optional profile/role prompts and clearer remote selection for forked repositories.
- Test with five outside contributors on Windows/macOS/Linux; measure time to first accepted registration.
- Automate reviewed schema distribution between the CLI and registry and pin workflow actions to reviewed commits.
- Consider GitHub Enterprise/non-GitHub submission backends only after the GitHub.com loop is proven.

The website remains a placeholder. No account system, database, reputation system, gamification, forum or cloud backend is included.
