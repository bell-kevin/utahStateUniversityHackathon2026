# A100 GPU-First Utah Snow Road & Weather Risk Forecaster

A solo hackathon project that proves **NVIDIA A100-SXM4-40GB** value with an end-to-end ML workflow:

1. data ingest (real weather with synthetic fallback),
2. preprocessing + feature engineering,
3. GPU model training (XGBoost on CUDA),
4. CPU vs GPU benchmark,
5. interactive Streamlit dashboard over SSH tunnel.

---

## Why this project
Winter mountain routes can change quickly. This demo forecasts for ski-bound roads (e.g., Ogden → Snowbasin / Trappers Loop):
- **Road Risk Score** (0–100)
- **Expected Travel Slowdown** (%)
for the next **1–6 hours**.

The app is designed for headless Ubuntu GPU servers and hackathon judging.

---

## Project tree

```text
a100gpuNvidia/
├── .env.example
├── .gitignore
├── Makefile
├── README.md
├── requirements.txt
├── app/
│   └── app.py
├── data/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── results/
│   └── .gitkeep
└── scripts/
    ├── 00_check_gpu.sh
    ├── 01_get_data.py
    ├── 02_train.py
    ├── 03_benchmark.py
    └── 04_serve.py
```

---

## Quickstart (one-command flow)

From this folder:

```bash
cd a100gpuNvidia
cp .env.example .env
make setup
make check-gpu
make data
make train
make bench
make run
```

Then open the app via tunnel (`http://localhost:8501`) from your laptop.

---

## SSH tunnel (laptop -> GPU server)

```bash
ssh -L 8501:localhost:8501 student@kbusu.users.weber.edu
```

In the SSH session, run:

```bash
cd /workspace/utahStateUniversityHackathon2026/a100gpuNvidia
make run
```

On laptop browser:

```text
http://localhost:8501
```

---

## Data mode: real or synthetic

Set in `.env`:

```bash
MODE=real
# or
MODE=synthetic
```

- `MODE=real`: fetches historical weather from Open-Meteo (no API key).
- If fetch fails, pipeline auto-falls back to synthetic data.
- `MODE=synthetic`: always generate realistic correlated weather + traffic signals.

Dataset stays small and local (<200MB).

---

## GPU proof checklist

### Shell checks

```bash
bash scripts/00_check_gpu.sh
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no-gpu')"
python -c "import xgboost as xgb; print(xgb.__version__)"
```

### During training

In a second terminal:

```bash
watch -n 0.5 nvidia-smi
```

### Benchmark output

`make bench` writes:
- `results/benchmark.md`
- `results/benchmark.csv`

with CPU vs GPU train speed and inference throughput.

---

## App features

- **Forecast Dashboard**
  - select route
  - select 1–6h horizon
  - storm intensity slider
  - predicted risk and slowdown
  - feature importance chart
- **Benchmark tab**
  - renders markdown speed table
  - includes live `nvidia-smi` instructions
- **Data Preview tab**
  - recent rows
  - model metrics JSON

---

## HackUSU pitch blurb

**Problem:** Utah mountain commutes can become dangerous quickly due to weather and congestion.

**Approach:** Build a GPU-first risk forecasting pipeline that combines weather + traffic-like features and predicts route risk and slowdown in near real time.

**Why GPU matters:** The A100 significantly accelerates boosting model training and allows rapid iteration for nowcasting and frequent retrains.

**What’s next:** Add UDOT road condition feeds, camera-based visibility signals, geospatial route graph modeling, and alert notifications.

**Track fit:** AI/ML + Cloud/Infrastructure + Community impact (safer winter mobility).

---

## 2-minute Judge Demo Script

1. **(0:00–0:20)** “This app forecasts winter road risk and travel slowdown for ski routes out of Ogden in the next 1–6 hours.”
2. **(0:20–0:40)** Show terminal running `watch -n 0.5 nvidia-smi`; in another tab run `make train` and point to GPU utilization.
3. **(0:40–1:10)** Open dashboard, switch route to *Trappers Loop*, set horizon to 6h, increase storm slider, explain risk/slowdown changes.
4. **(1:10–1:35)** Open **Benchmark** tab and show CPU vs GPU table from `results/benchmark.md`.
5. **(1:35–2:00)** Close with: “This is fully self-hosted on the remote A100 box, no paid APIs required, and supports real or synthetic mode for reliability under hackathon constraints.”

---

## Submission-ready “What we built” (5 bullets)

- Built an end-to-end, GPU-first ML pipeline for Utah winter road risk forecasting.
- Implemented robust data ingestion with real-weather mode and synthetic fallback.
- Trained dual XGBoost regressors (risk + slowdown) with CUDA acceleration on A100.
- Added CPU vs GPU benchmarking outputs and live GPU-utilization demo instructions.
- Delivered an interactive Streamlit dashboard accessible through SSH port forwarding.

---

## Screenshot placeholders

- `docs/screenshot_dashboard.png`
- `docs/screenshot_benchmark.png`

(Replace with actual screenshots taken on the GPU server demo environment.)
