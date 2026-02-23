"""
Backtest results export
"""

import logging
from pathlib import Path
from streamlit_app.utils import export_helpers, telegram_alerts

logger = logging.getLogger("backtest_results_export")
EXPORT_DIR = Path("exports/backtests")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_backtest_results_export(df, run_id="run"):
    try:
        fname = export_helpers.generate_export_filename(f"backtest_{run_id}")
        path = EXPORT_DIR / fname
        export_helpers.export_df_to_excel(df, path, index=False, sheet_name="backtest")
        telegram_alerts.send_telegram_alert(
            f"✅ Backtest results exported: `{path.name}`"
        )
        return f"✅ EXPORT_SUCCESS:{path.as_posix()}"
    except Exception as e:
        logger.exception("Backtest export failed")
        telegram_alerts.send_telegram_alert(f"❌ Backtest export failed: {e}")
        return f"❌ EXPORT_FAILED:{e}"
