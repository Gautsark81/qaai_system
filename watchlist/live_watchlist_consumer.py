import json
import logging
import os

import redis
from dotenv import load_dotenv

log = logging.getLogger("watchlist.live")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

def run():
    load_dotenv(override=True)

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.Redis.from_url(redis_url, decode_responses=True)

    pubsub = r.pubsub()
    pubsub.subscribe("market:ticks")
    log.info("Subscribed to Redis channel market:ticks for watchlist")

    for msg in pubsub.listen():
        if msg["type"] != "message":
            continue

        try:
            tick = json.loads(msg["data"])
        except Exception as e:
            log.warning(f"Bad tick payload: {e}")
            continue

        instrument = tick.get("instrument_key")
        if not instrument:
            continue

        snapshot = {
            "ts": tick.get("ts"),
            "segment": tick.get("segment"),
            "security_id": tick.get("security_id"),
            "symbol": tick.get("symbol"),
            "ltp": tick.get("ltp"),
            "open": tick.get("open"),
            "high": tick.get("high"),
            "low": tick.get("low"),
            "prev_close": tick.get("prev_close"),
            "volume": tick.get("volume"),
        }

        # Redis hash: watchlist:ltp -> instrument_key -> JSON snapshot
        r.hset("watchlist:ltp", instrument, json.dumps(snapshot))
