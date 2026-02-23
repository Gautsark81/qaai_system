from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalLedgerEventType,
)
from core.strategy_factory.capital.capital_state_verifier import (
    verify_capital_replay,
)


def _entry(strategy, amount):
    return CapitalLedgerEntry(
        strategy_dna=strategy,
        event_type=CapitalLedgerEventType.ALLOCATION_APPROVED,
        amount=amount,
    )


def test_replay_verification_passes_when_identical():
    ledger = [
        _entry("A", 10.0),
        _entry("B", 5.0),
    ]

    report = verify_capital_replay(
        pre_replay_ledger=ledger,
        post_replay_ledger=list(ledger),
    )

    assert report.is_consistent
    assert report.pre_replay_hash == report.post_replay_hash


def test_replay_verification_detects_drift():
    pre = [
        _entry("A", 10.0),
        _entry("B", 5.0),
    ]

    post = [
        _entry("A", 10.0),
        _entry("B", 7.0),  # mutation
    ]

    report = verify_capital_replay(
        pre_replay_ledger=pre,
        post_replay_ledger=post,
    )

    assert not report.is_consistent
    assert report.pre_replay_hash != report.post_replay_hash


def test_strict_mode_raises_on_drift():
    pre = [_entry("A", 10.0)]
    post = [_entry("A", 20.0)]

    try:
        verify_capital_replay(
            pre_replay_ledger=pre,
            post_replay_ledger=post,
            strict=True,
        )
    except RuntimeError:
        return

    assert False, "Strict mode must raise on mismatch"