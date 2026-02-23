# execution/trade_logger.py

import csv
import os
import json
import logging
from datetime import datetime


class TradeLogger:
    def __init__(
        self,
        log_dir="logs/trades",
        filename="trade_log.csv",
        json_log_file="trade_log.jsonl",
        log_to_console=True,
    ):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.csv_path = os.path.join(log_dir, filename)
        self.json_path = os.path.join(log_dir, json_log_file)
        self.log_to_console = log_to_console

        self.logger = self._setup_logger()
        self.headers = [
            "timestamp",
            "symbol",
            "side",
            "quantity",
            "entry_price",
            "execution_price",
            "exit_price",
            "pnl",
            "status",
            "strategy_id",
            "note",
            "order_id",
            "mode",
        ]

        if not os.path.isfile(self.csv_path):
            self._init_csv_file()

    def _setup_logger(self):
        logger = logging.getLogger("TradeLogger")
        logger.setLevel(logging.INFO)

        if self.log_to_console and not logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _init_csv_file(self):
        try:
            with open(self.csv_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
            self.logger.info("Initialized CSV trade log.")
        except Exception as e:
            self.logger.error(f"CSV init failed: {e}")

    def log_trade(self, trade: dict):
        try:
            formatted = self._format_trade(trade)

            # Append to CSV
            with open(self.csv_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([formatted.get(h, "") for h in self.headers])

            # Append to JSONL
            with open(self.json_path, mode="a") as f:
                f.write(json.dumps(formatted) + "\n")

            self.logger.info(
                f"Logged: {formatted['symbol']} | {formatted['side']} | {formatted['status']}"
            )

        except Exception as e:
            self.logger.error(f"[log_trade] Failed to log: {e}")

    def _format_trade(self, trade: dict) -> dict:
        return {
            "timestamp": str(trade.get("timestamp", datetime.now())),
            "symbol": trade.get("symbol", ""),
            "side": trade.get("side", ""),
            "quantity": trade.get("quantity", ""),
            "entry_price": trade.get("entry_price", ""),
            "execution_price": trade.get("execution_price", ""),
            "exit_price": trade.get("exit_price", ""),
            "pnl": trade.get("pnl", ""),
            "status": trade.get("status", "open"),
            "strategy_id": trade.get("strategy_id", "unknown"),
            "note": trade.get("note", ""),
            "order_id": trade.get("order_id", ""),
            "mode": os.getenv("MODE", "paper").lower(),
        }
