from core.v2.research.evaluators.ssr_evaluator import SSREvaluator
from core.v2.research.evaluators.stability_evaluator import StabilityEvaluator


def test_ssr_evaluator_basic():
    evaluator = SSREvaluator()
    result = evaluator.evaluate([True, False, True, True])

    assert result.total == 4
    assert result.successes == 3
    assert result.ssr == 0.75


def test_ssr_evaluator_empty():
    evaluator = SSREvaluator()
    result = evaluator.evaluate([])

    assert result.total == 0
    assert result.ssr == 0.0


def test_stability_evaluator_basic():
    evaluator = StabilityEvaluator()
    result = evaluator.evaluate([1.0, 2.0, 3.0])

    assert result.count == 3
    assert result.mean == 2.0
    assert result.variance > 0
    assert result.stddev > 0


def test_stability_evaluator_single_value():
    evaluator = StabilityEvaluator()
    result = evaluator.evaluate([5.0])

    assert result.count == 1
    assert result.mean == 5.0
    assert result.variance == 0.0
    assert result.stddev == 0.0


def test_stability_evaluator_empty():
    evaluator = StabilityEvaluator()
    result = evaluator.evaluate([])

    assert result.count == 0
    assert result.mean == 0.0
