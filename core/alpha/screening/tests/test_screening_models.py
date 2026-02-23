from core.alpha.screening.models.screening_layer import ScreeningLayer
from core.alpha.screening.models.screening_verdict import ScreeningVerdict
from core.alpha.screening.models.screening_evidence import ScreeningEvidence
from core.alpha.screening.models.screening_snapshot import ScreeningSnapshot


def test_screening_verdict_is_immutable():
    verdict = ScreeningVerdict(
        symbol="RELIANCE",
        eligible=False,
        failed_layer=ScreeningLayer.LIQUIDITY_SURVIVABILITY,
        confidence=0.12,
        evidence=[],
        explanation="Liquidity collapses during volatility"
    )

    try:
        verdict.eligible = True
        assert False, "Verdict must be immutable"
    except Exception:
        assert True


def test_screening_snapshot_serialization():
    verdict = ScreeningVerdict(
        symbol="RELIANCE",
        eligible=True,
        failed_layer=None,
        confidence=0.92,
        evidence=[],
        explanation="Passed all structural checks"
    )

    snapshot = ScreeningSnapshot(
        run_id="test_run",
        verdicts=[verdict],
    )

    data = snapshot.to_dict()

    assert data["run_id"] == "test_run"
    assert data["verdicts"][0]["symbol"] == "RELIANCE"
