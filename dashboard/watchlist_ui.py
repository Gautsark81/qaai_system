# File: dashboard/watchlist_ui.py

import streamlit as st
from infra.db_client import DBClient
import pandas as pd

st.set_page_config(page_title="QAAI Watchlist Manager", layout="wide")

st.title("📊 QAAI Watchlist Manager")

db = DBClient()

# View Current Watchlist
st.subheader("🔍 Current Watchlist")
query = "SELECT id, symbol, active FROM watchlist ORDER BY id;"
with db.conn.cursor() as cur:
    cur.execute(query)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "Symbol", "Active"])
    st.dataframe(df, use_container_width=True)

# Add new symbol
st.subheader("➕ Add New Symbol")
new_symbol = st.text_input("Symbol", max_chars=10)
if st.button("Add to Watchlist"):
    if new_symbol:
        with db.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO watchlist (symbol, active) VALUES (%s, TRUE) ON CONFLICT (symbol) DO NOTHING;",
                (new_symbol.upper(),),
            )
            db.conn.commit()
        st.success(f"{new_symbol.upper()} added to watchlist.")
        st.experimental_rerun()

# Deactivate symbol
st.subheader("🚫 Deactivate Symbol")
deactivate_id = st.selectbox(
    "Select Symbol ID to deactivate", df[df["Active"] == True]["ID"]
)
if st.button("Deactivate"):
    with db.conn.cursor() as cur:
        cur.execute(
            "UPDATE watchlist SET active = FALSE WHERE id = %s;", (deactivate_id,)
        )
        db.conn.commit()
    st.success(f"Symbol with ID {deactivate_id} deactivated.")
    st.experimental_rerun()
