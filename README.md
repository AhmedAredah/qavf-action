# QAVF data QA action

[![Test action](https://github.com/AhmedAredah/qavf-action/actions/workflows/test.yml/badge.svg)](https://github.com/AhmedAredah/qavf-action/actions/workflows/test.yml)

Run [QAVF](https://github.com/AhmedAredah/qavf) data quality checks in GitHub Actions.
The action installs QAVF with [uv](https://docs.astral.sh/uv/), runs your configuration,
and fails the step unless the QA verdict is `passed`. It also:

- writes a **job summary** with the verdict, counts and every failed or unassessed check;
- adds **annotations** for failed checks to the run and pull request;
- uploads the **HTML and JSON reports** as a workflow artifact;
- exposes the verdict and exit code as **outputs** for later steps.

Works on Linux, macOS and Windows runners.

## Usage

```yaml
on: [push, pull_request]
jobs:
  data-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: AhmedAredah/qavf-action@v1
        with:
          config: qavf.yaml
```

Pin a QAVF version and change the failure threshold:

```yaml
      - uses: AhmedAredah/qavf-action@v1
        with:
          config: qa/qavf.yaml
          version: 0.4.0
          extras: all
          fail-on: WARNING
```

Report without failing the job, then act on the outputs:

```yaml
      - id: qa
        uses: AhmedAredah/qavf-action@v1
        with:
          config: qavf.yaml
          fail: "false"
      - if: steps.qa.outputs.verdict != 'passed'
        run: echo "QA verdict was ${{ steps.qa.outputs.verdict }}"
```

## Inputs

| Input | Default | Description |
|---|---|---|
| `config` | (required) | QAVF configuration file (YAML or JSON) |
| `version` | latest | QAVF version to install |
| `extras` | `stats` | Extras to install: `stats`, `pandas`, `all` |
| `package` | | Full package specification, overriding `version` (for example a Git URL) |
| `python-version` | `3.12` | Python used to run QAVF |
| `fail-on` | from config | Lowest failing severity: `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `report-dir` | `qavf-report` | Directory for `qa_report.json` and `qa_report.html` |
| `upload-report` | `true` | Upload the report directory as an artifact |
| `artifact-name` | `qavf-report` | Artifact name (make it unique per job in a matrix) |
| `annotations` | `20` | Maximum failed checks shown as annotations (`0` disables) |
| `fail` | `true` | Fail the step when the verdict is not `passed` |

## Outputs

| Output | Description |
|---|---|
| `verdict` | `passed`, `failed`, `incomplete`, or `error` when no report was produced |
| `exit-code` | `0` passed, `1` QA failed or incomplete, `2` usage or resource error |
| `report-json` | Path of the JSON report |
| `report-html` | Path of the HTML report |

A container image is also available for pinned environments:
`ghcr.io/ahmedaredah/qavf`. See the [QAVF documentation](https://github.com/AhmedAredah/qavf#readme)
for configuration.

## License

[MIT](LICENSE)
