# execution/fill_monitor.py

import time
import logging
from datetime import datetime
from qaai_system.execution.execution_engine import ExecutionEngine
from utils.price_fetcher import get_latest_price  # This function must be implemented
from infra.config_loader import load_config

# Initialize dependencies manually
from qaai_system.execution.broker_adapter import BrokerAdapter
from qaai_system.execution.order_manager import OrderManager
from qaai_system.execution.risk_manager import RiskManager
from qaai_system.execution.trade_logger import TradeLogger
from dummy.signal_provider import (
    DummySignalProvider,
)  # Replace with actual signal provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FillMonitor")


def run_monitor():
    config = load_config("config.yaml")
    broker = BrokerAdapter(mode="paper")
    risk = RiskManager(config.get("risk", {}))
    trade_logger = TradeLogger()
    order_manager = OrderManager(broker, risk, trade_logger)
    signal_provider = DummySignalProvider()  # Won't be used here

    engine = ExecutionEngine(
        signal_provider=signal_provider,
        order_manager=order_manager,
        risk_manager=risk,
        trade_logger=trade_logger,
        broker_adapter=broker,
        config=config,
    )

    while True:
        logger.info(
            f"Checking open orders @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        engine.monitor_open_orders(get_price_func=get_latest_price)
        time.sleep(config.get("fill_poll_interval", 10))


if __name__ == "__main__":
    run_monitor()
