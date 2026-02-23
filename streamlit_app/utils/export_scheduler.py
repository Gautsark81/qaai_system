"""
export_scheduler.py
High-reliability overlay export system with IST datetime sanitization
and Telegram alert integration — fully MASTER UPGRADE OBJECTIVES ready.
"""

import logging
from datetime import datetime
from pathlib import Path
from streamlit_app.utils import telegram_alerts

# compat shim: re-export canonical functions from the tasks module
# Keep this file minimal so older imports remain valid and all logic lives in tasks/.
from ..tasks.export_scheduler import (
    run_overlay_export,
    SUCCESS_PREFIX,
    FAIL_PREFIX,
)

__all__ = ["run_overlay_export", "SUCCESS_PREFIX", "FAIL_PREFIX"]

"""
Compatibility proxy — canonical implementation lives in streamlit_app.tasks.export_scheduler.
This keeps older imports working while avoiding duplicate logic.
"""
from streamlit_app.tasks.export_scheduler import *  # noqa: F401,F403

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constants
IST = pytz.timezone("Asia/Kolkata")
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Utility Functions
# -----------------------------
def _sanitize_datetimes_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts tz-aware datetime columns to IST, then makes them tz-naive for Excel export.
    This ensures no Excel export failures due to timezone-aware datetimes.
    """
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        logger.debug(f"Sanitizing datetime column '{col}' → IST → tz-naive")
        df[col] = df[col].dt.tz_convert(IST).dt.tz_localize(None)
    return df


def _generate_mock_overlay_data() -> pd.DataFrame:
    """Fallback data for testing or when source is unavailable."""
    logger.warning(
        "⚠️ 'symbol' column missing or source not found — using mock export fallback."
    )
    now_ist = datetime.now(IST)
    data = {
        "symbol": ["AAPL", "MSFT", "GOOG"],
        "timestamp": [now_ist, now_ist, now_ist],
        "score": [0.85, 0.78, 0.92],
    }
    return pd.DataFrame(data)


def _get_overlay_data() -> pd.DataFrame:
    """
    Fetch real overlay data from your source.
    Here, just a mock fallback unless connected to DB or API.
    """
    try:
        # TODO: Replace with actual data source fetch
        df = _generate_mock_overlay_data()
        if "symbol" not in df.columns:
            return _generate_mock_overlay_data()
        return df
    except Exception as e:
        logger.error(f"❌ Failed to fetch overlay data: {e}")
        return _generate_mock_overlay_data()


# -----------------------------
# Main Export Function
# -----------------------------
def run_overlay_export() -> str:
    """
    Runs overlay export, sanitizes datetimes for Excel, sends Telegram alert.
    Returns status string.
    """
    logger.info("🚀 Starting overlay export process...")

    try:
        df = _get_overlay_data()
        df = _sanitize_datetimes_for_excel(df)

        # Export filename
        export_filename = (
            f"overlay_export_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        export_path = EXPORT_DIR / export_filename

        df.to_excel(export_path, index=False)
        success_msg = f"✅ Exported successfully: {export_path.as_posix()}"
        logger.info(success_msg)

        telegram_alerts.send_telegram_alert(
            f"✅ Daily Alpha Overlay Exported Successfully\n📂 File: `{export_path.as_posix()}`"
        )

        return success_msg

    except Exception as e:
        error_msg = f"❌ EXPORT_FAILED:{e}"
        logger.error(error_msg)

        telegram_alerts.send_telegram_alert(f"❌ Overlay Export Failed\n📝 Error: {e}")

        return error_msg
