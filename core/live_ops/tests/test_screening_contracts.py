from core.live_ops.screening import ScreeningResult


def test_screening_result_contract():
    result = ScreeningResult(
        symbol="RELIANCE",
        passed=True,
        reasons=["Volume spike", "Trend alignment"],
        score=0.87,
    )

    assert result.symbol == "RELIANCE"
    assert result.passed is True
    assert isinstance(result.reasons, list)
    assert result.score >= 0.0
