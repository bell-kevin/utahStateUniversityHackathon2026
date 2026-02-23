from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import xgboost as xgb

FEATURES = [
    "temp_c",
    "wind_kph",
    "precip_mm",
    "visibility_idx",
    "traffic_index",
    "hour",
    "dayofweek",
]

ROUTE_FACTORS = {
    "Ogden → Snowbasin": 1.00,
    "Ogden → Trappers Loop": 1.12,
    "Ogden → Pineview": 0.94,
}

st.set_page_config(page_title="A100 Utah Snow Risk Forecaster", layout="wide")


@st.cache_resource
def load_models():
    risk = xgb.XGBRegressor()
    risk.load_model("models/xgb_risk.json")
    slow = xgb.XGBRegressor()
    slow.load_model("models/xgb_slowdown.json")
    return risk, slow


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("data/road_weather.csv", parse_dates=["timestamp"]).sort_values("timestamp")


def horizon_rows(base_row: pd.Series, horizon: int, route_mult: float) -> pd.DataFrame:
    rows = []
    for h in range(1, horizon + 1):
        row = base_row.copy()
        row["hour"] = int((int(row["hour"]) + h) % 24)
        rush = 8 <= row["hour"] <= 10 or 15 <= row["hour"] <= 18
        row["traffic_index"] = float(np.clip(row["traffic_index"] * (1.03 if rush else 0.98), 20, 190))
        row["precip_mm"] = float(np.clip(row["precip_mm"] * (1.04 + 0.01 * h), 0, 12))
        row["visibility_idx"] = float(np.clip(row["visibility_idx"] - 0.6 * h, 5, 100))
        row["wind_kph"] = float(np.clip(row["wind_kph"] * (1.01 + h * 0.004), 2, 90))
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame["traffic_index"] = frame["traffic_index"] * route_mult
    return frame


def main() -> None:
    st.title("🚦 GPU-First Utah Snow Road & Weather Risk Forecaster")
    st.caption("XGBoost on NVIDIA A100 • CPU vs GPU benchmark • synthetic/real data pipeline")

    if not Path("models/xgb_risk.json").exists():
        st.error("No trained model found. Run: make data && make train && make bench")
        return

    risk_model, slow_model = load_models()
    df = load_data()
    latest = df.iloc[-1]

    tab_dashboard, tab_benchmark, tab_data = st.tabs(["Forecast Dashboard", "Benchmark", "Data Preview"])

    with tab_dashboard:
        c1, c2, c3 = st.columns(3)
        route = c1.selectbox("Route", list(ROUTE_FACTORS.keys()))
        horizon = c2.slider("Forecast horizon (hours)", 1, 6, 3)
        storm_boost = c3.slider("Storm intensity multiplier", 0.8, 1.5, 1.0, 0.05)

        rows = horizon_rows(latest, horizon, ROUTE_FACTORS[route])
        rows["precip_mm"] *= storm_boost
        rows["visibility_idx"] = np.clip(rows["visibility_idx"] / storm_boost, 5, 100)

        pred_risk = np.clip(risk_model.predict(rows[FEATURES]), 0, 100)
        pred_slow = np.clip(slow_model.predict(rows[FEATURES]), 0, 80)

        rows = rows.copy()
        rows["risk_score_pred"] = pred_risk
        rows["slowdown_pct_pred"] = pred_slow
        rows["horizon_hr"] = np.arange(1, horizon + 1)

        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Risk Score", f"{rows['risk_score_pred'].mean():.1f} / 100")
        m2.metric("Avg Slowdown", f"{rows['slowdown_pct_pred'].mean():.1f}%")
        m3.metric("Worst Hour", f"+{int(rows.iloc[rows['risk_score_pred'].idxmax()]['horizon_hr'])}h")

        fig = px.line(
            rows,
            x="horizon_hr",
            y=["risk_score_pred", "slowdown_pct_pred"],
            markers=True,
            title=f"{route} Forecast (next {horizon}h)",
        )
        st.plotly_chart(fig, use_container_width=True)

        imp_path = Path("results/feature_importance.csv")
        if imp_path.exists():
            imp = pd.read_csv(imp_path)
            fig_imp = px.bar(imp, x="importance", y="feature", orientation="h", title="Risk Model Feature Importance")
            st.plotly_chart(fig_imp, use_container_width=True)

    with tab_benchmark:
        st.subheader("CPU vs GPU (A100) Speed Comparison")
        bench_md = Path("results/benchmark.md")
        if bench_md.exists():
            st.markdown(bench_md.read_text(encoding="utf-8"))
        else:
            st.warning("No benchmark found yet. Run: make bench")

        st.code("watch -n 0.5 nvidia-smi", language="bash")
        st.info("Run the command above in a second SSH terminal while retraining to show live GPU utilization.")

    with tab_data:
        st.subheader("Latest rows")
        st.dataframe(df.tail(20), use_container_width=True)

        metrics_path = Path("models/metrics.json")
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            st.json(metrics)


if __name__ == "__main__":
    main()
