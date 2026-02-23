# streamlit_app/state.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from modules.signal_engine import SignalEngine


@st.cache_resource
def get_engine():
    return SignalEngine()
