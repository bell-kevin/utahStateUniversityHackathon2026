#!/usr/bin/env python3
"""Read LiPo telemetry from an Arduino Nano over serial and display on a Pi LCD."""

from __future__ import annotations

import argparse
import json
import queue
import threading
import time
import tkinter as tk
from dataclasses import dataclass

import serial


@dataclass
class BatterySample:
    voltage: float
    percent: float
    timestamp: float


class SerialReader(threading.Thread):
    def __init__(self, port: str, baud: int, out_queue: queue.Queue[BatterySample]) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.out_queue = out_queue
        self._stop = threading.Event()

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                with serial.Serial(self.port, self.baud, timeout=1) as ser:
                    while not self._stop.is_set():
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                            sample = BatterySample(
                                voltage=float(payload["voltage"]),
                                percent=float(payload["percent"]),
                                timestamp=time.time(),
                            )
                            self.out_queue.put(sample)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            except serial.SerialException:
                time.sleep(1.0)

    def stop(self) -> None:
        self._stop.set()


class BatteryDisplayApp:
    def __init__(self, port: str, baud: int, fullscreen: bool = True) -> None:
        self.root = tk.Tk()
        self.root.title("LiPo Battery Monitor")
        self.root.configure(bg="#111")
        self.root.attributes("-fullscreen", fullscreen)

        self.queue: queue.Queue[BatterySample] = queue.Queue()
        self.reader = SerialReader(port=port, baud=baud, out_queue=self.queue)
        self.latest: BatterySample | None = None

        self.title_label = tk.Label(
            self.root,
            text="LiPo Monitor",
            fg="#f5f5f5",
            bg="#111",
            font=("Helvetica", 34, "bold"),
        )
        self.title_label.pack(pady=(30, 10))

        self.voltage_label = tk.Label(
            self.root,
            text="Voltage: --.- V",
            fg="#9ad1ff",
            bg="#111",
            font=("Helvetica", 30),
        )
        self.voltage_label.pack(pady=10)

        self.percent_label = tk.Label(
            self.root,
            text="Charge: -- %",
            fg="#8ef58e",
            bg="#111",
            font=("Helvetica", 30),
        )
        self.percent_label.pack(pady=10)

        self.status_label = tk.Label(
            self.root,
            text="Waiting for serial data...",
            fg="#cccccc",
            bg="#111",
            font=("Helvetica", 18),
        )
        self.status_label.pack(pady=(20, 10))

        self.root.bind("<Escape>", self._on_escape)
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

    def _on_escape(self, _event: tk.Event) -> None:
        self.root.attributes("-fullscreen", False)

    def _refresh_ui(self) -> None:
        while not self.queue.empty():
            self.latest = self.queue.get_nowait()

        if self.latest:
            age = time.time() - self.latest.timestamp
            self.voltage_label.config(text=f"Voltage: {self.latest.voltage:.3f} V")
            self.percent_label.config(text=f"Charge: {self.latest.percent:.1f} %")
            self.status_label.config(text=f"Last update: {age:.1f}s ago")

            if self.latest.percent <= 15:
                self.percent_label.config(fg="#ff6b6b")
            elif self.latest.percent <= 40:
                self.percent_label.config(fg="#ffd166")
            else:
                self.percent_label.config(fg="#8ef58e")

        self.root.after(100, self._refresh_ui)

    def start(self) -> None:
        self.reader.start()
        self._refresh_ui()
        self.root.mainloop()

    def shutdown(self) -> None:
        self.reader.stop()
        self.root.destroy()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Display LiPo battery data from Arduino on Raspberry Pi LCD")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port connected to Arduino Nano")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    parser.add_argument("--windowed", action="store_true", help="Run in windowed mode instead of fullscreen")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = BatteryDisplayApp(port=args.port, baud=args.baud, fullscreen=not args.windowed)
    app.start()
