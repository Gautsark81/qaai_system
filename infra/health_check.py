import datetime
from data import ingestion
from infra import logging_utils

logger = logging_utils.get_logger("health_check")


def run_health_check():
    """
    Run a basic health check by fetching a small sample of data.
    Returns True if successful, False otherwise.
    """
    try:
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=5)).isoformat()
        end_date = today.isoformat()
        df = ingestion.fetch_data("RELIANCE", start_date, end_date)

        if df is not None and not df.empty:
            logger.info("Health check passed")
            return True
        else:
            logger.warning("Health check failed: DataFrame is empty")
            return False
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
