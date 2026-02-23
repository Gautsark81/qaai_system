from core.strategy_health.dimensions.regime_fit import RegimeFitDimensionEvaluator
from core.strategy_health.contracts.enums import DimensionVerdict


THRESHOLDS = {
    "history_window": 10,
    "mismatch_ratio_bad": 0.5,
    "instability_warn": 3,
    "instability_bad": 5,
    "fail_score_cap": 0.25,
}


def test_allowed_and_stable_passes():
    evaluator = RegimeFitDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "allowed_regimes": {"TREND"},
            "current_regime": "TREND",
            "recent_regime_history": ["TREND"] * 10,
        }
    )

    assert result.verdict == DimensionVerdict.PASS
    assert result.score > 0.7


def test_forbidden_regime_fails_immediately():
    evaluator = RegimeFitDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "allowed_regimes": {"RANGE"},
            "current_regime": "TREND",
            "recent_regime_history": ["TREND"] * 10,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score <= 0.25


def test_persistent_mismatch_fails():
    evaluator = RegimeFitDimensionEvaluator(thresholds=THRESHOLDS)

    history = ["RANGE"] * 6 + ["TREND"] * 4

    result = evaluator.evaluate(
        inputs={
            "allowed_regimes": {"TREND"},
            "current_regime": "TREND",
            "recent_regime_history": history,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL


def test_regime_transition_warns():
    evaluator = RegimeFitDimensionEvaluator(thresholds=THRESHOLDS)

    history = ["TREND", "RANGE", "TREND", "TREND", "TREND"]

    result = evaluator.evaluate(
        inputs={
            "allowed_regimes": {"TREND"},
            "current_regime": "TREND",
            "recent_regime_history": history,
        }
    )

    assert result.verdict == DimensionVerdict.WARN


def test_no_evidence_fails():
    evaluator = RegimeFitDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(inputs={})

    assert result.verdict == DimensionVerdict.FAIL
