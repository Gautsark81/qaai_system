import pytest
from datetime import datetime

from core.ssr.contracts.enums import SSRStatus
from core.ssr.contracts.components import SSRComponentScore
from core.ssr.contracts.snapshot import SSRSnapshot


def test_ssr_component_bounds():
    with pytest.raises(ValueError):
        SSRComponentScore(
            name="outcome",
            score=1.5,
            weight=1.0,
            metrics={},
        )


def test_ssr_snapshot_bounds():
    component = SSRComponentScore(
        name="outcome",
        score=0.8,
        weight=1.0,
        metrics={},
    )

    with pytest.raises(ValueError):
        SSRSnapshot(
            strategy_id="s1",
            as_of=datetime.utcnow(),
            ssr=1.2,
            status=SSRStatus.STRONG,
            components={"outcome": component},
            trailing_metrics={},
            confidence=0.9,
            flags=[],
            version="v1",
        )


def test_ssr_snapshot_frozen():
    component = SSRComponentScore(
        name="outcome",
        score=0.8,
        weight=1.0,
        metrics={},
    )

    snap = SSRSnapshot(
        strategy_id="s1",
        as_of=datetime.utcnow(),
        ssr=0.8,
        status=SSRStatus.STABLE,
        components={"outcome": component},
        trailing_metrics={},
        confidence=0.8,
        flags=[],
        version="v1",
    )

    with pytest.raises(Exception):
        snap.ssr = 0.5
