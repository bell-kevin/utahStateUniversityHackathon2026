#!/usr/bin/env bash
set -euo pipefail

echo "== NVIDIA SMI =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not found. Install NVIDIA drivers/CUDA runtime."
fi

echo
echo "== Python GPU checks =="
python3 - <<'PY'
try:
    import torch
    print("torch.cuda.is_available():", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("torch device:", torch.cuda.get_device_name(0))
except Exception as e:
    print("Torch check skipped:", e)

try:
    import xgboost as xgb
    print("xgboost version:", xgb.__version__)
except Exception as e:
    print("XGBoost check skipped:", e)
PY
