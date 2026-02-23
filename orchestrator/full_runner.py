# === orchestrator/full_runner.py ===

import logging
from modules.signal_engine import SignalEngine
from trader.paper_trader import PaperTrader
from model_selector.selector import ModelAutoSelector

logger = logging.getLogger("Orchestrator")


class FullOrchestrator:
    def __init__(self, model_candidates):
        self.signal_engine = SignalEngine()
        self.paper_trader = PaperTrader()
        self.model_selector = ModelAutoSelector(model_candidates)

    def run_once(self, symbols):
        # 1. Generate signals
        logger.info("🧠 Running SignalEngine...")
        signal_df = self.signal_engine.run(symbols)

        if signal_df.empty:
            logger.warning("❌ No signals generated. Skipping.")
            return

        # 2. Simulate trades
        logger.info("🧪 Executing Paper Trader...")
        self.paper_trader.run(signal_df)

        # 3. Auto-model selection (optional)
        logger.info("🤖 Evaluating best model...")
        df = self.signal_engine.db.fetch_ohlcv(symbols[0], timeframe="5min")
        self.model_selector.evaluate(
            symbols[0], df, label_func=lambda x: x.iloc[-1].to_dict()
        )
        best = self.model_selector.best_model()
        logger.info(f"🏆 Best Model: {best}")

    def get_dashboard_data(self):
        return self.paper_trader.summary()
