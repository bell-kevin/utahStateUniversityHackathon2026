#!/usr/bin/env python3
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    mode: str = os.getenv("MODE", "synthetic").lower()
    seed: int = int(os.getenv("SEED", "42"))
    days: int = int(os.getenv("DATA_DAYS", "120"))
    lat: float = float(os.getenv("OGDEN_LAT", "41.2230"))
    lon: float = float(os.getenv("OGDEN_LON", "-111.9738"))


def build_targets(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    precip_impact = np.clip(df["precip_mm"], 0, 6) * 7.5
    wind_impact = np.clip(df["wind_kph"] - 15, 0, 50) * 0.8
    temp_impact = np.clip(0 - df["temp_c"], 0, 20) * 1.1
    vis_impact = np.clip(100 - df["visibility_idx"], 0, 100) * 0.35
    traffic_impact = np.clip(df["traffic_index"] - 100, 0, 80) * 0.22

    risk_score = precip_impact + wind_impact + temp_impact + vis_impact + traffic_impact
    risk_score = np.clip(risk_score + rng.normal(0, 3, len(df)), 0, 100)

    slowdown_pct = (
        risk_score * 0.42
        + np.clip(df["hour"] - 15, 0, 8) * 1.4
        + np.clip(8 - df["hour"], 0, 6) * 0.8
    )
    slowdown_pct = np.clip(slowdown_pct + rng.normal(0, 2, len(df)), 0, 65)

    out = df.copy()
    out["risk_score"] = risk_score
    out["slowdown_pct"] = slowdown_pct
    return out


def synthetic_data(cfg: Config) -> pd.DataFrame:
    rng = np.random.default_rng(cfg.seed)
    total_hours = cfg.days * 24
    start = datetime.now(timezone.utc) - timedelta(hours=total_hours)
    ts = pd.date_range(start=start, periods=total_hours, freq="h", tz="UTC")

    day_of_year = ts.dayofyear.to_numpy()
    hour = ts.hour.to_numpy()

    base_temp = 2 + 12 * np.sin((day_of_year / 365) * 2 * np.pi)
    diurnal = 5 * np.sin(((hour - 8) / 24) * 2 * np.pi)
    storm_cycle = (np.sin(np.arange(total_hours) / 20) + 1) / 2

    temp_c = base_temp + diurnal + rng.normal(0, 2, total_hours)
    precip_mm = np.maximum(0, storm_cycle * rng.gamma(1.4, 1.8, total_hours) - 0.9)
    wind_kph = np.maximum(2, 9 + storm_cycle * 24 + rng.normal(0, 4, total_hours))
    visibility_idx = np.clip(98 - precip_mm * 13 - storm_cycle * 16 + rng.normal(0, 4, total_hours), 10, 100)

    weekend_boost = np.where(ts.dayofweek >= 5, 18, 0)
    commute_curve = np.exp(-((hour - 8) ** 2) / 18) * 24 + np.exp(-((hour - 17) ** 2) / 18) * 28
    ski_curve = np.exp(-((hour - 7) ** 2) / 10) * 34 + np.exp(-((hour - 16) ** 2) / 12) * 26
    weather_deterrent = np.clip(precip_mm * 4 + (35 - visibility_idx) * 0.7, 0, 25)
    traffic_index = 70 + weekend_boost + commute_curve + ski_curve - weather_deterrent + rng.normal(0, 5, total_hours)

    df = pd.DataFrame(
        {
            "timestamp": ts,
            "temp_c": temp_c,
            "wind_kph": wind_kph,
            "precip_mm": precip_mm,
            "visibility_idx": visibility_idx,
            "traffic_index": np.clip(traffic_index, 20, 180),
        }
    )
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    return build_targets(df, rng)


def real_data(cfg: Config) -> pd.DataFrame:
    end = datetime.now(timezone.utc).date() - timedelta(days=1)
    start = end - timedelta(days=cfg.days)

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={cfg.lat}&longitude={cfg.lon}&start_date={start}&end_date={end}"
        "&hourly=temperature_2m,precipitation,wind_speed_10m,cloud_cover"
        "&timezone=UTC"
    )
    response = requests.get(url, timeout=45)
    response.raise_for_status()
    payload = response.json()["hourly"]

    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(payload["time"], utc=True),
            "temp_c": payload["temperature_2m"],
            "wind_kph": payload["wind_speed_10m"],
            "precip_mm": payload["precipitation"],
            "cloud_cover": payload["cloud_cover"],
        }
    )
    df["visibility_idx"] = np.clip(100 - df["cloud_cover"] * 0.6 - df["precip_mm"] * 8, 10, 100)

    hour = df["timestamp"].dt.hour
    weekend_boost = np.where(df["timestamp"].dt.dayofweek >= 5, 16, 0)
    ski_curve = np.exp(-((hour - 7) ** 2) / 11) * 30 + np.exp(-((hour - 16) ** 2) / 12) * 24
    weather_deterrent = np.clip(df["precip_mm"] * 4 + (35 - df["visibility_idx"]) * 0.6, 0, 22)
    df["traffic_index"] = np.clip(75 + weekend_boost + ski_curve - weather_deterrent, 25, 170)
    df["hour"] = hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek

    return build_targets(df, np.random.default_rng(cfg.seed))


def main() -> None:
    cfg = Config()
    os.makedirs("data", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    if cfg.mode == "real":
        try:
            df = real_data(cfg)
            source = "real"
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Real data failed ({exc}). Falling back to synthetic mode.")
            df = synthetic_data(cfg)
            source = "synthetic_fallback"
    else:
        df = synthetic_data(cfg)
        source = "synthetic"

    df.to_csv("data/road_weather.csv", index=False)
    df.tail(200).to_csv("results/sample_data.csv", index=False)

    print(f"Saved {len(df):,} rows from mode={source} -> data/road_weather.csv")
    print("Saved quick sample -> results/sample_data.csv")


if __name__ == "__main__":
    main()
