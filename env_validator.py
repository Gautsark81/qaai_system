# File: env_validator.py

"""
Institutional Environment Validator

Guarantees:
- .env loaded exactly once
- Strict presence validation
- MODE semantic validation
- Mode-specific enforcement
- Cross-field invariants enforced
- Capital envelope bounded
- Token required only for live
- Config frozen after validation
"""

import os
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv


# ─────────────────────────────────────────────
# Load .env once
# ─────────────────────────────────────────────
load_dotenv()


ModeType = Literal["paper", "shadow", "live"]
_ALLOWED_MODES = {"paper", "shadow", "live"}


# ─────────────────────────────────────────────
# Immutable Config Object
# ─────────────────────────────────────────────
@dataclass(frozen=True)
class Config:
    mode: ModeType
    execution_enabled: bool
    max_capital_pct: float
    max_daily_drawdown_pct: float
    global_kill_switch: bool
    broker_allowed: bool
    require_token_refresh_daily: bool
    live_confirmation_phrase: str

    dhan_client_id: str
    dhan_access_token: str

    redis_url: str
    mlflow_uri: str

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str


def _require(var: str) -> str:
    value = os.getenv(var)
    if not value:
        raise RuntimeError(f"Missing required env var: {var}")
    return value


def validate_and_freeze() -> Config:

    mode = _require("MODE").lower()
    if mode not in _ALLOWED_MODES:
        raise RuntimeError(f"Invalid MODE: {mode}")

    execution_enabled = os.getenv("EXECUTION_ENABLED", "false").lower() == "true"
    broker_allowed = os.getenv("BROKER_ALLOWED", "false").lower() == "true"
    global_kill_switch = os.getenv("GLOBAL_KILL_SWITCH", "false").lower() == "true"
    require_token_refresh_daily = os.getenv(
        "REQUIRE_TOKEN_REFRESH_DAILY", "true"
    ).lower() == "true"

    max_capital_pct = float(_require("MAX_CAPITAL_PCT"))
    max_daily_drawdown_pct = float(_require("MAX_DAILY_DRAWDOWN_PCT"))

    live_confirmation_phrase = os.getenv("LIVE_CONFIRMATION_PHRASE", "")

    dhan_client_id = os.getenv("DHAN_CLIENT_ID", "")
    dhan_access_token = os.getenv("DHAN_ACCESS_TOKEN", "")

    redis_url = _require("REDIS_URL")
    mlflow_uri = _require("MLFLOW_TRACKING_URI")

    postgres_host = _require("POSTGRES_HOST")
    postgres_port = int(_require("POSTGRES_PORT"))
    postgres_user = _require("POSTGRES_USER")
    postgres_password = _require("POSTGRES_PASSWORD")
    postgres_db = _require("POSTGRES_DB")

    # ─────────────────────────────────────────
    # Cross-field constraints
    # ─────────────────────────────────────────

    if not (0 <= max_capital_pct <= 100):
        raise RuntimeError("MAX_CAPITAL_PCT must be 0–100")

    if max_daily_drawdown_pct <= 0:
        raise RuntimeError("MAX_DAILY_DRAWDOWN_PCT must be > 0")

    if global_kill_switch:
        raise RuntimeError("GLOBAL_KILL_SWITCH is enabled — aborting startup.")

    # ─────────────────────────────────────────
    # Mode-specific rules
    # ─────────────────────────────────────────

    if mode == "paper":
        if execution_enabled:
            raise RuntimeError("Paper mode cannot execute trades.")
        if broker_allowed:
            raise RuntimeError("Paper mode must not allow broker.")

    if mode == "shadow":
        if execution_enabled:
            raise RuntimeError("Shadow mode must not execute.")
        if broker_allowed:
            raise RuntimeError("Shadow must not send live orders.")

    if mode == "live":

        if not execution_enabled:
            raise RuntimeError("Live mode requires EXECUTION_ENABLED=true")

        if not broker_allowed:
            raise RuntimeError("Live mode requires BROKER_ALLOWED=true")

        if max_capital_pct <= 0:
            raise RuntimeError("Live mode requires capital envelope > 0")

        if live_confirmation_phrase != "I_ACCEPT_LIVE_RISK":
            raise RuntimeError(
                "Live mode requires LIVE_CONFIRMATION_PHRASE=I_ACCEPT_LIVE_RISK"
            )

        if not dhan_client_id or not dhan_access_token:
            raise RuntimeError("Live mode requires DHAN credentials.")

    return Config(
        mode=mode,
        execution_enabled=execution_enabled,
        max_capital_pct=max_capital_pct,
        max_daily_drawdown_pct=max_daily_drawdown_pct,
        global_kill_switch=global_kill_switch,
        broker_allowed=broker_allowed,
        require_token_refresh_daily=require_token_refresh_daily,
        live_confirmation_phrase=live_confirmation_phrase,
        dhan_client_id=dhan_client_id,
        dhan_access_token=dhan_access_token,
        redis_url=redis_url,
        mlflow_uri=mlflow_uri,
        postgres_host=postgres_host,
        postgres_port=postgres_port,
        postgres_user=postgres_user,
        postgres_password=postgres_password,
        postgres_db=postgres_db,
    )


CONFIG = validate_and_freeze()