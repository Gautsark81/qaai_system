from __future__ import annotations

"""
CLI entrypoint to run basic system health checks.

Usage:
    python -m apps.healthcheck
"""

import json
from infra.health.healthcheck import get_health_report


def main() -> None:
    report = get_health_report()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
