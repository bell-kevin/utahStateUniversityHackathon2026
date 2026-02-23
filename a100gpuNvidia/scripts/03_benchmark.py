#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time

import pandas as pd
import xgboost as xgb

FEATURES = ["temp_c", "wind_kph", "precip_mm", "visibility_idx", "traffic_index", "hour", "dayofweek"]


def train_once(X_train, y_train, X_val, y_val, device: str) -> tuple[float, xgb.XGBRegressor, str]:
    model = xgb.XGBRegressor(
        n_estimators=350,
        max_depth=7,
        learning_rate=0.06,
        subsample=0.9,
        colsample_bytree=0.9,
        tree_method="hist",
        device=device,
        random_state=42,
        eval_metric="mae",
        early_stopping_rounds=25,
    )
    start = time.perf_counter()
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    duration = time.perf_counter() - start
    cfg = json.loads(model.get_booster().save_config())
    actual = cfg["learner"]["generic_param"].get("device", "unknown")
    return duration, model, actual


def infer_throughput(model: xgb.XGBRegressor, X: pd.DataFrame) -> float:
    batch = pd.concat([X] * 50, ignore_index=True)
    start = time.perf_counter()
    _ = model.predict(batch)
    elapsed = time.perf_counter() - start
    return float(len(batch) / max(elapsed, 1e-9))


def main() -> None:
    os.makedirs("results", exist_ok=True)
    df = pd.read_csv("data/road_weather.csv").reset_index(drop=True)
    split_idx = int(len(df) * 0.8)
    train_df, val_df = df.iloc[:split_idx], df.iloc[split_idx:]
    X_train, X_val = train_df[FEATURES], val_df[FEATURES]
    y_train, y_val = train_df["risk_score"], val_df["risk_score"]

    results: list[dict] = []

    cpu_time, cpu_model, _ = train_once(X_train, y_train, X_val, y_val, "cpu")
    results.append({"mode": "CPU", "train_seconds": round(cpu_time, 3), "inference_rows_per_sec": round(infer_throughput(cpu_model, X_val), 1)})

    try:
        gpu_time, gpu_model, actual = train_once(X_train, y_train, X_val, y_val, "cuda")
        entry = {
            "mode": "GPU (A100)",
            "train_seconds": round(gpu_time, 3),
            "inference_rows_per_sec": round(infer_throughput(gpu_model, X_val), 1),
        }
        if actual != "cuda":
            entry["note"] = f"Requested CUDA but actual device was {actual}."
        results.append(entry)
    except xgb.core.XGBoostError as exc:
        results.append({"mode": "GPU (A100)", "train_seconds": None, "inference_rows_per_sec": None, "note": f"GPU unavailable: {exc}"})

    pd.DataFrame(results).to_csv("results/benchmark.csv", index=False)

    md_lines = ["# CPU vs GPU Benchmark", "", "| Mode | Train Seconds | Inference Rows/sec | Note |", "|---|---:|---:|---|"]
    for row in results:
        md_lines.append(f"| {row['mode']} | {row.get('train_seconds', 'n/a')} | {row.get('inference_rows_per_sec', 'n/a')} | {row.get('note', '')} |")
    md_lines += ["", "Run live utilization while training:", "```bash", "watch -n 0.5 nvidia-smi", "```"]

    with open("results/benchmark.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    with open("results/benchmark.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Wrote results/benchmark.md and results/benchmark.csv")


if __name__ == "__main__":
    main()
