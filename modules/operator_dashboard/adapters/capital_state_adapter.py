# modules/operator_dashboard/adapters/capital_state_adapter.py

from dataclasses import dataclass


# ============================
# Snapshot Contract
# ============================

@dataclass(frozen=True)
class CapitalSnapshot:
    total_capital: float
    allocated: float
    free: float
    utilization_pct: float
    max_drawdown: float


# ============================
# Adapter
# ============================

def get_capital_snapshot() -> CapitalSnapshot:
    """
    Dashboard-safe capital snapshot.

    MUST work even when capital engine has never run.
    """
    try:
        from core.capital.allocation_report import latest_allocation_report

        report = latest_allocation_report()

        if report is None:
            raise RuntimeError("No allocation report yet")

        return CapitalSnapshot(
            total_capital=report.total_capital,
            allocated=report.allocated,
            free=report.free,
            utilization_pct=report.utilization_pct,
            max_drawdown=report.max_drawdown,
        )

    except Exception:
        # ✅ Deterministic fallback
        return CapitalSnapshot(
            total_capital=0.0,
            allocated=0.0,
            free=0.0,
            utilization_pct=0.0,
            max_drawdown=0.0,
        )
