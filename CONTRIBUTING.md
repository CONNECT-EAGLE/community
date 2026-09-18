# Contributing to C.O.N.N.E.C.T. EAGLE

[Start here](START_HERE.md) · [Find work](OPPORTUNITIES.md) · [Ask a question](COMMUNITY.md)

Code, documentation, scientific review, tutorials, dataset validation, examples, figures, testing, research ideas, and issue triage all count. Keep contributions small enough for another person to understand and review.

## Find and claim a task

1. Choose an open issue from [Opportunities](OPPORTUNITIES.md). Check its assignee, comments, and linked PRs.
2. Comment with your plan and approximate availability. A maintainer assigns the issue after confirming scope; outside contributors may need to comment before GitHub can assign them. Do not assume a label means a task is unclaimed.
3. Ask scope questions in that issue. For a small, unclaimed documentation task you may open a draft PR while waiting. Coordinate larger changes before investing substantial work.
4. If you cannot continue, say so and release the claim. After 14 days without activity, a maintainer may ask whether the task should return to Ready. This is a coordination policy, not a deadline imposed on volunteers.

## Submit your contribution

- **In your browser:** open the relevant Markdown file, select the edit button, and let GitHub create a fork and branch. Propose the change as a PR. You can also post suggested wording or scientific review in the issue; a maintainer can help turn it into a credited change.
- **With Git:** fork this repository, branch from its current `main`, and use `docs/short-topic`, `feat/short-topic`, `fix/short-topic`, or `research/short-topic`. Commit focused changes and open a PR into `main`.
- Link the issue using `Closes #NUMBER` only when the acceptance criteria are satisfied. Use a draft PR for work in progress.
- Fill the PR template: what changed, why, checks performed, and scientific/data implications. Respond to review in the PR so others can follow the reasoning.

## Check the work that changed

| Contribution | Expected check |
| --- | --- |
| Documentation or terminology | Preview Markdown, follow links, define acronyms, cite factual claims |
| Scientific review or research idea | State assumptions, evidence, uncertainty, and what would change the conclusion; code is optional |
| Dataset or notebook | Document source, license, units, coordinates, missing data and versions; use small redistributable or explicitly synthetic examples |
| CLI or registry code | Run the relevant tests; follow the [CLI development guide](connect-eagle-foundation/connect-eagle-cli/README.md#development) |
| Project registration | Validate the record and regenerate the directory as described in [Submit a project](SUBMIT_PROJECT.md) |

Do not upload credentials, unpublished private data, large downloaded scenes, or material you lack permission to redistribute. Refer to dataset landing pages or DOIs. Preserve attribution; registration does not grant a license to the underlying project.

## Review and acceptance

Maintainers check scope, clarity, relevant tests, provenance, and the issue's acceptance criteria. Scientific claims require a reviewer who can assess the method; passing software tests does not validate science. Merge follows review and passing applicable checks. If the team lacks the needed expertise, the work stays provisional and the gap is recorded.

This is a small volunteer community with no guaranteed response time. After seven days without a response, one polite follow-up in the same thread is appropriate. Do not send repeated personal messages. Use [Community](COMMUNITY.md) for general questions.

## Credit and conduct

Credit code and non-code work through linked PRs, review acknowledgments, and project-specific citations. Ask before listing another person. See [Credits](CONTRIBUTORS.md) and [Code of conduct](CODE_OF_CONDUCT.md). Contributing here does not create NASA affiliation or automatically confer paper authorship.
