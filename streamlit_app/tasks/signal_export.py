"""
Signal export (watchlist/signals)
"""

import logging
from pathlib import Path
from streamlit_app.utils import export_helpers, telegram_alerts

logger = logging.getLogger("signal_export")
EXPORT_DIR = Path("exports/signals")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_signal_export(df, prefix="signal_export"):
    try:
        fname = export_helpers.generate_export_filename(prefix)
        path = EXPORT_DIR / fname
        export_helpers.export_df_to_excel(df, path, index=False, sheet_name="signals")
        telegram_alerts.send_telegram_alert(f"✅ Signal export: `{path.name}`")
        return f"✅ EXPORT_SUCCESS:{path.as_posix()}"
    except Exception as e:
        logger.exception("Signal export failed")
        telegram_alerts.send_telegram_alert(f"❌ Signal export failed: {e}")
        return f"❌ EXPORT_FAILED:{e}"
