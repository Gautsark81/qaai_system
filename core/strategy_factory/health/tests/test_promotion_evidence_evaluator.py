import pytest

from core.strategy_factory.health.ledger import StrategyHealthLedger
from core.strategy_factory.health.evaluator import (
    PromotionEvidenceEvaluator,
    PromotionEvidence,
)
from core.strategy_factory.health.report import StrategyHealthReport
from core.ssr.contracts.components import SSRComponentScore
from core.strategy_health.contracts.enums import HealthStatus


# ------------------------------------------------------------------
# TEST STUBS (OPAQUE, CONTRACT-ONLY)
# ------------------------------------------------------------------

class _SnapshotStub:
    def __init__(self, *, status: HealthStatus):
        self.status = status

    def to_dict(self):
        return {"status": self.status.value}


class _RegimeStub:
    def __init__(self, *, is_favorable: bool):
        self.is_favorable = is_favorable

    def to_dict(self):
        return {"is_favorable": self.is_favorable}


def _stability(score: float) -> SSRComponentScore:
    return SSRComponentScore(
        name="health_stability",
        score=score,
        weight=1.0,
        metrics={},
    )


def _report(dna: str, *, healthy: bool = True) -> StrategyHealthReport:
    return StrategyHealthReport(
        strategy_dna=dna,
        health_snapshot=_SnapshotStub(
            status=HealthStatus.HEALTHY if healthy else HealthStatus.CRITICAL
        ),
        stability_score=_stability(0.9),
        regime=_RegimeStub(is_favorable=True),
    )


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_evaluator_blocks_when_no_history():
    ledger = StrategyHealthLedger()
    evaluator = PromotionEvidenceEvaluator()

    evidence = evaluator.evaluate("S1", ledger)

    assert evidence.promotable is False
    assert "no health history" in evidence.reasons[0].lower()


def test_evaluator_blocks_on_latest_unhealthy():
    ledger = StrategyHealthLedger()
    evaluator = PromotionEvidenceEvaluator()

    ledger.append(_report("S1", healthy=True))
    ledger.append(_report("S1", healthy=False))

    evidence = evaluator.evaluate("S1", ledger)

    assert evidence.promotable is False
    assert "latest health is not healthy" in evidence.reasons[0].lower()


def test_evaluator_allows_when_latest_healthy():
    ledger = StrategyHealthLedger()
    evaluator = PromotionEvidenceEvaluator()

    ledger.append(_report("S1", healthy=False))
    ledger.append(_report("S1", healthy=True))

    evidence = evaluator.evaluate("S1", ledger)

    assert evidence.promotable is True
    assert evidence.strategy_dna == "S1"


def test_evaluator_reports_last_entry_timestamp():
    ledger = StrategyHealthLedger()
    evaluator = PromotionEvidenceEvaluator()

    entry = ledger.append(_report("S1"))

    evidence = evaluator.evaluate("S1", ledger)

    assert evidence.last_evaluated_at == entry.timestamp


def test_evidence_is_immutable():
    ledger = StrategyHealthLedger()
    evaluator = PromotionEvidenceEvaluator()

    ledger.append(_report("S1"))
    evidence = evaluator.evaluate("S1", ledger)

    with pytest.raises(Exception):
        evidence.promotable = False  # type: ignore[misc]
