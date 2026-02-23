# utils/ltp_stream.py

import os
import redis
from infra.Dhan_websocket import LTP_CACHE
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger("LTPStream")

USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class LTPStream:
    def __init__(self):
        self.use_redis = USE_REDIS
        if self.use_redis:
            try:
                self.redis = redis.Redis.from_url(REDIS_URL)
                self.redis.ping()
                logger.info("Connected to Redis for LTP stream")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self.use_redis = False

    def get_price(self, symbol):
        # First check in-memory cache
        if symbol in LTP_CACHE:
            return LTP_CACHE[symbol]

        # Then check Redis
        if self.use_redis:
            try:
                value = self.redis.get(f"LTP:{symbol}")
                if value:
                    return float(value.decode())
            except Exception as e:
                logger.warning(f"Redis error for {symbol}: {e}")

        # Fallback
        logger.warning(f"No LTP found for {symbol}")
        return None

    def set_price(self, symbol, price):
        # Update Redis only
        if self.use_redis:
            try:
                self.redis.set(f"LTP:{symbol}", price, ex=30)
            except Exception as e:
                logger.warning(f"Failed to set LTP in Redis: {e}")
