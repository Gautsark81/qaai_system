from datetime import datetime, timedelta
from domain.behavior_fingerprint.fingerprint import (
    StrategyBehaviorFingerprint,
    FingerprintMeta,
)
from domain.behavior_fingerprint.identity import IdentityFingerprint
from domain.behavior_fingerprint.market_behavior import MarketInteractionFingerprint
from domain.behavior_fingerprint.risk_behavior import RiskExposureFingerprint
from domain.behavior_fingerprint.execution_behavior import ExecutionStyleFingerprint
from domain.behavior_fingerprint.performance_shape import PerformanceShapeFingerprint
from domain.behavior_fingerprint.stability import StabilityFingerprint
from domain.behavior_fingerprint.governance import GovernanceFingerprint
from domain.behavior_fingerprint.enums import (
    StrategyFamily,
    GenerationSource,
    RiskLevel,
    StabilityLevel,
)


def test_full_strategy_behavior_fingerprint():
    fp = StrategyBehaviorFingerprint(
        identity=IdentityFingerprint(
            strategy_id="s1",
            strategy_family=StrategyFamily.TREND,
            generation_source=GenerationSource.HUMAN,
            code_hash="hash1",
            parameter_hash="hash2",
            creation_ts=datetime.utcnow(),
        ),
        market_behavior=MarketInteractionFingerprint(
            instruments=["NIFTY"],
            avg_holding_period=timedelta(minutes=10),
            trade_frequency_per_day=5.0,
            market_regimes={"trend"},
            session_bias={"open"},
        ),
        risk_behavior=RiskExposureFingerprint(
            max_position_pct=0.05,
            avg_leverage=1.5,
            stop_type="ATR",
            stop_distance_pct=0.01,
            tail_risk_exposure=RiskLevel.LOW,
            capital_concentration=0.15,
        ),
        execution_behavior=ExecutionStyleFingerprint(
            order_types={"market"},
            slippage_sensitivity="low",
            latency_tolerance_ms=300,
            partial_fill_handling="accept",
        ),
        performance_shape=PerformanceShapeFingerprint(
            win_rate_bucket="55-70",
            payoff_ratio_bucket="1-2",
            drawdown_profile="shallow",
            equity_curve_shape="smooth",
        ),
        stability_profile=StabilityFingerprint(
            parameter_sensitivity=StabilityLevel.LOW,
            regime_dependence=StabilityLevel.LOW,
            sample_efficiency=StabilityLevel.HIGH,
            backtest_variance=StabilityLevel.STABLE,
        ),
        governance_flags=GovernanceFingerprint(
            allowed_environments={"backtest"},
            requires_human_approval=False,
            max_capital_allocation_pct=0.05,
            kill_switch_required=True,
            audit_level="standard",
        ),
        meta=FingerprintMeta(
            schema_version="1.0",
            generated_by="unit_test",
            generated_ts=datetime.utcnow(),
            validation_status="valid",
        ),
    )

    assert fp.identity.strategy_id == "s1"
