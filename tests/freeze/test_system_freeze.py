from freeze.system_fingerprint import compute_system_checksum


def test_system_freeze_manifest_fast_and_deterministic():
    c1 = compute_system_checksum(".")
    c2 = compute_system_checksum(".")

    # Deterministic
    assert c1 == c2

    # SHA-256 hex
    assert isinstance(c1, str)
    assert len(c1) == 64
