# Project submission example

[Submission guide](../SUBMIT_PROJECT.md) · [Metadata schema](../connect-eagle-foundation/connect-eagle-cli/docs/metadata-v1.md)

This entire example is fictional and is **not registered**. `example.org` and the maintainer name are placeholders for teaching. Replace them with your own verified details before submitting a real project.

## Filled-in browser form

| Field | Illustrative answer |
| --- | --- |
| Repository and maintainer | `https://example.org/example/thermal-learning`; Example Project Owner; in a real request, explain your maintainer authority or agreement. |
| Project description | A tutorial using synthetic thermal observations to teach quality checks. Relevant to TIR; type: tutorial. |
| Status and collaboration | Planning. Welcomes documentation review; basic familiarity with Markdown is sufficient. |
| License and citation | Not yet available in this fictional example. A real owner must choose a license and provide existing citation information. |

## Matching schema-v1 record

```yaml
schema: 1
project:
  name: Example Thermal Learning
  slug: example-thermal-learning
  description: A tutorial using synthetic thermal observations to teach quality checks.
eagle:
  mission: [TIR]
  topics: [education, thermal-infrared]
project_type: tutorial
status: planning
collaboration:
  open: true
  looking_for: [documentation-review]
repository: https://example.org/example/thermal-learning
maintainers:
  - name: Example Project Owner
```

`eagle.mission` records relevance; `project_type` and `status` describe the project; `maintainers` names its real responsible people; `collaboration` expresses the owner's preferences. License and citation fields are omitted because none are asserted here. This is schema-valid, but it is not a reusable real-project record or evidence of maintainer consent.

## Validate without registering

With the CLI installed, save the YAML as `<temporary-folder>/projects/example-thermal-learning.yml`, outside the hub's production registry. Then run:

```sh
connect-eagle registry validate --directory <temporary-folder>/projects
```

Expected output: `Registry valid: 1 project(s).` Use the actual temporary path instead of the angle-bracket placeholder. Validation checks structure and duplicate identities; it cannot establish ownership, scientific validity, licensing rights, or repository availability. Do not submit this teaching record online.
