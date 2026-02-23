# core/dashboard_read/replay/tests/test_invariants.py

from core.dashboard_read.replay.engine import OfflineReplayEngine


class SnapshotProxy:
    """
    Proxy that hides one attribute without mutating
    the real snapshot view.
    """
    def __init__(self, real_view, hide: str):
        self._real = real_view
        self._hide = hide

    def __getattr__(self, name):
        if name == self._hide:
            raise AttributeError(name)
        return getattr(self._real, name)


def test_replay_fails_on_missing_evidence(deterministic_replay):
    engine = OfflineReplayEngine()

    broken_view = SnapshotProxy(
        deterministic_replay.snapshot,
        hide="chain_hash",
    )

    class Wrapper:
        snapshot = broken_view

    result = engine.replay(Wrapper())

    assert result.verification_status is False
    assert "Missing required attribute" in result.discrepancies[0].description


def test_replay_detects_forensic_evidence_mutation(deterministic_replay):
    engine = OfflineReplayEngine()

    # CORRECT mutation path
    deterministic_replay.snapshot.components["evil_component"] = {}

    result = engine.replay(deterministic_replay)

    assert result.verification_status is False
    assert "Forensic evidence mutated" in result.discrepancies[0].description