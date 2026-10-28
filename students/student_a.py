"""Student A - Asset Performance Index page. Only calls my FastAPI service (no model here)."""
import altair as alt
import pandas as pd
import requests
import streamlit as st

API_URL = "https://three6120-26sp-at3-group33-studenta-api-1.onrender.com"
TIMEOUT = 70   # free Render services can take ~50 s to wake up


@st.cache_data(ttl=600, show_spinner=False)
def _get(method, endpoint, payload=None):
    if method == "GET":
        resp = requests.get(API_URL + endpoint, timeout=TIMEOUT)
    else:
        resp = requests.post(API_URL + endpoint, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def call_api(method, endpoint, payload=None):
    """Returns the API's answer, or None if it can't be reached (the page doesn't crash)."""
    try:
        return _get(method, endpoint, payload)
    except Exception:
        return None


def show_chart(chart):
    """Full-width chart. Works on new and older Streamlit versions."""
    try:
        st.altair_chart(chart, width="stretch")
    except TypeError:
        st.altair_chart(chart, use_container_width=True)


def pct(value):
    return "n/a" if value is None else f"{value:.2%}"


def level(score):
    return "High" if score >= 70 else "Medium" if score >= 40 else "Low"


def home_chart(token):
    """Small visualisation for the home page: the predicted score on a 0-100 scale."""
    pred = call_api("POST", "/predict", {"token": token, "forecast_horizon": 7})
    if pred is None:
        st.info("Asset Performance service unavailable.")
        return
    score = pred["prediction"]
    bands = pd.DataFrame({"start": [0, 40, 70], "end": [40, 70, 100],
                          "band": ["Low", "Medium", "High"]})
    base = alt.Chart(bands).mark_bar(height=26).encode(
        x=alt.X("start:Q", scale=alt.Scale(domain=[0, 100]), title=None), x2="end:Q",
        color=alt.Color("band:N", scale=alt.Scale(domain=["Low", "Medium", "High"],
                                                    range=["#f3c9b8", "#e6e6e6", "#bcd7f5"]), legend=None))
    marker = alt.Chart(pd.DataFrame({"score": [score]})).mark_tick(color="#2a78d6", thickness=4, size=34).encode(x="score:Q")
    show_chart((base + marker).properties(height=60))
    st.caption(f"Predicted score {score:.1f} ({level(score)}) for {pred['prediction_date']}")


def render(token):
    st.header("📈 Asset Performance Index")
    st.caption("Student A · XGBoost · score predicted 7 days ahead")

    with st.spinner("Getting the prediction (can take up to a minute if the API is waking up)..."):
        pred = call_api("POST", "/predict", {"token": token, "forecast_horizon": 7})

    if pred is None:
        st.error("The prediction service is unavailable right now. Please try again later.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Performance Score (0-100)", f"{pred['prediction']:.1f}")
        col2.metric("Level", level(pred["prediction"]))
        col3.metric("Forecast for", pred["prediction_date"])
        st.caption(f"Based on market data up to {pred['as_of_date']} · source: {pred.get('data_source', '-')}")

    st.subheader("Student A features (latest completed day)")
    feats = call_api("POST", "/features", {"token": token})
    if feats is None:
        st.info("Features are unavailable right now.")
    else:
        f = feats.get("features", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Daily Return", pct(f.get("DailyReturn")))
        c2.metric("5-Day Return", pct(f.get("Return5")))
        c3.metric("20-Day Return", pct(f.get("Return20")))
        momentum = f.get("Momentum")
        c4.metric("Momentum (USD)", "n/a" if momentum is None else f"{momentum:,.4g}")
        st.caption(f"As of {feats.get('date', '-')} · source: {feats.get('source', '-')}")

    st.subheader("Feature importance")
    meta = call_api("GET", "/model-metadata")
    if meta is None:
        st.info("Feature importance is unavailable right now.")
    else:
        fi = meta.get("feature_importance") or {}
        importance = pd.DataFrame({"feature": [str(k) for k in fi],
                                   "importance": [float(v) for v in fi.values()]})
        chart = alt.Chart(importance).mark_bar(color="#2a78d6").encode(
            x=alt.X("importance:Q", title="share of importance"),
            y=alt.Y("feature:N", sort="-x", title=None),
            tooltip=["feature", alt.Tooltip("importance:Q", format=".2f")],
        )
        show_chart(chart)

    st.caption("This score is a guide, not financial advice.")