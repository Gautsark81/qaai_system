from datetime import datetime, timedelta

from domain.validation.fingerprint_validator import FingerprintValidator
from domain.behavior_fingerprint.fingerprint import (
    StrategyBehaviorFingerprint,
    IdentityFingerprint,
    MarketInteractionFingerprint,
    RiskExposureFingerprint,
    ExecutionStyleFingerprint,
    PerformanceShapeFingerprint,
    StabilityFingerprint,
    GovernanceFingerprint,
    FingerprintMeta,
)
from domain.behavior_fingerprint.enums import (
    StrategyFamily,
    GenerationSource,
    RiskLevel,
    StabilityLevel,
)


def _valid_fingerprint():
    return StrategyBehaviorFingerprint(
        identity=IdentityFingerprint(
            strategy_id="TEST_STRAT",
            strategy_family=StrategyFamily.TREND,
            generation_source=GenerationSource.HUMAN,
            code_hash="abc123",
            parameter_hash="def456",
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
            avg_leverage=1.0,
            stop_type="ATR",
            stop_distance_pct=0.01,
            tail_risk_exposure=RiskLevel.LOW,
            capital_concentration=0.10,
        ),
        execution_behavior=ExecutionStyleFingerprint(
            order_types={"market"},
            slippage_sensitivity="low",
            latency_tolerance_ms=200,
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


def test_valid_fingerprint_passes_validation():
    fp = _valid_fingerprint()
    result = FingerprintValidator.validate(fp)
    assert result.valid is True
    assert result.errors == []
