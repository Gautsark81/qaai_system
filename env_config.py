# env_config.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Union


# ============================================================
# BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# MODE
# ============================================================

MODE: str = os.getenv("MODE", "paper")
if MODE not in ("paper", "live"):
    MODE = "paper"


# ============================================================
# CORE SETTINGS
# ============================================================

TOP_K: int = int(os.getenv("TOP_K", "5"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
ACCOUNT_EQUITY: float = float(os.getenv("ACCOUNT_EQUITY", "1000000"))


# ============================================================
# DATABASE
# ============================================================

POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "qaai")
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "qaai")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "qaai")


# ============================================================
# PATHS (Monkeypatch Safe)
# ============================================================

LOG_DIR: Union[str, Path] = BASE_DIR / "logs"
AUDIT_DIR: Union[str, Path] = BASE_DIR / "audit"
SIGNALS_PATH: Union[str, Path] = BASE_DIR / "signals" / "latest_signals.csv"

TRADE_LOG_PATH: Union[str, Path] = BASE_DIR / "trades" / "trade_log.csv"
MARKET_LOG_PATH: Union[str, Path] = BASE_DIR / "market" / "price_data.csv"


def _to_path(p: Union[str, Path]) -> Path:
    return p if isinstance(p, Path) else Path(p)


# ============================================================
# DIRECTORY CREATION
# ============================================================

def ensure_dirs() -> None:
    """
    Must create directories dynamically based on current values.
    Fully monkeypatch-safe.
    """

    log_dir = _to_path(LOG_DIR)
    audit_dir = _to_path(AUDIT_DIR)
    signals_path = _to_path(SIGNALS_PATH)
    trade_log_path = _to_path(TRADE_LOG_PATH)
    market_log_path = _to_path(MARKET_LOG_PATH)

    # Create main log directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create audit directory
    audit_dir.mkdir(parents=True, exist_ok=True)

    # Create parents of file paths
    signals_path.parent.mkdir(parents=True, exist_ok=True)
    trade_log_path.parent.mkdir(parents=True, exist_ok=True)
    market_log_path.parent.mkdir(parents=True, exist_ok=True)