PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: setup check-gpu data train bench run clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

check-gpu:
	bash scripts/00_check_gpu.sh

data:
	$(PY) scripts/01_get_data.py

train:
	$(PY) scripts/02_train.py

bench:
	$(PY) scripts/03_benchmark.py

run:
	$(PY) scripts/04_serve.py

clean:
	rm -rf $(VENV)
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
