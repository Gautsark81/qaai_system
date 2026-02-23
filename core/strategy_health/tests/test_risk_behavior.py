from core.strategy_health.dimensions.risk_behavior import RiskBehaviorDimensionEvaluator
from core.strategy_health.contracts.enums import DimensionVerdict


THRESHOLDS = {
    "max_avg_risk": 0.02,
    "warn_avg_risk": 0.015,
    "risk_volatility_warn": 0.01,
    "risk_volatility_bad": 0.02,
    "tail_n": 5,
    "tail_loss_bad": 0.10,
    "fail_score_cap": 0.25,
}


def test_clean_risk_behavior_passes():
    evaluator = RiskBehaviorDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "risk_per_trade": [0.01] * 30,
            "trade_pnl": [0.02] * 30,
            "risk_breaches": 0,
        }
    )

    assert result.verdict == DimensionVerdict.PASS
    assert result.score > 0.5


def test_high_avg_risk_fails():
    evaluator = RiskBehaviorDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "risk_per_trade": [0.03] * 20,
            "trade_pnl": [0.01] * 20,
            "risk_breaches": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score <= 0.25


def test_tail_loss_fails():
    evaluator = RiskBehaviorDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "risk_per_trade": [0.01] * 20,
            "trade_pnl": [-0.05] * 5 + [0.01] * 15,
            "risk_breaches": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL


def test_risk_breach_fails_immediately():
    evaluator = RiskBehaviorDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "risk_per_trade": [0.005] * 10,
            "trade_pnl": [0.01] * 10,
            "risk_breaches": 2,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score <= 0.25


def test_risk_volatility_warns():
    evaluator = RiskBehaviorDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "risk_per_trade": [0.005, 0.02] * 15,
            "trade_pnl": [0.01] * 30,
            "risk_breaches": 0,
        }
    )

    assert result.verdict == DimensionVerdict.WARN
