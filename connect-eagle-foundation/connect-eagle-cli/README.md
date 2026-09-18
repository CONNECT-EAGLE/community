# connect-eagle v0.1

Connect an existing Git project to C.O.N.N.E.C.T. EAGLE without transferring its repository.

Requires Python 3.11+, Git, and (only for online GitHub registration) [GitHub CLI](https://cli.github.com/).

## Install

From this directory:

```sh
pipx install .
```

Install the published foundation feature branch directly:

```sh
pipx install 'git+https://github.com/CONNECT-SBG/testrepo.git@feat/connect-eagle-foundation#subdirectory=connect-eagle-foundation/connect-eagle-cli'
```

The package is **not yet published to PyPI**. `pipx install connect-eagle` is the intended release experience, not a currently promised package name. Check name availability before publishing.

## Contributor quickstart

Run inside your existing Git project:

```sh
connect-eagle init
connect-eagle doctor
connect-eagle status
connect-eagle submit
```

`init` asks up to five short questions. It detects Python, JavaScript or R package metadata, README, license, citation and remotes. It writes only `.connect-eagle.yml`, never replaces one, and works from a subdirectory or linked Git worktree. Origin is the default remote; select `--remote upstream` to register another. Non-GitHub projects work too.

For unattended use:

```sh
connect-eagle init --non-interactive --mission both --type software --description "Tools for thermal and spectral observations" --topics remote-sensing,earth-observation --collaborators
```

`--mission` accepts `VSWIR`, `TIR`, `both`, or `supporting-technology`. Missing scientific details are never guessed non-interactively. Edit the generated YAML to add roles, links, contributors and publications.

## Commands

| Command | Behavior |
| --- | --- |
| `init` | Create metadata from repository facts and a few answers |
| `status` | Show readiness and local submission receipt; never infer remote acceptance |
| `doctor` | Validate metadata and Git state; recommendations are warnings |
| `doctor --strict` | Exit nonzero on warnings as well as errors |
| `doctor --online` | Also check remotes and GitHub authentication |
| `submit` | Save a registration packet under the Git directory; no network writes |
| `submit --dry-run` | Validate and preview without writing anything |
| `submit --registry OWNER/project-registry --push` | Create a registry feature branch and PR; fork when necessary |
| `registry validate --directory projects` | Validate all registry entries and detect collisions |
| `registry export --directory projects --output catalog.json` | Export deterministic JSON; refuses to overwrite output |

Use `--path DIRECTORY` with the four contributor commands. The registry can also be set through `CONNECT_EAGLE_REGISTRY`.

Before online submission, publish the registry foundation so its default branch has `projects/README.md`, then run `gh auth login --hostname github.com`. An existing PR is reused. A changed record for another repository cannot overwrite an occupied slug. API failures stop cleanly; a created fork or branch may remain and can be inspected/reused on retry. A fork still being provisioned by GitHub may require a later retry.

The contributor's working tree, remotes, branch and commit history are not modified by submission. Metadata is submitted as a snapshot; commit it to your project separately when ready. Registry maintainers verify ownership manually before merge. Draft entries never become automatic endorsements.

Warnings for missing README/license/citation do not prevent registration. No license is invented. Unsupported schema versions, duplicate YAML keys, aliases, invalid slugs, credential-bearing links and ambiguous metadata files are errors.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check src tests
python -m build
```

See `docs/metadata-v1.md` and `docs/architecture.md`. The CI matrix runs on Windows, macOS and Linux with Python 3.11 and 3.12; see [PR #2 checks](https://github.com/CONNECT-SBG/testrepo/pull/2/checks) for current results. Network mutation is contract-tested using a fake GitHub API; see the foundation verification report for the exact live checks performed.
