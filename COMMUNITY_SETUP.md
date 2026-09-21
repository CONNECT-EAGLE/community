# Community launch audit and administrator checklist

Latest audit: 2026-09-21. Initial setup: 2026-09-18. This is a maintainer handoff; newcomers should use [Start here](START_HERE.md).

## What a stranger encountered

| Surface | Observed before this update | Response |
| --- | --- | --- |
| Organization profile | Display name CONNECT-EAGLE; no public profile README | Write a concise profile with science context and navigation |
| Public repositories | One: `testrepo`, no description, no root README on default branch | Merge verified foundation and publish an understandable community hub |
| Additional accessible repository | Private `.github`; generic README, one old bug template and an empty feature template | Prepare recognized default-template paths and a profile; preserve old files |
| Pins | Public page showed Popular repositories, not Pinned | Pin the public hub after administrator sign-in |
| Issues | No open contribution issues | Create 12 scoped opportunities plus one help thread |
| Discussions | Disabled on both repositories | Use the help thread now; prepare six categories |
| Projects | No public organization Projects | Publish an opportunities index; prepare a simple native board |
| Lifecycle and registry | Historical files mixed with new foundation; no accepted registry entries | Separate history, infrastructure, and generated project directory |

The connected installation exposed two repositories; the public page exposed one. No other private assets, private boards, or hidden organization settings are claimed to have been audited. No duplicate active project repositories were found in the accessible inventory. Historical notebooks were not scientifically revalidated.

## Publishing decisions

- The organization is now `CONNECT-EAGLE`. Use that slug in current links and commands. The hub was renamed from `testrepo` to `community` on September 21; its original research history and issues are preserved.
- Use the current public repository as a consolidated hub, with clear navigation to tools and registry. Additional repositories can be split later when their maintenance benefits justify it.
- Merge foundation PR #2 only after its six platform/version jobs passed, then publish this contributor update through a separate PR.
- Keep original scientific files and their licensing status unchanged. Do not enroll outside projects, fabricate contributors, or advertise mentors without their agreement.
- Keep dedicated security and conduct reporting contacts explicitly unconfigured until the owner names them.

## September 20 contribution-path update

- Updated current links, forms, installation commands, and issue bodies to `CONNECT-EAGLE`. Historical scientific files remain unchanged.
- Added CLI v0.1.1 `submit --registry CONNECT-EAGLE/community --issue` to request review in the existing hub, with duplicate protection and a no-write dry run. Dedicated-registry PR submission remains separate.
- Added a schema-valid fictional submission example outside the production registry and a maintainer review checklist.
- Existing contribution issues remain the task queue; no duplicate opportunity issues are needed.
- Contributor update PR #17 merged after all 13 CI runs passed. The settings work below was completed after administrator sign-in.
- Validation: 65 CLI tests, lint, template validation, registry validation, directory checks, and package build. GitHub Actions must pass before merging this update. A real external contributor has not yet exercised authenticated CLI issue submission.

## September 21 live settings

- Set the organization display name to **C.O.N.N.E.C.T. EAGLE**, added its independent-community description, and linked Start here.
- Added descriptions to both repositories and pinned the public hub on the organization homepage.
- Enabled hub and organization [Discussions](https://github.com/orgs/CONNECT-EAGLE/discussions): Announcements, Help (Q&A), Research Ideas, Projects & Collaboration, Education & Resources, and Showcase. The default Polls category remains available.
- Created the public [CONNECT EAGLE Opportunities board](https://github.com/orgs/CONNECT-EAGLE/projects/2/views/1), with 11 open issues (#3–13) in Ready and statuses Ideas, Ready, In Progress, Review, and Done. New issues require adding to the board; automatic import is not configured.
- Enabled private vulnerability reporting on the hub. See [Security](SECURITY.md).
- Completed the submission example (#14); it is no longer an open opportunity.

## Remaining owner decisions and validation

- **The `.github` repository remains private.** Its prepared profile and inherited defaults are not publicly active. Automatic approval review blocked changing visibility because publication exposes files, commit history, activity, and any Actions logs. Obtain explicit owner approval for that disclosure before continuing. Current contribution forms and guides are already available in the public hub.
- Designate a private conduct-reporting route and a second consenting moderator before broad recruitment. The security reporting route is not a substitute for conduct reporting.
- Have a real external contributor exercise authenticated CLI issue submission. Automated tests and CI passed, but that live external-user walkthrough has not been performed.

[GitHub documents](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) that the `.github` repository must be public for inherited defaults, with forms in `.github/ISSUE_TEMPLATE`. The [organization profile instructions](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile) specify `profile/README.md` and owner-controlled pins. Publishing those files alone does not change repository visibility or pin anything.

## Newcomer walkthrough

| Question | Direct answer / entry point |
| --- | --- |
| What is this? | Root README: independent EO research, tools, learning and collaboration community |
| What are VSWIR/TIR? | Plain-language README definitions and the official NASA EAGLE link |
| Where do I start? | START_HERE.md: five pathways with an immediate action |
| What can I contribute to? | OPPORTUNITIES.md and public board: 11 open issues with acceptance criteria |
| Can beginners participate? | Five `good first issue` / `beginner` tasks |
| Can scientists participate without coding? | Two research reviews and referenced-comment contribution route |
| Can I register my own project? | Browser submission form; YAML and CLI alternatives; no transfer required |
| Where do I ask questions? | Help Discussions, existing thread #15, and task-specific threads |
| Which projects are active? | PROJECTS.md: infrastructure separated from accepted registry records; no invented memberships |

The repository experience can be checked independently of the organization homepage. The public hub accepts contributions now. Organization-wide profile/default publication and the remaining owner decisions above are still outstanding.
