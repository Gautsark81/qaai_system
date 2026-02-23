"""
Watchlist export helper
"""

import logging
from pathlib import Path
from streamlit_app.utils import export_helpers, telegram_alerts

logger = logging.getLogger("watchlist_export")
EXPORT_DIR = Path("exports/watchlist")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_watchlist_export(df):
    try:
        fname = export_helpers.generate_export_filename("watchlist")
        path = EXPORT_DIR / fname
        export_helpers.export_df_to_excel(df, path, index=False, sheet_name="watchlist")
        telegram_alerts.send_telegram_alert(f"✅ Watchlist exported: `{path.name}`")
        return f"✅ EXPORT_SUCCESS:{path.as_posix()}"
    except Exception as e:
        logger.exception("Watchlist export failed")
        telegram_alerts.send_telegram_alert(f"❌ Watchlist export failed: {e}")
        return f"❌ EXPORT_FAILED:{e}"
