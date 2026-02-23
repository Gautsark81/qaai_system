from datetime import datetime

from core.v2.operator_dashboard.contracts import (
    StrategyStatus,
    ApprovalStatus,
    SafetyStatus,
)


def test_strategy_status_is_immutable():
    s = StrategyStatus(
        strategy_id="s1",
        lifecycle_state="paper_active",
        shadow_pnl=10.0,
        last_updated=datetime.utcnow(),
    )

    try:
        s.shadow_pnl = 20.0
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_approval_status_fields():
    a = ApprovalStatus(
        strategy_id="s1",
        approved=True,
        approved_by="operator",
        expires_at=None,
    )

    assert a.approved is True
    assert a.approved_by == "operator"


def test_safety_status_fields():
    st = SafetyStatus(
        strategy_id="s1",
        live_allowed=False,
        last_check=datetime.utcnow(),
        reason_summary="no_active_approval",
    )

    assert st.live_allowed is False
    assert "approval" in st.reason_summary
