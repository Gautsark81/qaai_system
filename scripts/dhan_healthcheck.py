# scripts/dhan_healthcheck.py
from qaai_system.infra.logging_utils import get_logger
from qaai_system.infra.broker_factory import get_broker_adapter

logger = get_logger("dhan_healthcheck")
broker = get_broker_adapter()
ok, info = broker.ping_broker()
if ok:
    logger.info("Dhan ping OK: %s", info)
else:
    logger.error("Dhan ping FAILED: %s", info)
    raise SystemExit(2)
