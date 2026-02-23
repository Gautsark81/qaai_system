# src/config.py
"""
Central config for QA-AI project (revised to prefer Dhan v2 endpoint)

- Exposes `config` SimpleNamespace for `from src.config import config`
- Automatically builds Dhan v2 websocket URL (version=2) from token+client id when possible
- If DHAN_WS_URL explicitly set and contains '/v1/' or '/v1', it will be ignored in favor of a constructed v2 URL.
"""
from __future__ import annotations
import os
import logging
from types import SimpleNamespace
from pathlib import Path
from dotenv import load_dotenv
import json

_log = logging.getLogger(__name__)

# Load .env if present
env_path = Path(os.getenv("ENV_PATH", ".")) / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))
else:
    load_dotenv()

def _get_env(k, default=None):
    v = os.getenv(k)
    return v if v is not None else default

TRADING_ENV = (_get_env("TRADING_ENV") or _get_env("MODE") or "paper").lower()
if TRADING_ENV not in ("live", "paper"):
    _log.warning("Unknown TRADING_ENV '%s', defaulting to 'paper'", TRADING_ENV)
    TRADING_ENV = "paper"

DHAN_CLIENT_ID = _get_env("DHAN_CLIENT_ID") or _get_env("DHAN_CLIENTID") or _get_env("CLIENT_ID")

# tokens
DHAN_ACCESS_TOKEN = _get_env("DHAN_ACCESS_TOKEN")
DHAN_ACCESS_TOKEN_LIVE = _get_env("DHAN_ACCESS_TOKEN_LIVE")
DHAN_ACCESS_TOKEN_PAPER = _get_env("DHAN_ACCESS_TOKEN_PAPER")

# ws overrides (may be v1 or full url); we'll prefer constructing v2
DHAN_WS_URL = _get_env("DHAN_WS_URL")
DHAN_WS_URL_LIVE = _get_env("DHAN_WS_URL_LIVE")
DHAN_WS_URL_PAPER = _get_env("DHAN_WS_URL_PAPER")

# rest
DHAN_REST_BASE = _get_env("DHAN_REST_BASE")
DHAN_REST_BASE_LIVE = _get_env("DHAN_REST_BASE_LIVE")
DHAN_REST_BASE_PAPER = _get_env("DHAN_REST_BASE_PAPER")

# instruments
_raw_instruments = _get_env("DHAN_V2_INSTRUMENTS", "[]")
try:
    DHAN_V2_INSTRUMENTS = json.loads(_raw_instruments)
    if not isinstance(DHAN_V2_INSTRUMENTS, list):
        raise ValueError("DHAN_V2_INSTRUMENTS not a list")
except Exception:
    DHAN_V2_INSTRUMENTS = []
    _log.warning("DHAN_V2_INSTRUMENTS invalid JSON; defaulting to []")

# tuning
def _int_env(name, default):
    v = _get_env(name)
    try:
        return int(v) if v is not None else default
    except Exception:
        return default

MAX_WS_CONNECTIONS = _int_env("MAX_WS_CONNECTIONS", 5)
MAX_INSTRUMENTS_PER_CONNECTION = _int_env("MAX_INSTRUMENTS_PER_CONNECTION", 5000)
SUBSCRIBE_BATCH_SIZE = _int_env("SUBSCRIBE_BATCH_SIZE", 100)
LOG_LEVEL = _get_env("LOG_LEVEL", "INFO")

def _select_token(env):
    if env == "live":
        return DHAN_ACCESS_TOKEN_LIVE or DHAN_ACCESS_TOKEN
    return DHAN_ACCESS_TOKEN_PAPER or DHAN_ACCESS_TOKEN

def _select_ws(env):
    if env == "live":
        return DHAN_WS_URL_LIVE or DHAN_WS_URL
    return DHAN_WS_URL_PAPER or DHAN_WS_URL

def _select_rest(env):
    if env == "live":
        return DHAN_REST_BASE_LIVE or DHAN_REST_BASE or "https://api.dhan.co"
    return DHAN_REST_BASE_PAPER or DHAN_REST_BASE or "https://api.dhan.co"

selected_token = _select_token(TRADING_ENV)
selected_ws_url = _select_ws(TRADING_ENV)
selected_rest_base = _select_rest(TRADING_ENV)
selected_client_id = DHAN_CLIENT_ID

def build_v2_ws_url(token: str, client_id: str, auth_type: int = 2, base: str = "wss://api-feed.dhan.co"):
    token_enc = token
    return f"{base}?version=2&token={token_enc}&clientId={client_id}&authType={auth_type}"

# If selected_ws_url explicitly contains '/v1' or '/v1/live' we ignore it and build v2 url (Dhan requires v2 URL).
if selected_ws_url:
    lower = selected_ws_url.lower()
    if ("v1" in lower and "api-feed.dhan.co" in lower) or "/v1/" in lower or lower.endswith("/v1") or "/v1/live" in lower:
        _log.warning("DHAN_WS_URL appears to reference v1 (%s) — will build v2 endpoint from token+client_id instead.", selected_ws_url)
        selected_ws_url = None

# Build v2 url if missing but we have token+client_id
if not selected_ws_url and selected_token and selected_client_id:
    try:
        selected_ws_url = build_v2_ws_url(selected_token, selected_client_id)
        _log.debug("Constructed v2 ws url from token + client id")
    except Exception:
        _log.exception("Failed building v2 ws url")

def _looks_truncated(tok: str) -> bool:
    if not tok:
        return True
    parts = tok.split(".")
    if len(parts) != 3:
        return True
    return len(parts[1]) < 40

if selected_token and _looks_truncated(selected_token):
    _log.warning("Selected DHAN access token appears truncated or non-JWT. Ensure .env contains the full JWT string (no quotes/newlines).")

# final config object
config = SimpleNamespace(
    TRADING_ENV=TRADING_ENV,
    DHAN_CLIENT_ID=DHAN_CLIENT_ID,
    selected_token=selected_token,
    selected_ws_url=selected_ws_url,
    selected_rest_base=selected_rest_base,
    selected_client_id=selected_client_id,
    DHAN_V2_INSTRUMENTS=DHAN_V2_INSTRUMENTS,
    MAX_WS_CONNECTIONS=MAX_WS_CONNECTIONS,
    MAX_INSTRUMENTS_PER_CONNECTION=MAX_INSTRUMENTS_PER_CONNECTION,
    SUBSCRIBE_BATCH_SIZE=SUBSCRIBE_BATCH_SIZE,
    LOG_LEVEL=LOG_LEVEL,
    build_v2_ws_url=build_v2_ws_url,
)

# module-level names for backward compat
__all__ = ["config", "selected_token", "selected_ws_url", "selected_rest_base", "selected_client_id"]

_log.info("TRADING_ENV=%s, DHAN_CLIENT_ID=%s", TRADING_ENV, selected_client_id)
_log.info("Selected WS URL = %s", selected_ws_url or "<will build from token+clientId>")
_log.info("Selected REST base = %s", selected_rest_base)
