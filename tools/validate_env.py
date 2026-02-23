# Path: tools/validate_env.py
"""Validate environment variables required for Dhan v2 feed and trading.

- Prints derived 'selected' values based on TRADING_ENV
- Heuristics for truncated/expired-looking tokens
"""
import logging
import json
import os
from dotenv import load_dotenv

load_dotenv()

from src.config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("tools.validate_env")

def looks_truncated_token(token: str) -> bool:
    """Heuristic: JWT usually has two dots and is fairly long (>100)."""
    if not token:
        return True
    if token.count(".") < 2:
        return True
    if len(token) < 80:
        return True
    return False

def mask_token(token: str) -> str:
    if not token:
        return "<missing>"
    if len(token) <= 20:
        return token[:4] + "..." + token[-4:]
    return token[:6] + "..." + token[-6:]

def main():
    errors = []
    warnings = []

    # Client ID
    client_id = config.DHAN_CLIENT_ID
    if not client_id:
        errors.append("DHAN_CLIENT_ID missing")

    # Selected token based on TRADING_ENV and overrides
    selected_token = config.selected_token
    if not selected_token:
        errors.append("No Dhan access token selected (DHAN_ACCESS_TOKEN or DHAN_ACCESS_TOKEN_{LIVE|PAPER})")
    else:
        if looks_truncated_token(selected_token):
            warnings.append("Selected DHAN access token appears truncated or unusually short. Ensure you pasted the FULL JWT into .env.")
    # Selected WS & REST
    selected_ws = config.selected_ws_url
    selected_rest = config.selected_rest_base

    # instruments
    try:
        instruments = config.DHAN_V2_INSTRUMENTS
        if not isinstance(instruments, list):
            errors.append("DHAN_V2_INSTRUMENTS is not a valid JSON list")
    except Exception:
        errors.append("DHAN_V2_INSTRUMENTS invalid JSON")

    # print results
    logger.info("TRADING_ENV = %s", config.TRADING_ENV)
    logger.info("DHAN_CLIENT_ID = %s", client_id or "<missing>")
    logger.info("Selected token = %s", mask_token(selected_token))
    logger.info("Selected WS URL = %s", selected_ws or "<none>")
    logger.info("Selected REST base = %s", selected_rest or "<none>")
    logger.info("Instruments (count) = %d", len(instruments or []))

    if warnings:
        logger.warning("Warnings:")
        for w in warnings:
            logger.warning(" - %s", w)

    if errors:
        logger.error("Errors:")
        for e in errors:
            logger.error(" - %s", e)
        return 1

    logger.info("Environment validation OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
