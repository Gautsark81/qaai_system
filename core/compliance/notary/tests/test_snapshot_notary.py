from core.compliance.notary.snapshot import SnapshotNotary
from core.compliance.notary.verifier import SnapshotVerifier


def test_snapshot_notarization_is_deterministic():
    snapshot = {
        "exports": [{"export_id": "E1"}],
        "provenance": [{"trade_id": "T1"}],
    }

    notary = SnapshotNotary()
    seal1 = notary.notarize(snapshot=snapshot)
    seal2 = notary.notarize(snapshot=snapshot)

    assert seal1.digest == seal2.digest


def test_snapshot_verification_passes_for_same_content():
    snapshot = {
        "exports": [{"export_id": "E1"}],
        "provenance": [{"trade_id": "T1"}],
    }

    notary = SnapshotNotary()
    verifier = SnapshotVerifier()

    seal = notary.notarize(snapshot=snapshot)
    assert verifier.verify(snapshot=snapshot, seal=seal)


def test_snapshot_verification_fails_on_tamper():
    snapshot = {
        "exports": [{"export_id": "E1"}],
        "provenance": [{"trade_id": "T1"}],
    }

    notary = SnapshotNotary()
    verifier = SnapshotVerifier()

    seal = notary.notarize(snapshot=snapshot)

    tampered = {
        "exports": [{"export_id": "E2"}],
        "provenance": [{"trade_id": "T1"}],
    }

    assert not verifier.verify(snapshot=tampered, seal=seal)
