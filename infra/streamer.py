import redis
import mlflow
import json
from infra.logging_utils import get_logger

logger = get_logger("streamer")


class Streamer:
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, decode_responses=True
        )

    def stream_to_redis(self, key, data):
        try:
            self.redis_client.publish(key, json.dumps(data))
            logger.info(f"Streamed to Redis on {key}: {data}")
        except Exception as e:
            logger.error(f"Failed to stream to Redis: {e}")

    def log_to_mlflow(self, symbol, signal_data):
        try:
            with mlflow.start_run(run_name=f"Signal_{symbol}"):
                for k, v in signal_data.items():
                    if isinstance(v, (int, float)):
                        mlflow.log_metric(k, v)
                    elif isinstance(v, str):
                        mlflow.set_tag(k, v)
                logger.info(f"Logged to MLflow: {signal_data}")
        except Exception as e:
            logger.error(f"MLflow logging error: {e}")
