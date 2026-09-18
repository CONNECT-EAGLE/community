# Community launch audit and administrator checklist

Audit: 2026-09-18. This is a maintainer handoff; newcomers should use [Start here](START_HERE.md).

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

- Preserve the `CONNECT-SBG` organization slug and `testrepo` repository name to keep existing links and history.
- Use the current public repository as a consolidated hub, with clear navigation to tools and registry. Additional repositories can be split later when their maintenance benefits justify it.
- Merge foundation PR #2 only after its six platform/version jobs passed, then publish this contributor update through a separate PR.
- Keep original scientific files and their licensing status unchanged. Do not enroll outside projects, fabricate contributors, or advertise mentors without their agreement.
- Keep dedicated security and conduct reporting contacts explicitly unconfigured until the owner names them.

## Remaining administrator actions

The GitHub connector can publish files, issues, labels, and PRs. It does not expose repository descriptions/visibility, organization profile settings, pins, Discussions categories, or Projects creation. The separate browser currently requires GitHub sign-in for these controls.

| Action | Exact proposed setting |
| --- | --- |
| Organization display name | `C.O.N.N.E.C.T. EAGLE` |
| Organization description | `Independent Earth-observation community for EAGLE VSWIR/TIR research, open tools, education, and collaboration.` |
| `testrepo` description | `Community hub, contribution opportunities, and tools for C.O.N.N.E.C.T. EAGLE; preserves CONNECT-SBG research history.` |
| `.github` description | `Organization profile and shared contribution guidelines, issue forms, and PR templates for C.O.N.N.E.C.T. EAGLE.` |
| `.github` visibility | Public, after reviewing its existing history for information that should stay private |
| Public pins | Pin `testrepo` as the community hub. Add dedicated tools/registry repositories only when they actually exist. |
| Discussions | Enable in the public hub: Announcements, Help (Q&A), Research Ideas, Projects & Collaboration, Education & Resources, Showcase |
| Project board | `CONNECT EAGLE Opportunities`; statuses Ideas, Ready, In Progress, Review, Done; add issues #3–14; filter by existing labels |
| Moderation | Name a private reporting route and a second consenting moderator before broad recruitment |
| Security | Enable private vulnerability reporting or publish a verified private security contact |

[GitHub documents](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) that the `.github` repository must be public for inherited defaults, with forms in `.github/ISSUE_TEMPLATE`. The [organization profile instructions](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile) specify `profile/README.md` and owner-controlled pins. Publishing those files alone does not change repository visibility or pin anything.

## Newcomer walkthrough

| Question | Direct answer / entry point |
| --- | --- |
| What is this? | Root README: independent EO research, tools, learning and collaboration community |
| What are VSWIR/TIR? | Plain-language README definitions and the official NASA EAGLE link |
| Where do I start? | START_HERE.md: five pathways with an immediate action |
| What can I contribute to? | OPPORTUNITIES.md: 12 real issues with acceptance criteria |
| Can beginners participate? | Five `good first issue` / `beginner` tasks |
| Can scientists participate without coding? | Two research reviews and referenced-comment contribution route |
| Can I register my own project? | Browser submission form; YAML and CLI alternatives; no transfer required |
| Where do I ask questions? | Public help thread #15 and task-specific threads |
| Which projects are active? | PROJECTS.md: infrastructure separated from accepted registry records; no invented memberships |

The repository experience can be checked independently of the organization homepage. The full organization launch remains incomplete until the visibility, description, and pin settings above are applied and the public homepage is checked again.
