from __future__ import annotations

"""
Basic healthcheck helpers for the QA AI trading system.

These checks are intentionally light-weight for Phase 8:
- They do NOT start the orchestrator.
- They just verify that key modules can be imported and that
  basic components are structurally available.

Later (Phase 13), you can add live broker/API connectivity checks.
"""

import importlib
import time
from typing import Any, Dict


def _check_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def get_health_report() -> Dict[str, Any]:
    """
    Return a simple health report.

    Fields:
        engine: "ok" | "error"
        broker_adapter: "ok" | "error"
        risk: "ok" | "error"
        data_layer: "ok" | "error"
        ts: float unix timestamp
    """
    engine_ok = _check_import("execution.execution_engine")
    broker_ok = _check_import("infra.broker_factory") or _check_import(
        "infra.dhan_adapter"
    )
    risk_ok = _check_import("risk.risk_engine")
    data_ok = (
        _check_import("data.ohlcv_store")
        and _check_import("data.tick_store")
        and _check_import("data.feature_store")
    )

    report: Dict[str, Any] = {
        "ts": time.time(),
        "engine": "ok" if engine_ok else "error",
        "broker_adapter": "ok" if broker_ok else "error",
        "risk": "ok" if risk_ok else "error",
        "data_layer": "ok" if data_ok else "error",
    }
    overall_ok = engine_ok and broker_ok and risk_ok and data_ok
    report["status"] = "ok" if overall_ok else "degraded"

    return report
