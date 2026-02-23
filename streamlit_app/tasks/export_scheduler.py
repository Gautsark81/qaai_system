# streamlit_app/tasks/export_scheduler.py
from __future__ import annotations
from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# import helper run_overlay_export
try:
    from streamlit_app.utils.export_helpers import (
        run_overlay_export as helper_run_overlay_export,
        load_overlay_source,
        export_df_to_excel,
        generate_export_filename,
        SUCCESS_PREFIX,
        FAIL_PREFIX,
    )
except Exception:
    helper_run_overlay_export = None
    load_overlay_source = None
    export_df_to_excel = None
    generate_export_filename = None
    SUCCESS_PREFIX = "EXPORT_SUCCESS"
    FAIL_PREFIX = "EXPORT_FAIL"


def run_overlay_export_scheduler() -> str:
    logger.info("Starting scheduled overlay export (scheduler).")
    try:
        if load_overlay_source is not None:
            df = load_overlay_source(Path.cwd() / "overlay.csv")
        else:
            df = pd.DataFrame()

        if df.empty:
            raise RuntimeError("Source overlay data is empty or unavailable.")

        if generate_export_filename is not None:
            export_file = generate_export_filename(None, out_dir=Path.cwd() / "exports")
        else:
            export_file = Path.cwd() / "exports" / "overlay_fallback.xlsx"

        export_file.parent.mkdir(parents=True, exist_ok=True)

        if export_df_to_excel is not None:
            export_df_to_excel(df, export_file)
        else:
            with pd.ExcelWriter(export_file, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="overlay", index=False)

        return f"{SUCCESS_PREFIX}: {export_file.as_posix()}"
    except Exception as exc:
        logger.exception("Scheduled overlay export failed.")
        return f"{FAIL_PREFIX}: {exc}"


def run_overlay_export(*args, **kwargs):
    if args or kwargs:
        try:
            return helper_run_overlay_export(*args, **kwargs)
        except Exception:
            logger.exception(
                "Failed to delegate to helper run_overlay_export; falling back to scheduler."
            )
            return run_overlay_export_scheduler()
    else:
        return run_overlay_export_scheduler()
