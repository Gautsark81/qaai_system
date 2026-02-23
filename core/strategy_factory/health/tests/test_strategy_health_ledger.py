import pytest
from datetime import datetime, timedelta

from core.strategy_factory.health.report import StrategyHealthReport
from core.strategy_factory.health.ledger import (
    StrategyHealthLedger,
    StrategyHealthLedgerEntry,
)
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

def test_ledger_appends_entries_in_order():
    ledger = StrategyHealthLedger()

    r1 = _report("S1", healthy=True)
    r2 = _report("S1", healthy=False)

    e1 = ledger.append(r1)
    e2 = ledger.append(r2)

    assert e1.sequence == 1
    assert e2.sequence == 2

    entries = ledger.history("S1")
    assert len(entries) == 2
    assert entries[0].report == r1
    assert entries[1].report == r2


def test_ledger_is_append_only():
    ledger = StrategyHealthLedger()
    r = _report("S1")

    ledger.append(r)

    with pytest.raises(RuntimeError):
        ledger._entries.clear()  # type: ignore[attr-defined]


def test_ledger_filters_by_strategy():
    ledger = StrategyHealthLedger()

    ledger.append(_report("S1"))
    ledger.append(_report("S2"))
    ledger.append(_report("S1"))

    s1_entries = ledger.history("S1")
    s2_entries = ledger.history("S2")

    assert len(s1_entries) == 2
    assert len(s2_entries) == 1


def test_ledger_latest_returns_last_entry():
    ledger = StrategyHealthLedger()

    r1 = _report("S1", healthy=True)
    r2 = _report("S1", healthy=False)

    ledger.append(r1)
    ledger.append(r2)

    latest = ledger.latest("S1")
    assert latest.report == r2


def test_ledger_entry_is_immutable():
    ledger = StrategyHealthLedger()
    entry = ledger.append(_report("S1"))

    with pytest.raises(Exception):
        entry.sequence = 99  # type: ignore[misc]


def test_ledger_entry_has_timestamp():
    ledger = StrategyHealthLedger()
    entry = ledger.append(_report("S1"))

    assert isinstance(entry.timestamp, datetime)
