from screening.stock_screener import StockScreener
from infra.logging_utils import get_logger
from infra.config_loader import load_config

logger = get_logger("phase_screening")


def run():
    logger.info("Starting Stock Screening Phase...")

    try:
        config = load_config()
        logger.info(f"Loaded configuration: {config}")
    except Exception as e:
        logger.error(f"[CONFIG LOAD ERROR] {e}")
        return

    try:
        screener = StockScreener(config)
        screened_stocks = screener.run()

        logger.info(
            f"Screening completed. {len(screened_stocks)} stocks passed filters."
        )
        for stock in screened_stocks:
            logger.info(
                f"Passed: {stock['symbol']} | Score: {stock['score']:.2f} | Tags: {stock['tags']}"
            )

    except Exception as e:
        logger.error(f"[SCREENING ERROR] {e}")
        return

    logger.info("Stock Screening Phase completed successfully.")


if __name__ == "__main__":
    run()
