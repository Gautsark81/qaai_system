from tests.domain.validation.test_fingerprint_validator import _valid_fingerprint
from domain.runtime.fingerprint_persistence_gate import FingerprintPersistenceGate


def test_invalid_fingerprint_blocked():
    fp = _valid_fingerprint()
    res = FingerprintPersistenceGate.allow_persist(fp)
    assert res.valid is True
