"""
Trade audit export — uses export_helpers to write Excel safe of timestamps (IST)
"""

import logging
from pathlib import Path
from streamlit_app.utils import export_helpers, telegram_alerts
import pandas as pd

logger = logging.getLogger("trade_audit_export")
EXPORT_DIR = Path("exports/trade_audit")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_trade_audit_export(df: pd.DataFrame) -> str:
    try:
        file_name = export_helpers.generate_export_filename("trade_audit")
        file_path = EXPORT_DIR / file_name
        export_helpers.export_df_to_excel(
            df, file_path, index=False, sheet_name="audit"
        )
        telegram_alerts.send_telegram_alert(
            f"✅ Trade audit exported: `{file_path.name}`"
        )
        return f"✅ EXPORT_SUCCESS:{file_path.as_posix()}"
    except Exception as e:
        logger.exception("Trade audit export failed")
        telegram_alerts.send_telegram_alert(f"❌ Trade audit export failed: {e}")
        return f"❌ EXPORT_FAILED:{e}"
