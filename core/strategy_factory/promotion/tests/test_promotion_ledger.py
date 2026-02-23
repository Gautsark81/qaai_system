import pytest
from datetime import datetime, timezone

from core.strategy_factory.promotion.engine import PromotionDecision
from core.strategy_factory.promotion.ledger import PromotionLedger


def _decision(promote: bool, fraction: float):
    return PromotionDecision(
        strategy_dna="S1",
        promote=promote,
        recommended_fraction=fraction,
        reasons=["ok"] if promote else ["blocked"],
    )


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_ledger_appends_decisions():
    ledger = PromotionLedger()

    d1 = _decision(True, 0.2)
    d2 = _decision(False, 0.0)

    ledger.append(d1)
    ledger.append(d2)

    history = ledger.history("S1")

    assert len(history) == 2
    assert history[0] is d1
    assert history[1] is d2


def test_ledger_is_append_only():
    ledger = PromotionLedger()

    d1 = _decision(True, 0.2)
    ledger.append(d1)

    with pytest.raises(RuntimeError):
        ledger._records.clear()  # type: ignore[attr-defined]


def test_ledger_returns_empty_for_unknown_strategy():
    ledger = PromotionLedger()

    assert ledger.history("UNKNOWN") == []


def test_ledger_entries_are_immutable():
    ledger = PromotionLedger()

    d1 = _decision(True, 0.2)
    ledger.append(d1)

    stored = ledger.history("S1")[0]

    with pytest.raises(Exception):
        stored.promote = False  # type: ignore[misc]


def test_ledger_preserves_order():
    ledger = PromotionLedger()

    d1 = _decision(True, 0.1)
    d2 = _decision(True, 0.2)
    d3 = _decision(False, 0.0)

    ledger.append(d1)
    ledger.append(d2)
    ledger.append(d3)

    history = ledger.history("S1")

    assert history == [d1, d2, d3]
