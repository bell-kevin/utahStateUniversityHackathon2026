# LiPo Battery Monitor (Arduino Nano + Raspberry Pi + 5" LCD)

This project reads a LiPo battery voltage on an **Arduino Nano** and sends live telemetry to a **Raspberry Pi** over USB serial. The Pi then shows the voltage/percentage on a 5" LCD.

## What is included

- **C++ (Arduino)**: battery reader firmware (`arduino_nano/lipo_reader.ino`)
- **Python (Raspberry Pi)**: full-screen display app (`raspberry_pi/display_lipo.py`)
- Helper script and Python dependency file for easy startup

## Architecture

1. LiPo battery voltage is measured by the Arduino through a resistor divider.
2. Arduino streams JSON lines such as:
   ```json
   {"voltage":4.012,"percent":81.2}
   ```
3. Raspberry Pi reads serial data and renders it on the LCD.

## Hardware notes (important)

- A 1S LiPo can go up to ~4.2V. Protect Nano analog input with a voltage divider.
- Default firmware constants assume:
  - `R1 = 10k` from battery+ to A0
  - `R2 = 20k` from A0 to GND
- This gives `Vpin = Vbattery * (R2 / (R1 + R2)) = 2/3 * Vbattery`.

## Folder layout

```text
LipoBattery/
├── README.md
├── arduino_nano/
│   └── lipo_reader.ino
└── raspberry_pi/
    ├── display_lipo.py
    ├── requirements.txt
    └── run_display.sh
```

## 1) Flash Arduino Nano firmware

1. Open `arduino_nano/lipo_reader.ino` in Arduino IDE.
2. Select board: **Arduino Nano**.
3. Choose the correct processor/port.
4. Upload.

### Firmware behavior

- Samples A0 every 500ms
- Computes battery voltage using resistor-divider math
- Estimates battery percentage (3.2V empty, 4.2V full)
- Sends JSON over serial at 115200 baud

## 2) Set up Raspberry Pi software

```bash
cd LipoBattery/raspberry_pi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Find your Arduino serial path:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

Run the display:

```bash
./run_display.sh /dev/ttyUSB0 115200
```

Press `Esc` to leave fullscreen mode.

## Optional: Auto-start on boot with systemd

Create `/etc/systemd/system/lipo-monitor.service`:

```ini
[Unit]
Description=LiPo Monitor Display
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/path/to/repo/LipoBattery/raspberry_pi
ExecStart=/home/pi/path/to/repo/LipoBattery/raspberry_pi/run_display.sh /dev/ttyUSB0 115200
Restart=always
RestartSec=2

[Install]
WantedBy=graphical.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lipo-monitor
sudo systemctl start lipo-monitor
```

## Calibration tips

- Measure battery voltage with a multimeter.
- Compare to displayed value.
- Tweak `R1_OHMS`, `R2_OHMS`, or `ADC_REFERENCE_VOLTAGE` in the Arduino sketch if needed.
- For better stability, average multiple ADC samples.

## Teammate outreach text (optional)

If you want to recruit collaborators, you can post this:

> Looking for 1-2 teammates with Raspberry Pi digital interfacing experience and C/Python skills. Project: Arduino Nano reads LiPo battery voltage and streams data to a Raspberry Pi driving a 5" LCD. DM me if interested.

