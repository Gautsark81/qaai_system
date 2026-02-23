"""
QAAI SYSTEM — ENTRYPOINT

This file is intentionally minimal.
All runtime behavior is delegated to bootstrap.
"""

from __future__ import annotations

import sys
from typing import Optional


def main(argv: Optional[list[str]] = None) -> None:
    try:
        from bootstrap import bootstrap
        bootstrap()  # 🔒 ZERO-ARG ONLY
    except SystemExit:
        raise
    except Exception:
        print("BOOT_FATAL", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
