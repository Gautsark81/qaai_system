import time
from infra.token_bucket import TokenBucket

def test_token_bucket_refill():
    tb = TokenBucket(capacity=2, refill_rate_per_sec=1.0)
    assert tb.consume() is True
    assert tb.consume() is True
    # exhausted now
    assert tb.consume() is False
    # wait 1.1 seconds to allow refill of ~1 token
    time.sleep(1.1)
    assert tb.consume() is True
