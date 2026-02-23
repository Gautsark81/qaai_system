# File: watchlist/auto_updater.py

from infra.db_client import DBClient
from screening.stock_screener import StockScreener
from features.indicators import IndicatorEngine
from infra.logging_utils import get_logger

logger = get_logger("auto_watchlist")


class AutoWatchlistBuilder:
    def __init__(self, min_volume=100000, top_n=10):
        self.db = DBClient()
        self.indicator_engine = IndicatorEngine()
        self.screener = StockScreener(self.indicator_engine)
        self.min_volume = min_volume
        self.top_n = top_n

    def fetch_market_universe(self):
        # Replace with Dhan universe fetch if integrated
        return [
            "RELIANCE",
            "TCS",
            "INFY",
            "HDFCBANK",
            "ICICIBANK",
            "LT",
            "SBIN",
            "HINDUNILVR",
            "AXISBANK",
            "WIPRO",
        ]

    def build(self):
        logger.info("🧠 Auto-adaptive watchlist building started...")
        universe = self.fetch_market_universe()

        symbol_data = {}
        for symbol in universe:
            df = self.db.fetch_ohlcv(symbol, days=30)
            if df.empty or df["volume"].mean() < self.min_volume:
                continue
            symbol_data[symbol] = df

        logger.info(f"✅ {len(symbol_data)} symbols passed basic filters")
        if not symbol_data:
            logger.warning("⚠️ No valid symbols found for auto-watchlist update.")
            return []

        screener_results = self.screener.screen(symbol_data)
        if screener_results.empty:
            logger.info("🧹 Screener returned no candidates.")
            return []

        top_symbols = (
            screener_results.sort_values("score", ascending=False)
            .head(self.top_n)["symbol"]
            .tolist()
        )
        logger.info(f"📈 Top symbols selected: {top_symbols}")

        # Update the watchlist in the DB
        self.update_watchlist(top_symbols)
        return top_symbols

    def update_watchlist(self, symbols):
        existing = self.db.fetch_watchlist()
        new_entries = list(set(symbols) - set(existing))

        if not new_entries:
            logger.info("ℹ️ Watchlist already up-to-date.")
            return

        try:
            with self.db.conn.cursor() as cur:
                for symbol in new_entries:
                    cur.execute(
                        """
                        INSERT INTO watchlist (symbol, active)
                        VALUES (%s, TRUE)
                        ON CONFLICT (symbol) DO UPDATE SET active = TRUE;
                    """,
                        (symbol,),
                    )
            self.db.conn.commit()
            logger.info(f"✅ Updated watchlist with: {new_entries}")
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"❌ Watchlist update failed: {e}")


if __name__ == "__main__":
    builder = AutoWatchlistBuilder(min_volume=100000, top_n=5)
    builder.build()
