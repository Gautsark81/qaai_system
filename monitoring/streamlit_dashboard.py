import streamlit as st
from pathlib import Path

st.title("Next-Gen Trading Dashboard")
log_path = st.text_input("Runtime log path", "runtime.log")
if st.button("Refresh"):
    pass

p = Path(log_path)
if p.exists():
    lines = p.read_text(encoding="utf-8").splitlines()[-1000:]
    st.code("\n".join(lines))
else:
    st.info("Log file not found. Start the algo to generate logs.")
