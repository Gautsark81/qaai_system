# qaai_system/strategies/registry.py
"""
Hybrid, dynamic, supercharged Strategy Registry for qaai_system.

- Resolves strategy_registry.yaml from multiple candidate locations (configs/, config/, project root).
- Loads aggregated metrics (data/metrics/strategy_performance.json).
- Exposes get_deps(), recommend_strategies_for_symbol(), promote/demote helpers.
- Keeps an audit table in a small SQLite DB under db/registry.db.
"""
from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import yaml
import numpy as np

# try to import your project's SQLiteClient pattern (may vary)
try:
    from infra.sqlite_client import SQLiteClient
except Exception:
    # fallback minimal SQLite wrapper
    import sqlite3
    class SQLiteClient:
        def __init__(self, path: Path):
            self.path = str(path)
            self.conn = sqlite3.connect(self.path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        def exec(self, sql: str, params: tuple = ()):
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return cur
        def fetch_all(self, sql: str, params: tuple = ()):
            cur = self.conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()

logger = logging.getLogger("strategies.registry")
logger.setLevel(logging.INFO)

# ---------------- Paths & candidates ----------------
PROJECT_ROOT = Path(".").resolve()

_CANDIDATE_REGISTRY_PATHS = [
    PROJECT_ROOT / "configs" / "strategy_registry.yaml",
    PROJECT_ROOT / "config" / "strategy_registry.yaml",
    PROJECT_ROOT / "strategy_registry.yaml",
]

REGISTRY_PATH = next((p for p in _CANDIDATE_REGISTRY_PATHS if p.exists()), _CANDIDATE_REGISTRY_PATHS[0])
METRICS_PATH = PROJECT_ROOT / "data" / "metrics" / "strategy_performance.json"

# ---------------- DB clients ----------------
DB = {
    "db_ohlcv": SQLiteClient(Path("db/ohlcv.db")),
    "db_ticks": SQLiteClient(Path("db/ticks.db")),
    "db_features": SQLiteClient(Path("db/features.db")),
    "db_preds": SQLiteClient(Path("data/ml_predictions.db")),
    "db_registry": SQLiteClient(Path("db/registry.db")),
}

# account equity from env_config if present
try:
    import env_config
    _ACCOUNT_EQUITY = float(getattr(env_config, "ACCOUNT_EQUITY", 100000.0))
except Exception:
    _ACCOUNT_EQUITY = 100000.0

# ---------------- cache & locks ----------------
_lock = threading.RLock()
_registry_cache: Optional[Dict[str, Any]] = None
_metrics_cache: Optional[List[Dict[str, Any]]] = None
_last_registry_load: Optional[datetime] = None
_last_metrics_load: Optional[datetime] = None

@dataclass
class StrategyVersion:
    strategy_id: str
    version: str
    status: str
    params: Dict[str, Any]
    capital_allocation: float
    allowed_segments: List[str]
    allowed_regimes: List[str]

# ---------------- helpers ----------------
def _ensure_registry_audit_table() -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS registry_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        action TEXT,
        strategy_id TEXT,
        version TEXT,
        actor TEXT,
        reason TEXT,
        payload TEXT
    )
    """
    DB["db_registry"].exec(sql)

# ---------------- load/save registry ----------------
def load_registry(force: bool = False) -> Dict[str, Any]:
    global _registry_cache, _last_registry_load
    with _lock:
        if _registry_cache is not None and not force:
            return _registry_cache

        if not REGISTRY_PATH.exists():
            logger.warning("Registry YAML not found at %s; returning empty registry", REGISTRY_PATH)
            _registry_cache = {"strategies": {}}
            _last_registry_load = datetime.utcnow()
            return _registry_cache

        with REGISTRY_PATH.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        logger.info("Using registry path", extra={"registry_path": str(REGISTRY_PATH)})

        strategies = {}
        for sid, cfg in raw.get("strategies", {}).items():
            versions = {}
            for ver, vcfg in (cfg.get("versions") or {}).items():
                versions[str(ver)] = {
                    "status": str(vcfg.get("status", "Backtest-Approved")),
                    "params": vcfg.get("params", {}) or {},
                    "capital_allocation": float(vcfg.get("capital_allocation", 0.0) or 0.0),
                    "allowed_segments": list(vcfg.get("allowed_segments", []) or []),
                    "allowed_regimes": list(vcfg.get("allowed_regimes", []) or []),
                }
            strategies[sid] = {
                "family": str(cfg.get("family", "generic")),
                "description": str(cfg.get("description", "") or ""),
                "versions": versions,
            }

        _registry_cache = {"strategies": strategies}
        _last_registry_load = datetime.utcnow()
        logger.info("Loaded strategy registry", extra={"path": str(REGISTRY_PATH), "n": len(strategies)})
        return _registry_cache

def save_registry(registry: Dict[str, Any]) -> None:
    with _lock:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {"strategies": registry.get("strategies", {})}
        with REGISTRY_PATH.open("w", encoding="utf-8") as f:
            yaml.safe_dump(payload, f, sort_keys=False)
        load_registry(force=True)

# ---------------- metrics loader ----------------
def load_metrics(force: bool = False) -> List[Dict[str, Any]]:
    global _metrics_cache, _last_metrics_load
    with _lock:
        if _metrics_cache is not None and not force:
            return _metrics_cache
        if not METRICS_PATH.exists():
            logger.warning("Metrics file not found at %s; returning empty metrics", METRICS_PATH)
            _metrics_cache = []
            _last_metrics_load = datetime.utcnow()
            return _metrics_cache
        with METRICS_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f) or []
        _metrics_cache = raw
        _last_metrics_load = datetime.utcnow()
        logger.info("Loaded strategy metrics", extra={"path": str(METRICS_PATH), "groups": len(raw)})
        return _metrics_cache

def auto_refresh() -> None:
    load_registry(force=True)
    load_metrics(force=True)
    _ensure_registry_audit_table()

# ---------------- dependency bag ----------------
def get_deps() -> Dict[str, Any]:
    return {
        "db_ohlcv": DB["db_ohlcv"],
        "db_ticks": DB["db_ticks"],
        "db_features": DB["db_features"],
        "db_preds": DB["db_preds"],
        "logger": logger,
        "rng": np.random.default_rng(),
        "account": {"equity": _ACCOUNT_EQUITY},
    }

# ---------------- registry helpers ----------------
def list_strategies() -> List[str]:
    reg = load_registry()
    return list(reg.get("strategies", {}).keys())

def get_strategy_versions(strategy_id: str) -> Dict[str, StrategyVersion]:
    reg = load_registry()
    s = reg.get("strategies", {}).get(strategy_id)
    if not s:
        return {}
    out: Dict[str, StrategyVersion] = {}
    for ver, vcfg in s.get("versions", {}).items():
        out[ver] = StrategyVersion(
            strategy_id=strategy_id,
            version=ver,
            status=vcfg.get("status", "Backtest-Approved"),
            params=vcfg.get("params", {}) or {},
            capital_allocation=float(vcfg.get("capital_allocation", 0.0) or 0.0),
            allowed_segments=list(vcfg.get("allowed_segments", []) or []),
            allowed_regimes=list(vcfg.get("allowed_regimes", []) or []),
        )
    return out

def get_strategy_config(strategy_id: str, version: str) -> Optional[StrategyVersion]:
    vs = get_strategy_versions(strategy_id)
    return vs.get(str(version))

# ---------------- metrics query ----------------
def get_metrics_for(strategy_id: str, version: str, run_mode: str = "paper") -> Optional[Dict[str, Any]]:
    metrics = load_metrics()
    for row in metrics:
        if row.get("strategy_id") == strategy_id and str(row.get("version")) == str(version) and row.get("run_mode") == run_mode:
            return row
    return None

# ---------------- meta-model / recommendation (simple heuristic fallback) ----------------
try:
    from analytics.meta_model import StrategyMetaModel, MetaModelFeatures
except Exception:
    StrategyMetaModel = None
    MetaModelFeatures = None

def _heuristic_score(perf: Dict[str, Any]) -> float:
    wr = float(perf.get("win_rate", 0.0))
    pf = float(perf.get("profit_factor", 0.0) or 0.0)
    net = float(perf.get("net_pnl", 0.0) or 0.0)
    return wr * (1.0 + min(pf, 5.0) / 5.0) + (0.000001 * net)

def recommend_strategies_for_symbol(symbol: str, candidate_limit: int = 5) -> List[Tuple[StrategyVersion, float]]:
    registry = load_registry()
    metrics = load_metrics()
    candidates: List[Tuple[StrategyVersion, float]] = []
    meta_model = StrategyMetaModel() if StrategyMetaModel is not None else None
    for sid, s in registry.get("strategies", {}).items():
        for ver, vcfg in s.get("versions", {}).items():
            status = vcfg.get("status")
            if status not in {"Paper-Approved", "Live-Approved", "Backtest-Approved"}:
                continue
            perf = get_metrics_for(sid, ver, "paper") or get_metrics_for(sid, ver, "backtest") or get_metrics_for(sid, ver, "live")
            if not perf:
                continue
            if meta_model is not None and MetaModelFeatures is not None:
                try:
                    feat = MetaModelFeatures(
                        strategy_id=sid,
                        version=str(ver),
                        symbol=symbol,
                        win_rate=float(perf.get("win_rate", 0.0)),
                        profit_factor=float(perf.get("profit_factor", 0.0)),
                        net_pnl=float(perf.get("net_pnl", 0.0)),
                        volatility_regime=None,
                        mcap_bucket=None,
                    )
                    score = float(meta_model.score(feat))
                except Exception:
                    logger.exception("Meta-model scoring failed; falling back to heuristic")
                    score = _heuristic_score(perf)
            else:
                score = _heuristic_score(perf)
            sv = StrategyVersion(
                strategy_id=sid,
                version=str(ver),
                status=status,
                params=vcfg.get("params", {}) or {},
                capital_allocation=float(vcfg.get("capital_allocation", 0.0) or 0.0),
                allowed_segments=list(vcfg.get("allowed_segments", []) or []),
                allowed_regimes=list(vcfg.get("allowed_regimes", []) or []),
            )
            candidates.append((sv, score))
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:candidate_limit]

# ---------------- promote / demote ----------------
def promote_strategy(strategy_id: str, version: str, actor: str = "system", reason: str = "", force: bool = False) -> bool:
    reg = load_registry()
    s = reg.get("strategies", {}).get(strategy_id)
    if not s:
        raise ValueError(f"Unknown strategy: {strategy_id}")
    vcfg = s.get("versions", {}).get(str(version))
    if not vcfg:
        raise ValueError(f"Unknown version {version} for strategy {strategy_id}")
    if not force:
        perf = get_metrics_for(strategy_id, str(version), "paper") or get_metrics_for(strategy_id, str(version), "backtest")
        if not perf:
            raise RuntimeError("No metrics available for gating promotion; use force=True to override")
        if perf.get("trades", 0) < 50 or perf.get("win_rate", 0.0) < 0.8 or perf.get("profit_factor", 0.0) < 1.2:
            raise RuntimeError("Promotion gating failed: insufficient metrics")
    old_status = vcfg.get("status", "Backtest-Approved")
    new_status = old_status
    if old_status == "Backtest-Approved":
        new_status = "Paper-Approved"
    elif old_status == "Paper-Approved":
        new_status = "Live-Approved"
    elif old_status == "Live-Approved":
        return True
    else:
        new_status = "Paper-Approved"
    s["versions"][str(version)]["status"] = new_status
    save_registry(reg)
    _ensure_registry_audit_table()
    payload = {"strategy_id": strategy_id, "version": str(version), "old_status": old_status, "new_status": new_status}
    DB["db_registry"].exec(
        "INSERT INTO registry_audit (ts, action, strategy_id, version, actor, reason, payload) VALUES (?,?,?,?,?,?,?)",
        (datetime.utcnow().isoformat(), "promote", strategy_id, str(version), actor, reason or "", json.dumps(payload)),
    )
    logger.info("Promoted strategy", extra={"strategy_id": strategy_id, "version": version, "old": old_status, "new": new_status})
    load_registry(force=True)
    return True

def demote_strategy(strategy_id: str, version: str, actor: str = "system", reason: str = "") -> bool:
    reg = load_registry()
    s = reg.get("strategies", {}).get(strategy_id)
    if not s:
        raise ValueError(f"Unknown strategy: {strategy_id}")
    vcfg = s.get("versions", {}).get(str(version))
    if not vcfg:
        raise ValueError(f"Unknown version {version} for strategy {strategy_id}")
    old_status = vcfg.get("status", "Backtest-Approved")
    new_status = old_status
    if old_status == "Live-Approved":
        new_status = "Paper-Approved"
    elif old_status == "Paper-Approved":
        new_status = "Backtest-Approved"
    else:
        return True
    s["versions"][str(version)]["status"] = new_status
    save_registry(reg)
    _ensure_registry_audit_table()
    payload = {"strategy_id": strategy_id, "version": str(version), "old_status": old_status, "new_status": new_status}
    DB["db_registry"].exec(
        "INSERT INTO registry_audit (ts, action, strategy_id, version, actor, reason, payload) VALUES (?,?,?,?,?,?,?)",
        (datetime.utcnow().isoformat(), "demote", strategy_id, str(version), actor, reason or "", json.dumps(payload)),
    )
    logger.info("Demoted strategy", extra={"strategy_id": strategy_id, "version": version, "old": old_status, "new": new_status})
    load_registry(force=True)
    return True

def get_registry_audit(limit: int = 100) -> List[Dict[str, Any]]:
    _ensure_registry_audit_table()
    rows = DB["db_registry"].fetch_all("SELECT ts, action, strategy_id, version, actor, reason, payload FROM registry_audit ORDER BY id DESC LIMIT ?", (limit,))
    result = []
    for r in rows:
        ts, action, sid, ver, actor, reason, payload = r
        try:
            payload_json = json.loads(payload)
        except Exception:
            payload_json = payload
        result.append({"ts": ts, "action": action, "strategy_id": sid, "version": ver, "actor": actor, "reason": reason, "payload": payload_json})
    return result
