#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8501")


def main() -> None:
    cmd = [
        "streamlit",
        "run",
        "app/app.py",
        "--server.address",
        HOST,
        "--server.port",
        PORT,
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
