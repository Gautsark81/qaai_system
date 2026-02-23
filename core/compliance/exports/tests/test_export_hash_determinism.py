from core.compliance.exports.hasher import CanonicalSHA256Hasher


def test_hash_is_deterministic():
    hasher = CanonicalSHA256Hasher()

    payload = {
        "b": 2,
        "a": 1,
        "nested": {"y": 2, "x": 1},
    }

    h1 = hasher.hash(payload)
    h2 = hasher.hash(payload)

    assert h1 == h2
