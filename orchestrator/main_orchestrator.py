# File: qaai_system/orchestrator/main_orchestrator.py

import os
import yaml
import pandas as pd
from typing import Dict, Any

from qaai_system.signal_engine.signal_engine_supercharged import (
    SignalEngineSupercharged,
)
from qaai_system.screener.meta_engine import MetaScreeningEngine
from qaai_system.paper_trading.paper_broker import PaperExecutionProvider
from qaai_system.execution.live_broker import LiveExecutionProvider


class MainOrchestrator:
    """
    End-to-end orchestrator for signals → screening → execution.
    Supports both paper trading (default) and live trading (stub).
    """

    def __init__(self, config_root: str = ".", config_file: str = "execution.yaml"):
        self.config_root = config_root
        self.config_file = os.path.join(config_root, config_file)

        # ------------------------
        # Load config
        # ------------------------
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                cfg = yaml.safe_load(f) or {}
        else:
            cfg = {}

        self.execution_mode = cfg.get("execution_mode", "paper").lower()

        # ------------------------
        # Components
        # ------------------------
        self.signal_engine = SignalEngineSupercharged()
        self.screening_engine = MetaScreeningEngine()

        if self.execution_mode == "paper":
            self.execution_provider = PaperExecutionProvider()
        elif self.execution_mode == "live":
            # Will raise NotImplementedError if instantiated
            self.execution_provider = LiveExecutionProvider()
        else:
            raise ValueError(f"Unknown execution_mode: {self.execution_mode}")

    # -----------------------------------------------------------------
    # Main Cycle
    # -----------------------------------------------------------------
    def run_cycle(self, market_df: pd.DataFrame, top_k: int = 10) -> Dict[str, Any]:
        """
        Orchestrate full pipeline:
        1. Generate signals
        2. Screen universe
        3. Select watchlist
        4. Execute orders
        """

        # --- Step 1: Signals ---
        signals = self.signal_engine.generate_signals(market_df)

        # --- Step 2: Screening ---
        screened = self.screening_engine.run_cycle(market_df, top_k=top_k)

        # --- Step 3: Build orders ---
        orders = []
        for sym, score in screened:
            side = "BUY" if score > 0 else "SELL"
            orders.append({"symbol": sym, "side": side, "qty": 1})

        # --- Step 4: Execute ---
        reports = self.execution_provider.place_orders(orders)

        # --- Step 5: Feedback (update screening engine) ---
        for rpt in reports:
            if rpt["status"] == "FILLED":
                self.screening_engine.on_trade_closed(
                    rpt["symbol"],
                    rpt.get("realized_pnl", 0.0),
                    rpt.get("notional", 1.0),
                )

        return {
            "signals": signals,
            "screened": screened,
            "orders": reports,
        }
