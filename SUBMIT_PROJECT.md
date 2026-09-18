# Connect your project

[Start here](START_HERE.md) · [Project directory](PROJECTS.md) · [Registry schema](connect-eagle-foundation/connect-eagle-cli/docs/metadata-v1.md)

Keep ownership, issues, releases, and scientific decisions in your own repository. Registration adds a discoverable, reviewed description here. It does not endorse results or change licensing.

## Simplest route: use your browser

1. Open a [project submission](https://github.com/CONNECT-SBG/testrepo/issues/new?template=project-submission.yml).
2. Provide the repository, a short description, VSWIR/TIR/supporting-EO relevance, project type, current status, maintainer, and whether you want collaborators.
3. Confirm you maintain the project or have the maintainer's agreement. A reviewer verifies the public repository and ownership evidence, asks for missing details, and helps prepare a registry PR.
4. After the record is reviewed and merged, it appears in [Projects](PROJECTS.md).

## CLI route: prepare your record

Install from the published source (Python 3.11+, Git; pipx must already be installed):

```sh
pipx install 'git+https://github.com/CONNECT-SBG/testrepo.git@main#subdirectory=connect-eagle-foundation/connect-eagle-cli'
```

Inside your own Git project:

```sh
connect-eagle init
connect-eagle doctor
connect-eagle submit
```

The last command prepares a local packet; it does **not** register your project online. Open the browser submission above or contribute the reviewed YAML through a PR. The current registry lives in a subdirectory of this hub, so **do not run `submit --registry CONNECT-SBG/testrepo --push`**: v0.1 expects a dedicated registry with `projects/` at the root. The automated online route will be advertised after that destination exists and a live end-to-end submission is verified.

## Contribute a registry PR

Add `connect-eagle-foundation/project-registry/projects/<project-slug>.yml`, using the [schema guide](connect-eagle-foundation/connect-eagle-cli/docs/metadata-v1.md). Include a real maintainer and source repository. Do not add a project on someone else's behalf without their agreement.

From the hub root:

```sh
python -m pip install -r connect-eagle-foundation/project-registry/requirements.txt
python connect-eagle-foundation/project-registry/validate_registry.py connect-eagle-foundation/project-registry/projects
python connect-eagle-foundation/scripts/build_directory.py
```

Commit the YAML and regenerated `PROJECTS.md`. CI checks that the directory matches the registry. The reviewer checks maintainer authority, links, scientific scope, and collaboration status; schema validation alone cannot verify those facts. Missing license/citation is a review prompt, not permission to invent them.
