"""Write a GitHub job summary, annotations and outputs from a QAVF JSON report.

Standard library only: it runs before, and independently of, the QAVF install.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ORDER = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
ICONS = {"passed": "✅", "failed": "❌", "incomplete": "⚠️", "error": "💥"}


def _escape(text: str, *, prop: bool = False) -> str:
    """Escape workflow-command data, or a property value when ``prop`` is set."""
    text = (text or "").replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return text.replace(":", "%3A").replace(",", "%2C") if prop else text


def _cell(text: object) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def _write(name: str, text: str) -> None:
    target = os.environ.get(name)
    if target:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(text)


def main() -> int:
    path = Path(os.environ.get("QAVF_REPORT") or "qavf-report/qa_report.json")
    limit = int(os.environ.get("QAVF_ANNOTATIONS") or 20)
    if not path.is_file():
        _write("GITHUB_OUTPUT", "verdict=error\n")
        _write(
            "GITHUB_STEP_SUMMARY",
            f"## {ICONS['error']} QAVF did not produce a report\n\n"
            "The run failed before writing results. See the step log for the error.\n",
        )
        return 0
    report = json.loads(path.read_text(encoding="utf-8"))
    acceptance, summary = report["acceptance"], report["summary"]
    verdict = acceptance["verdict"]
    results = report.get("results", [])
    problems = sorted(
        (r for r in results if r.get("status") in {"FAIL", "ERROR"}),
        key=lambda r: (r["status"] != "ERROR", ORDER.get(r.get("severity"), 9)),
    )
    for result in problems[:limit]:
        severe = result["status"] == "ERROR" or ORDER.get(result["severity"], 9) <= 1
        level = "error" if severe else "warning"
        label = result.get("check") or result.get("name") or result["rule_id"]
        title = _escape(f"{result['rule_id']} {result['status']}: {label}"[:200], prop=True)
        print(f"::{level} title={title}::{_escape(result.get('message', ''))}")

    lines = [
        f"## {ICONS.get(verdict, '')} QAVF: {verdict}",
        "",
        f"Fail on **{acceptance['fail_on']}**"
        + (" · incomplete runs fail" if acceptance.get("fail_on_incomplete") else ""),
        "",
        "| Results | Passed | Failed | Not assessed | Skipped |",
        "|---|---|---|---|---|",
        f"| {summary['total']} | {summary['passed']} | {summary['failed']} "
        f"| {summary['errored']} | {summary['skipped']} |",
    ]
    if problems:
        lines += [
            "",
            "| Rule | Status | Severity | Check | Message |",
            "|---|---|---|---|---|",
        ]
        for result in problems[:50]:
            lines.append(
                f"| {result['rule_id']} | {result['status']} | {result.get('severity', '')} "
                f"| {_cell(result.get('check') or result.get('name'))} "
                f"| {_cell(result.get('message'))[:300]} |"
            )
        if len(problems) > 50:
            lines.append(f"\n{len(problems) - 50} more in the report artifact.")
    _write("GITHUB_STEP_SUMMARY", "\n".join(lines) + "\n")
    _write("GITHUB_OUTPUT", f"verdict={verdict}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
