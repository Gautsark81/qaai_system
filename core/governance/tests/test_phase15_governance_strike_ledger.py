from datetime import datetime, timezone
from core.governance.escalation.governance_strike_ledger import (
    GovernanceStrikeLedger,
)


def test_strike_appends_and_increments():
    ledger = GovernanceStrikeLedger()

    entry1 = ledger.append_strike(
        governance_id="gov-1",
        strategy_id="STRAT-1",
        reason="DRIFT",
        decision_checksum="chk-1",
    )

    entry2 = ledger.append_strike(
        governance_id="gov-1",
        strategy_id="STRAT-1",
        reason="DRIFT_AGAIN",
        decision_checksum="chk-2",
    )

    assert entry1.strike_number == 1
    assert entry2.strike_number == 2
    assert ledger.get_strike_count("gov-1") == 2


def test_strike_hash_chain_integrity():
    ledger = GovernanceStrikeLedger()

    e1 = ledger.append_strike(
        governance_id="gov-2",
        strategy_id="STRAT-2",
        reason="FIRST",
        decision_checksum="a",
    )

    e2 = ledger.append_strike(
        governance_id="gov-2",
        strategy_id="STRAT-2",
        reason="SECOND",
        decision_checksum="b",
    )

    assert e2.previous_hash == e1.compute_hash()


def test_strike_is_governance_scoped():
    ledger = GovernanceStrikeLedger()

    ledger.append_strike(
        governance_id="gov-A",
        strategy_id="STRAT-1",
        reason="A1",
        decision_checksum="x",
    )

    ledger.append_strike(
        governance_id="gov-B",
        strategy_id="STRAT-2",
        reason="B1",
        decision_checksum="y",
    )

    assert ledger.get_strike_count("gov-A") == 1
    assert ledger.get_strike_count("gov-B") == 1


def test_ledger_entries_are_immutable():
    ledger = GovernanceStrikeLedger()

    entry = ledger.append_strike(
        governance_id="gov-3",
        strategy_id="STRAT-3",
        reason="IMMUTABLE",
        decision_checksum="z",
    )

    try:
        entry.reason = "MODIFIED"
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_last_strike_resolution_by_timestamp():
    ledger = GovernanceStrikeLedger()

    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 2, tzinfo=timezone.utc)

    ledger.append_strike(
        governance_id="gov-4",
        strategy_id="STRAT-4",
        reason="OLD",
        decision_checksum="1",
        timestamp=t1,
    )

    ledger.append_strike(
        governance_id="gov-4",
        strategy_id="STRAT-4",
        reason="NEW",
        decision_checksum="2",
        timestamp=t2,
    )

    last = ledger.get_last_strike("gov-4")
    assert last.reason == "NEW"