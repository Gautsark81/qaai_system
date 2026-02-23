import pytest

import builtins

from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)

# Expose LiveCapitalScaler for tests that do not import it explicitly
builtins.LiveCapitalScaler = LiveCapitalScaler

from dataclasses import dataclass
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)

from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)

@pytest.fixture
def live_capital_scaler():
    return LiveCapitalScaler()

# ---------------------------------------------------------------------
# SSR METRICS ADAPTER (CRITICAL)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class SSRMetrics:
    ssr: float
    win_rate: float
    drawdown: float
    total_trades: int

    def is_live_eligible(self) -> bool:
        return (
            self.ssr >= 0.8
            and self.total_trades >= 100
            and self.drawdown <= 0.2
        )


# ---------------------------------------------------------------------
# STRATEGY CONTEXT OBJECT (CRITICAL)
# ---------------------------------------------------------------------

@dataclass
class StrategyContext:
    strategy_id: str
    state: PromotionState
    capital_authority: bool = True
    execution_authority: bool = True
    operator_veto: bool = False


# ---------------------------------------------------------------------
# SSR FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
def strong_ssr_metrics():
    return SSRMetrics(
        ssr=0.86,
        win_rate=0.62,
        drawdown=0.04,
        total_trades=500,
    )


@pytest.fixture
def weak_ssr_metrics():
    return SSRMetrics(
        ssr=0.42,
        win_rate=0.44,
        drawdown=0.21,
        total_trades=80,
    )


@pytest.fixture
def governed_live_ssr_metrics():
    return SSRMetrics(
        ssr=0.85,
        win_rate=0.61,
        drawdown=0.05,
        total_trades=600,
    )


# ---------------------------------------------------------------------
# RISK ENVELOPE FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
def valid_risk_envelope():
    return "VALID"


@pytest.fixture
def invalid_risk_envelope():
    return "INVALID"


@pytest.fixture
def valid_governed_live_risk_envelope():
    return "VALID"


@pytest.fixture
def invalid_governed_live_risk_envelope():
    return "INVALID"


# ---------------------------------------------------------------------
# STRATEGY FIXTURES (PHASE 11)
# ---------------------------------------------------------------------

@pytest.fixture
def healthy_tiny_live_strategy():
    return StrategyContext(
        strategy_id="STRAT-TL-001",
        state=PromotionState.TINY_LIVE,
        capital_authority=True,
        execution_authority=True,
        operator_veto=False,
    )


@pytest.fixture
def eligible_tiny_live_strategy(healthy_tiny_live_strategy):
    return healthy_tiny_live_strategy


@pytest.fixture
def eligible_tiny_live_for_full_admission(
    healthy_tiny_live_strategy,
):
    return healthy_tiny_live_strategy


@pytest.fixture
def eligible_governed_live_strategy(
    eligible_tiny_live_for_full_admission,
):
    return eligible_tiny_live_for_full_admission


@pytest.fixture
def non_tiny_live_strategy():
    return PromotionState.PAPER


# ---------------------------------------------------------------------
# STRATEGY FIXTURES (PHASE 12 — LIVE CAPITAL SCALING)
# ---------------------------------------------------------------------

@pytest.fixture
def live_strategy_context():
    """
    Phase 12: Fully LIVE strategy eligible for capital scaling.
    """
    return StrategyContext(
        strategy_id="STRAT-LIVE-001",
        state=PromotionState.LIVE,
        capital_authority=True,
        execution_authority=True,
        operator_veto=False,
    )

# ---------------------------------------------------------------------
# PHASE 12 — LIVE CAPITAL SCALING SSR FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
def strong_live_ssr_metrics():
    """
    Eligible for capital scaling increase.
    """
    return SSRMetrics(
        ssr=0.90,
        win_rate=0.64,
        drawdown=0.03,
        total_trades=1200,
    )


@pytest.fixture
def weak_live_ssr_metrics():
    """
    SSR decay — should block scaling up.
    """
    return SSRMetrics(
        ssr=0.62,
        win_rate=0.51,
        drawdown=0.09,
        total_trades=900,
    )


@pytest.fixture
def high_drawdown_ssr_metrics():
    """
    Drawdown breach — must hard-block scaling.
    """
    return SSRMetrics(
        ssr=0.88,
        win_rate=0.60,
        drawdown=0.31,  # 🔴 Breach
        total_trades=1500,
    )

# ---------------------------------------------------------------------
# PHASE 12 — LIVE CAPITAL SCALING RISK ENVELOPES
# ---------------------------------------------------------------------

@pytest.fixture
def safe_risk_envelope():
    """
    Risk envelope safe for capital scaling.
    """
    return "SAFE"


@pytest.fixture
def unsafe_risk_envelope():
    """
    Risk envelope breached — must trigger scale-down or freeze.
    """
    return "UNSAFE"
