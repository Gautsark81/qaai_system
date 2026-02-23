# pipeline/signal_ingestion.py

import pandas as pd
from infra.db_client import DBClient
from screening.stock_screener import StockScreener
from features.indicators import IndicatorEngine
from modules.signal_engine import SignalEngine
from infra.streamer import Streamer
from infra.logging_utils import get_logger

logger = get_logger("signal_ingestion")


class SignalIngestionPipeline:
    def __init__(self):
        self.db = DBClient()
        self.indicator_engine = IndicatorEngine()
        self.screener = StockScreener(self.indicator_engine)
        self.signal_engine = SignalEngine()
        self.streamer = Streamer()

    def run(self):
        logger.info("🚀 Starting Signal Ingestion Loop")
        watchlist = self.db.fetch_watchlist()

        if not watchlist:
            logger.warning("⚠️ Watchlist is empty.")
            return pd.DataFrame()

        # Fetch OHLCV data for each symbol
        symbol_data = {}
        for symbol in watchlist:
            df = self.db.fetch_ohlcv(symbol, days=60)
            logger.info(f"📊 {symbol} OHLCV rows: {len(df)}")
            symbol_data[symbol] = df

        # Step 1: Run Screener
        logger.info("🔍 Running stock screener...")
        results_df = self.screener.screen(symbol_data)
        if results_df.empty:
            logger.warning("🧹 No symbols passed screening.")
            return pd.DataFrame()

        logger.info(f"✅ Screener passed symbols: {results_df['symbol'].tolist()}")

        # Step 2: Write screener scores to DB
        self.db.write_screener_scores(results_df)

        # Step 3: Trigger Signal Engine
        logger.info("🧠 Generating signals...")
        signals_df = self.signal_engine.process_signals(results_df["symbol"].tolist())

        if signals_df.empty:
            logger.warning("🛑 No actionable signals generated.")
            return pd.DataFrame()

        logger.info(f"📡 Signals generated: {len(signals_df)}")

        # Step 4: Stream signals to Redis/MLflow
        self.streamer.stream(signals_df)

        logger.info("✅ Signal ingestion loop complete.")
        return signals_df


if __name__ == "__main__":
    pipeline = SignalIngestionPipeline()
    pipeline.run()
