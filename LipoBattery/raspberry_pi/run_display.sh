#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/display_lipo.py" --port "${1:-/dev/ttyUSB0}" --baud "${2:-115200}"
