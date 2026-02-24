/*
  LipoBattery Nano Reader
  Reads a LiPo battery through a resistor divider on A0 and sends JSON to serial.

  Wiring assumptions:
  - Battery positive -> R1 -> A0 -> R2 -> GND
  - Battery negative -> GND
  - Recommended divider for 1S LiPo (max 4.2V): R1 = 10k, R2 = 20k

  Divider ratio = (R1 + R2) / R2 = 1.5
*/

const uint8_t BATTERY_PIN = A0;
const float ADC_REFERENCE_VOLTAGE = 5.0;      // Nano default analog reference
const int ADC_MAX = 1023;
const float R1_OHMS = 10000.0;
const float R2_OHMS = 20000.0;
const unsigned long SAMPLE_INTERVAL_MS = 500;

// Clamp percentage between 0 and 100 for a 1S LiPo
float batteryPercent(float volts) {
  const float EMPTY_V = 3.2;
  const float FULL_V = 4.2;

  float pct = (volts - EMPTY_V) * 100.0 / (FULL_V - EMPTY_V);
  if (pct < 0.0) return 0.0;
  if (pct > 100.0) return 100.0;
  return pct;
}

float readBatteryVoltage() {
  int raw = analogRead(BATTERY_PIN);
  float pinVoltage = (raw * ADC_REFERENCE_VOLTAGE) / ADC_MAX;
  float dividerRatio = (R1_OHMS + R2_OHMS) / R2_OHMS;
  return pinVoltage * dividerRatio;
}

void setup() {
  Serial.begin(115200);
  pinMode(BATTERY_PIN, INPUT);
}

void loop() {
  static unsigned long lastSample = 0;
  unsigned long now = millis();

  if (now - lastSample >= SAMPLE_INTERVAL_MS) {
    lastSample = now;

    float voltage = readBatteryVoltage();
    float percent = batteryPercent(voltage);

    Serial.print("{\"voltage\":");
    Serial.print(voltage, 3);
    Serial.print(",\"percent\":");
    Serial.print(percent, 1);
    Serial.println("}");
  }
}
