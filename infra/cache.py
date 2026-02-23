from data import ingestion, cleaner, schema_validator
from infra import config_loader, logging_utils, health_check
from infra.dhan_client import DhanClient

logger = logging_utils.get_logger("phase1")


def run():
    logger.info("Phase 1: Full Run Starting...")

    dhan_client = DhanClient()

    try:
        df = ingestion.fetch_data(
            symbol="RELIANCE",
            start_date="2025-07-01",
            end_date="2025-07-31",
            dhan_client=dhan_client,
        )
        logger.info(f"Fetched data shape: {df.shape}")
    except Exception as e:
        logger.error(f"[INGESTION FAILED] Error while fetching data: {e}")
        return

    try:
        missing, extra = schema_validator.validate_schema(
            df, ["open", "high", "low", "close", "volume"]
        )
        if missing or extra:
            logger.warning(f"[SCHEMA WARNING] Missing: {missing}, Extra: {extra}")
        else:
            logger.info("Schema validated successfully.")
    except Exception as e:
        logger.error(f"[SCHEMA ERROR] Validation failed: {e}")
        return

    try:
        df = cleaner.clean_data(df)
        logger.info(f"Cleaned data shape: {df.shape}")
    except Exception as e:
        logger.error(f"[CLEANING FAILED] Error during cleaning: {e}")
        return

    try:
        config = config_loader.load_config()
        logger.info(f"Loaded config: {config}")
    except Exception as e:
        logger.error(f"[CONFIG ERROR] Failed to load config: {e}")
        return

    try:
        healthy = health_check.run_health_check()
        if healthy:
            logger.info("Health check passed")
        else:
            logger.warning("Health check failed.")
    except Exception as e:
        logger.error(f"[HEALTH CHECK ERROR] {e}")
        return

    logger.info("Phase 1: Run Completed Successfully.")


if __name__ == "__main__":
    run()
