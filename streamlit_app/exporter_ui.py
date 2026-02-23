# streamlit_apps/exporter_ui.py
import streamlit as st
from pathlib import Path
import pandas as pd
import time
from ml import export_preds_to_parquet as exporter

st.set_page_config(page_title="Export Predictions", layout="centered")
st.title("ML Predictions Exporter — One click")

db_path = st.text_input("SQLite DB path", value=str(exporter.DEFAULT_DB))
out_path = st.text_input("Output directory", value=str(exporter.DEFAULT_OUT))

col1, col2 = st.columns(2)
with col1:
    archive = st.checkbox("Archive exported rows", value=False)
    delete = st.checkbox("Delete exported rows (irreversible)", value=False)
with col2:
    update_marker = st.checkbox("Update last_export_ts marker after export", value=True)
    force = st.checkbox("Force export (ignore marker)", value=False)

compression = st.selectbox(
    "Parquet compression", options=[None, "snappy", "gzip", "brotli", "lz4"], index=0
)

since = st.text_input("Since (YYYY-MM-DD or ISO) — leave blank to use marker", value="")

run = st.button("Run export now")

if run:
    st.info("Starting export...")
    try:
        start = time.time()
        written_files, rows = exporter.do_export(
            db_path=Path(db_path),
            out_dir=Path(out_path),
            since=since or None,
            archive=archive,
            delete=delete,
            update_marker=update_marker,
            force=force,
            compression=compression,
            verbose=True,
        )
        elapsed = time.time() - start
        st.success(
            f"Export finished — wrote {len(written_files)} partition files, {rows} rows (elapsed {elapsed:.2f}s)"
        )
        if written_files:
            st.write("Files written:")
            for p in written_files:
                st.write(f"- {p}")
            # show preview of first parquet if possible
            first = written_files[0]
            try:
                df = pd.read_parquet(first)
                st.write("Preview:", df.head())
            except Exception as e:
                st.warning(f"Unable to preview {first}: {e}")
        marker = exporter.read_last_export_ts(Path(db_path))
        st.write("Current marker (last_export_ts):", marker)
    except Exception as exc:
        st.error(f"Export failed: {exc}")
        raise
