"""Student A (Group 33) - Asset Performance Index app.

Uses the same page file as the group app (students/student_a.py), so both apps show the same thing.
All predictions come from the Student A FastAPI service on Render - no model runs here.
Run locally: streamlit run streamlit_app.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))   # so "students" can be imported

st.set_page_config(page_title="Asset Performance Index | Group 33", page_icon="📈", layout="wide")

from students import student_a  # noqa: E402

TOKENS = {"BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple", "SOL": "Solana",
          "DOGE": "Dogecoin", "XLM": "Stellar", "TRX": "Tron", "XMR": "Monero"}

with st.sidebar:
    token = st.selectbox("Cryptocurrency", list(TOKENS), format_func=lambda t: f"{TOKENS[t]} ({t})")
    st.caption("Predictions come from the Student A FastAPI service on Render. "
               "The first load can take up to a minute while the service wakes up.")

st.title("Crypto Financial Intelligence Platform")
st.caption("Group 33 · Student A: Harsh Javia (26138800)")

home, page = st.tabs(["🏠 Home", "📈 Asset Performance Index"])

with home:
    st.subheader(f"Snapshot: {TOKENS[token]} ({token})")
    try:
        student_a.home_chart(token)
    except Exception as error:   # never let one section break the app
        st.warning(f"Visualisation unavailable ({type(error).__name__}).")

with page:
    try:
        student_a.render(token)
    except Exception as error:
        st.error(f"This page hit an unexpected error ({type(error).__name__}). Please try again.")
