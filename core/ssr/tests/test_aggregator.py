import pytest
from datetime import datetime

from core.ssr.aggregator import SSRAggregator
from core.ssr.contracts.components import SSRComponentScore
from core.ssr.contracts.enums import SSRStatus


def _comp(name, score, weight=1.0):
    return SSRComponentScore(
        name=name,
        score=score,
        weight=weight,
        metrics={},
    )


def test_strong_ssr():
    agg = SSRAggregator()

    snap = agg.aggregate(
        strategy_id="s1",
        as_of=datetime.utcnow(),
        components=[
            _comp("outcome", 0.9),
            _comp("health", 0.85),
            _comp("consistency", 0.8),
        ],
        trailing_metrics={},
        confidence=0.9,
        version="v1",
    )

    assert snap.status == SSRStatus.STRONG
    assert snap.ssr >= 0.8


def test_stable_ssr():
    agg = SSRAggregator()

    snap = agg.aggregate(
        strategy_id="s2",
        as_of=datetime.utcnow(),
        components=[
            _comp("outcome", 0.7),
            _comp("health", 0.75),
            _comp("consistency", 0.7),
        ],
        trailing_metrics={},
        confidence=0.8,
        version="v1",
    )

    assert snap.status == SSRStatus.STABLE


def test_weak_ssr_due_to_two_weak_components():
    agg = SSRAggregator()

    snap = agg.aggregate(
        strategy_id="s3",
        as_of=datetime.utcnow(),
        components=[
            _comp("outcome", 0.45),
            _comp("health", 0.4),
            _comp("consistency", 0.9),
        ],
        trailing_metrics={},
        confidence=0.7,
        version="v1",
    )

    assert snap.status == SSRStatus.WEAK
    assert len(snap.flags) >= 2


def test_failing_ssr_dominates():
    agg = SSRAggregator()

    snap = agg.aggregate(
        strategy_id="s4",
        as_of=datetime.utcnow(),
        components=[
            _comp("outcome", 0.2),
            _comp("health", 0.9),
            _comp("consistency", 0.9),
        ],
        trailing_metrics={},
        confidence=0.6,
        version="v1",
    )

    assert snap.status == SSRStatus.FAILING
    assert any("FAILING" in f.code for f in snap.flags)


def test_weighted_ssr_calculation():
    agg = SSRAggregator()

    snap = agg.aggregate(
        strategy_id="s5",
        as_of=datetime.utcnow(),
        components=[
            _comp("outcome", 1.0, weight=2.0),
            _comp("health", 0.0, weight=1.0),
        ],
        trailing_metrics={},
        confidence=1.0,
        version="v1",
    )

    assert snap.ssr == pytest.approx(0.6667, rel=1e-4)


def test_empty_components_rejected():
    agg = SSRAggregator()

    with pytest.raises(ValueError):
        agg.aggregate(
            strategy_id="s6",
            as_of=datetime.utcnow(),
            components=[],
            trailing_metrics={},
            confidence=0.5,
            version="v1",
        )
