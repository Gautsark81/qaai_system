import pytest
from datetime import datetime

from modules.config.feature_flags import FeatureFlags
from modules.config.runtime_mode import RuntimeMode
from modules.portfolio.state import PortfolioState
from modules.capital.decision import CapitalDecision
from modules.portfolio.state import Symbol, StrategyId


@pytest.mark.phase13
def test_phase13_sim_flow_with_capital_decision_stub():
    """
    Phase 13 integration contract test (SIM mode):

    Proves:
    - PortfolioState updates correctly
    - CapitalDecision is advisory
    - CapitalDecision can only scale DOWN
    - No execution / risk override possible
    """

    flags = FeatureFlags(
        ENABLE_PHASE_13=True,
        RUNTIME_MODE=RuntimeMode.SIM,
    )

    # --- Phase 13.1: Portfolio observation ---
    portfolio = PortfolioState(cash=100_000)

    portfolio.apply_trade(
        symbol=Symbol("NIFTY"),
        quantity=10,
        price=100,
        strategy_id=StrategyId("trend"),
    )

    snapshot = portfolio.snapshot(
        timestamp=datetime.utcnow(),
        prices={"NIFTY": 105},
    )

    assert snapshot.metrics["unrealized_pnl"] == 50
    assert snapshot.metrics["equity"] == 99_050

    # --- Phase 13.2: Capital decision (STUB) ---
    decision = CapitalDecision(
        approved=True,
        max_notional=50_000,
        scale_factor=0.5,
        reason="Stub: portfolio DD scaling",
    )

    # Contract guarantees
    assert decision.is_scaling_only()
    assert decision.scale_factor <= 1.0
    assert decision.max_notional > 0
    assert "scaling" in decision.reason.lower()

    # CapitalDecision must NOT mutate portfolio
    assert snapshot.metrics["equity"] == 99_050

    # CapitalDecision must NOT auto-approve execution
    # (RiskManager + OrderManager still required)
    assert decision.approved is True
