# tests/test_idempotency_redis.py
import os
import pytest

skip_reason = "redis not available or AMATS_RUN_REDIS_TESTS not set"
try:
    import redis  # noqa: F401
    _HAS_REDIS = True
except Exception:
    _HAS_REDIS = False

pytestmark = pytest.mark.skipif(not (_HAS_REDIS and os.environ.get("AMATS_RUN_REDIS_TESTS") == "1"), reason=skip_reason)

from clients.idempotency_redis import RedisIdempotencyStore

def test_redis_idempotency_store_basic(tmp_path):
    store = RedisIdempotencyStore(host="localhost", port=6379, db=1, prefix="test:amats:")
    # use a short key to avoid collisions; ensure it's removed at end
    key = "redis-test-key"
    try:
        assert key not in store
        store[key] = {"foo": "bar"}
        assert key in store
        v = store.get(key)
        assert v["foo"] == "bar"
    finally:
        try:
            store._client.delete(store._key(key))
        except Exception:
            pass
        store.close()
