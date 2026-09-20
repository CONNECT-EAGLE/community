# Reviewing community contributions

[Start here](START_HERE.md) · [Contribution guide](CONTRIBUTING.md) · [Submission guide](SUBMIT_PROJECT.md)

Fares Alhezaimi ([falhezaimi](https://github.com/falhezaimi)) is the current setup contact. Review requests and decisions stay in their issue or PR. Add other reviewers only after they agree to the role.

## Triage a first contribution

1. Check for an existing issue or PR and acknowledge the contributor's proposed scope.
2. Apply the existing topic and difficulty labels from [Labels](LABELS.md). Use `good first issue` only for work with clear instructions and a bounded outcome.
3. Confirm who is working on the task. Help a new contributor reduce a large proposal to a reviewable first change.
4. Review against the acceptance criteria. Credit documentation, scientific review, and testing as well as code.

## Review a project request

Browser forms and CLI `--issue` requests enter the same queue. Neither constitutes automatic registration.

1. Verify the repository exists and the submitter maintains it or has the maintainer's agreement. Request clarification in the issue when evidence is missing. Do not treat a checked box or passing CI as proof of authority.
2. Check the description, VSWIR/TIR/supporting-EO relevance, lifecycle, maintainer, collaboration preferences, and existing license/citation against the source. Do not invent metadata or imply endorsement.
3. Check for an existing record or another submission. Update the existing slug when appropriate; do not create duplicate entries for one repository.
4. On a branch, add the reviewed snapshot to `connect-eagle-foundation/project-registry/projects/<slug>.yml` and run:

   ```sh
   python -m pip install -r connect-eagle-foundation/project-registry/requirements.txt
   python connect-eagle-foundation/project-registry/validate_registry.py connect-eagle-foundation/project-registry/projects
   python connect-eagle-foundation/scripts/build_directory.py
   python connect-eagle-foundation/scripts/build_directory.py --check
   ```

5. Open a PR with the YAML and regenerated `PROJECTS.md`; link the submission issue. Require passing applicable checks and review the human evidence above before merging.
6. After merge, close the request with a link to the accepted record and directory. Explain a rejection respectfully and identify what would make a revised submission eligible. Record archival/status changes through another PR.

## Before broad recruitment

Complete the concrete settings in [Community setup](COMMUNITY_SETUP.md), particularly the public organization profile and private reporting route. The public help thread supports ordinary onboarding; it is not a private reporting channel. A second moderator requires a real person's agreement.
