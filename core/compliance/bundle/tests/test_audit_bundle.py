from core.compliance.bundle.bundle import AuditBundleBuilder
from core.compliance.bundle.verifier import AuditBundleVerifier


def test_audit_bundle_is_deterministic():
    builder = AuditBundleBuilder()

    payload = {
        "exports": {"export_id": "E1"},
        "provenance": {"trade_id": "T1"},
        "snapshot_seal": {"digest": "abc"},
    }

    bundle1 = builder.build(**payload)
    bundle2 = builder.build(**payload)

    assert bundle1.bundle_hash == bundle2.bundle_hash
    assert bundle1.payload == bundle2.payload


def test_audit_bundle_verification_passes():
    builder = AuditBundleBuilder()
    verifier = AuditBundleVerifier()

    bundle = builder.build(
        exports={"export_id": "E1"},
        provenance={"trade_id": "T1"},
        snapshot_seal={"digest": "abc"},
    )

    assert verifier.verify(bundle=bundle)


def test_audit_bundle_verification_fails_on_tamper():
    builder = AuditBundleBuilder()
    verifier = AuditBundleVerifier()

    bundle = builder.build(
        exports={"export_id": "E1"},
        provenance={"trade_id": "T1"},
        snapshot_seal={"digest": "abc"},
    )

    tampered = bundle.payload.copy()
    tampered["exports"] = {"export_id": "E2"}

    from core.compliance.bundle.bundle import ImmutableAuditBundle

    tampered_bundle = ImmutableAuditBundle(
        bundle_hash=bundle.bundle_hash,
        payload=tampered,
    )

    assert not verifier.verify(bundle=tampered_bundle)
