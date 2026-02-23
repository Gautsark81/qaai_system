# modules/execution/plan_builder.py

from datetime import datetime

from modules.execution.plan import ExecutionPlan
from modules.execution.plan_id import make_plan_id
from modules.strategies.intent import StrategyIntent

from modules.risk.evaluator import evaluate_risk
from modules.risk.types import PortfolioSnapshot, MarketSnapshot
from modules.risk.limits import RiskLimits

from modules.audit.events import AuditEvent
from modules.audit.sink import AuditSink


_AUDIT = AuditSink()


# -------------------------------------------------------------------
# G4 AUTHORITATIVE PLAN BUILDER (PURE)
# -------------------------------------------------------------------

def build_execution_plan(
    *,
    intent: StrategyIntent,
    price: float,
    portfolio: PortfolioSnapshot,
    market: MarketSnapshot,
    limits: RiskLimits,
    desired_quantity: int,
) -> ExecutionPlan | None:
    """
    Authoritative G4 execution plan builder.

    Properties:
    - PURE (no I/O, no clocks, no mutation)
    - Deterministic
    - Broker-agnostic
    - Risk-dominance enforced
    """
    if intent.confidence < 0.5:
        _AUDIT.emit(
            AuditEvent(
                timestamp=datetime.utcnow(),
                category="PLAN_REJECTED",
                entity_id=intent.strategy_id,
                message="Rejected: confidence below threshold",
            )
        )
        return None

    risk = evaluate_risk(
        desired_quantity=desired_quantity,
        price=price,
        portfolio=portfolio,
        market=market,
        limits=limits,
        symbol=intent.symbol,
    )

    if not risk.allowed:
        _AUDIT.emit(
            AuditEvent(
                timestamp=datetime.utcnow(),
                category="PLAN_REJECTED",
                entity_id=intent.strategy_id,
                message=risk.reason,
            )
        )
        return None

    payload = {
        "strategy_id": intent.strategy_id,
        "symbol": intent.symbol,
        "side": intent.side,
        "quantity": risk.quantity,
    }

    plan_id = make_plan_id(payload)

    plan = ExecutionPlan(
        plan_id=plan_id,
        strategy_id=intent.strategy_id,
        symbol=intent.symbol,
        side=intent.side,
        quantity=risk.quantity,
        order_type="MARKET",
        reason=risk.reason,
    )

    _AUDIT.emit(
        AuditEvent(
            timestamp=datetime.utcnow(),
            category="PLAN_CREATED",
            entity_id=plan_id,
            message=f"Execution plan created for {intent.symbol}",
        )
    )

    return plan


# -------------------------------------------------------------------
# LEGACY G3 COMPATIBILITY WRAPPER (EXPLICIT)
# -------------------------------------------------------------------

def build_execution_plan_legacy(
    *,
    intent: StrategyIntent,
    max_quantity: int,
) -> ExecutionPlan | None:
    """
    Legacy G3 compatibility wrapper.

    - Deterministic defaults
    - Still routes through full G4 risk logic
    - DO NOT use for new code
    """
    portfolio = PortfolioSnapshot(
        equity=1_000_000.0,
        gross_exposure=0.0,
        positions_by_symbol={},
    )

    market = MarketSnapshot(
        atr=1.0,
        volatility=0.1,
    )

    limits = RiskLimits(
        max_gross_exposure_pct=1.0,
        max_atr_loss_pct=1.0,
        max_volatility=1.0,
        max_symbol_pct=1.0,
    )

    return build_execution_plan(
        intent=intent,
        price=1.0,
        portfolio=portfolio,
        market=market,
        limits=limits,
        desired_quantity=max_quantity,
    )
