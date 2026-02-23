"""
Root wrapper for live market service.

Usage:
    python Live_market.py
"""

import logging
import os

from dotenv import load_dotenv

# Load root .env before importing services
load_dotenv(override=True)

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("live.market.wrapper")


def main() -> None:
    from services import live_market

    safe_mode = os.getenv("SAFE_MODE", "true").lower()
    logger.info("Starting live market via root wrapper (SAFE_MODE=%s)", safe_mode)

    # Touch healthfile & start
    live_market.touch_healthfile()
    live_market.run()


if __name__ == "__main__":
    main()
