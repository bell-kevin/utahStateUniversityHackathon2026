#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import xgboost as xgb
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, r2_score

load_dotenv()

FEATURES = ["temp_c", "wind_kph", "precip_mm", "visibility_idx", "traffic_index", "hour", "dayofweek"]


@dataclass
class Config:
    seed: int = int(os.getenv("SEED", "42"))
    device: str = os.getenv("XGB_DEVICE", "cuda")


def fit_one(X_train, y_train, X_val, y_val, device: str, seed: int) -> xgb.XGBRegressor:
    model = xgb.XGBRegressor(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=seed,
        tree_method="hist",
        device=device,
        eval_metric="mae",
        early_stopping_rounds=30,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    return model


def model_device(model: xgb.XGBRegressor) -> str:
    cfg = json.loads(model.get_booster().save_config())
    return cfg["learner"]["generic_param"].get("device", "unknown")


def main() -> None:
    cfg = Config()
    os.makedirs("models", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    df = pd.read_csv("data/road_weather.csv", parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    split_idx = int(len(df) * 0.8)
    train_df, val_df = df.iloc[:split_idx], df.iloc[split_idx:]

    X_train, X_val = train_df[FEATURES], val_df[FEATURES]
    y_train_risk, y_val_risk = train_df["risk_score"], val_df["risk_score"]
    y_train_slow, y_val_slow = train_df["slowdown_pct"], val_df["slowdown_pct"]

    start = time.perf_counter()
    try:
        risk_model = fit_one(X_train, y_train_risk, X_val, y_val_risk, cfg.device, cfg.seed)
        slow_model = fit_one(X_train, y_train_slow, X_val, y_val_slow, cfg.device, cfg.seed)
    except xgb.core.XGBoostError as exc:
        print(f"[WARN] Requested device={cfg.device} failed ({exc}); retrying on CPU")
        risk_model = fit_one(X_train, y_train_risk, X_val, y_val_risk, "cpu", cfg.seed)
        slow_model = fit_one(X_train, y_train_slow, X_val, y_val_slow, "cpu", cfg.seed)
    train_s = time.perf_counter() - start

    actual_device = model_device(risk_model)

    risk_pred = np.clip(risk_model.predict(X_val), 0, 100)
    slow_pred = np.clip(slow_model.predict(X_val), 0, 80)

    metrics = {
        "requested_device": cfg.device,
        "actual_device": actual_device,
        "rows": int(len(df)),
        "risk_mae": float(mean_absolute_error(y_val_risk, risk_pred)),
        "risk_r2": float(r2_score(y_val_risk, risk_pred)),
        "slowdown_mae": float(mean_absolute_error(y_val_slow, slow_pred)),
        "slowdown_r2": float(r2_score(y_val_slow, slow_pred)),
        "train_seconds": float(train_s),
        "features": FEATURES,
    }

    risk_model.save_model("models/xgb_risk.json")
    slow_model.save_model("models/xgb_slowdown.json")

    pd.DataFrame({"feature": FEATURES, "importance": risk_model.feature_importances_}).sort_values(
        "importance", ascending=False
    ).to_csv("results/feature_importance.csv", index=False)

    with open("models/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))
    print("Saved models and metrics.")


if __name__ == "__main__":
    main()
