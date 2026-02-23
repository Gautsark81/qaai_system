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


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_promotion_ready_when_healthy():
    report = StrategyHealthReport(
        strategy_dna="S1",
        health_snapshot=_SnapshotStub(status=HealthStatus.HEALTHY),
        stability_score=_stability(0.9),
        regime=None,
    )

    assert report.promotion_ready is True


def test_blocks_unhealthy_strategy():
    report = StrategyHealthReport(
        strategy_dna="S1",
        health_snapshot=_SnapshotStub(status=HealthStatus.CRITICAL),
        stability_score=_stability(1.0),
        regime=None,
    )

    assert report.promotion_ready is False


def test_blocks_hostile_regime():
    report = StrategyHealthReport(
        strategy_dna="S1",
        health_snapshot=_SnapshotStub(status=HealthStatus.HEALTHY),
        stability_score=_stability(0.8),
        regime=_RegimeStub(is_favorable=False),
    )

    assert report.promotion_ready is False


def test_allows_favorable_regime():
    report = StrategyHealthReport(
        strategy_dna="S1",
        health_snapshot=_SnapshotStub(status=HealthStatus.HEALTHY),
        stability_score=_stability(0.8),
        regime=_RegimeStub(is_favorable=True),
    )

    assert report.promotion_ready is True


def test_to_dict_structure():
    report = StrategyHealthReport(
        strategy_dna="S1",
        health_snapshot=_SnapshotStub(status=HealthStatus.HEALTHY),
        stability_score=_stability(0.75),
        regime=_RegimeStub(is_favorable=True),
    )

    payload = report.to_dict()

    assert payload["strategy_dna"] == "S1"
    assert payload["promotion_ready"] is True
    assert payload["stability_score"]["score"] == 0.75
    assert payload["health"]["status"] == "HEALTHY"
