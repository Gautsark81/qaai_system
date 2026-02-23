import json
import time
import logging
from collections import defaultdict

import redis
from dotenv import load_dotenv
import os

log = logging.getLogger("screening.live")
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
    log.info("Subscribed to Redis channel market:ticks for screening")

    # state: instrument_key -> current bar + rolling info
    state = defaultdict(lambda: {
        "last_minute": None,
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "volume": 0.0,
        "vwap_numerator": 0.0,
        "vwap_denominator": 0.0,
    })

    for msg in pubsub.listen():
        if msg["type"] != "message":
            continue

        try:
            tick = json.loads(msg["data"])
        except Exception as e:
            log.warning(f"Bad tick payload: {e}")
            continue

        instrument = tick.get("instrument_key")
        ts = tick.get("ts")  # ms
        ltp = tick.get("ltp")
        vol = tick.get("volume")

        if not instrument or ltp is None or ts is None:
            continue

        minute = int(ts // 60000)  # minute bucket

        s = state[instrument]

        if s["last_minute"] is None or minute != s["last_minute"]:
            # new minute -> finalize previous bar, compute factors, publish
            if s["last_minute"] is not None:
                _publish_bar_and_factors(r, instrument, s)

            # reset for new minute
            s["last_minute"] = minute
            s["open"] = ltp
            s["high"] = ltp
            s["low"] = ltp
            s["close"] = ltp
            s["volume"] = vol or 0
            s["vwap_numerator"] = (ltp * (vol or 0))
            s["vwap_denominator"] = (vol or 0)
        else:
            # update current bar
            s["high"] = max(s["high"], ltp) if s["high"] is not None else ltp
            s["low"] = min(s["low"], ltp) if s["low"] is not None else ltp
            s["close"] = ltp
            if vol is not None:
                delta_vol = max(vol - s["volume"], 0)
                s["vwap_numerator"] += ltp * delta_vol
                s["vwap_denominator"] += delta_vol
                s["volume"] = vol


def _publish_bar_and_factors(r, instrument, s):
    if s["vwap_denominator"] > 0:
        vwap = s["vwap_numerator"] / s["vwap_denominator"]
    else:
        vwap = s["close"]

    bar = {
        "instrument_key": instrument,
        "minute": s["last_minute"],
        "open": s["open"],
        "high": s["high"],
        "low": s["low"],
        "close": s["close"],
        "volume": s["volume"],
        "vwap": vwap,
    }

    # simple factors for now
    factors = {
        "instrument_key": instrument,
        "minute": s["last_minute"],
        "close": s["close"],
        "vwap": vwap,
        "close_minus_vwap": (s["close"] - vwap) if s["close"] and vwap else None,
    }

    payload = json.dumps({"bar": bar, "factors": factors})
    r.publish("screening:factors", payload)
    r.hset(f"screening:last_factors", instrument, json.dumps(factors))
