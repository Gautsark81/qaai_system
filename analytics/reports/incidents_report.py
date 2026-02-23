from __future__ import annotations

"""
Incident report generator.

Reads structured JSON log lines (INFO/WARNING/ERROR) from a log file
(or multiple files), filters for "error-like" events, and aggregates
into a simple summary.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _iter_log_lines(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if isinstance(rec, dict):
                    yield rec
            except json.JSONDecodeError:
                continue


def summarize_incidents(
    log_paths: List[str],
) -> Dict[str, Any]:
    total_errors = 0
    by_event: Dict[str, int] = {}
    by_component: Dict[str, int] = {}

    for p_str in log_paths:
        path = Path(p_str)
        for rec in _iter_log_lines(path):
            level = str(rec.get("level", "")).upper()
            event = str(rec.get("event", "")).upper()
            component = str(
                rec.get("component", rec.get("logger", "unknown"))
            ).lower()

            if level == "ERROR" or event in {
                "PANIC_SHUTDOWN",
                "RISK_KILL_SWITCH",
                "BROKER_ERROR",
            }:
                total_errors += 1
                by_event[event] = by_event.get(event, 0) + 1
                by_component[component] = by_component.get(component, 0) + 1

    return {
        "total_incidents": total_errors,
        "by_event": by_event,
        "by_component": by_component,
    }


def main() -> None:
    """
    CLI:

        python -m analytics.reports.incidents_report path/to/log1.jsonl [log2.jsonl ...]
    """
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m analytics.reports.incidents_report "
            "<log1.jsonl> [<log2.jsonl> ...]"
        )
        raise SystemExit(1)

    summary = summarize_incidents(sys.argv[1:])
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
