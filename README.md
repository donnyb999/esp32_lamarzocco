# ESP32-S3 La Marzocco Linea Micra Controller

A MicroPython-based firmware for the **Waveshare ESP32-S3-Knob-Touch-LCD-1.8** to control a La Marzocco Linea Micra espresso machine. This project provides a modern, circular "Planetary" UI built with **LVGL** to adjust temperature, steam power, and pre-infusion settings via the La Marzocco Cloud API.

## 🚀 Features

-   **Planetary UI**: A unique circular interface optimized for the 1.8" round display.
-   **Dual Input**: Supports both **Rotary Encoder** navigation and **Touch Screen** interaction.
-   **Machine Control**:
    -   Toggle Power (On/Standby)
    -   Set Coffee Boiler Temperature (0.1°C increments)
    -   Set Steam Level (1, 2, or 3)
    -   Configure Pre-Infusion (Enable/Disable, Time)
-   **Telemetry**: Displays machine status and timers.
-   **Smart Debouncing**: Prevents API rate limiting during rapid encoder adjustments.

## 🛠 Hardware Requirements

-   **Device**: [Waveshare ESP32-S3-Knob-Touch-LCD-1.8](https://www.waveshare.com/wiki/ESP32-S3-Knob-Touch-LCD-1.8)
-   **Display Driver**: SH8601 (SPI/QSPI)
-   **Touch Driver**: CST816S (I2C)
-   **Microcontroller**: ESP32-S3

## 💾 Software Requirements

-   **MicroPython Firmware**: You **MUST** use a MicroPython build that includes **LVGL** support. Standard MicroPython binaries will not work.
    -   Recommended: Custom build using [lv_micropython](https://github.com/lvgl/lv_micropython).

## 📂 Project Structure

```
esp32_lamarzocco/
├── config.py              # Configuration (WiFi, API Creds, Pins)
├── main.py                # Entry point, Hardware & LVGL Init
├── drivers/
│   ├── display.py         # SH8601 Display Driver
│   ├── touch.py           # CST816S Touch Driver
│   └── encoder.py         # Rotary Encoder Driver
├── lib/
│   └── lamarzocco.py      # La Marzocco "Lite" API Client
└── ui/
    └── interface.py       # LVGL UI Logic (Planetary Layout)
```

## ⚙️ Installation & Setup

1.  **Flash Firmware**: Flash your ESP32-S3 with an LVGL-enabled MicroPython firmware.
2.  **Configure**:
    -   Open `config.py`.
    -   Enter your WiFi credentials (`WIFI_SSID`, `WIFI_PASSWORD`).
    -   Enter your La Marzocco credentials (`LM_EMAIL`, `LM_PASSWORD`, `LM_MACHINE_ID`).
    -   *Optional*: Verify GPIO pins if your board revision differs.
3.  **Upload**: Upload all files and folders to the root of the ESP32-S3 using a tool like `mpremote` (mpremote cp -r . :), `ampy`, or Thonny.
4.  **Run**: Reset the board. The UI should start automatically.

## 🎮 Usage

-   **Select**: Tap an icon on the screen to select it. It will move to the center.
-   **Adjust**: Rotate the knob to change the value of the selected item.
-   **Auto-Save**: Stop rotating the knob. After a short delay (2 seconds), the new value is automatically sent to the machine.
-   **Return**: Tap the center icon (or background) to return to the main menu.

## ⚠️ Disclaimer

This project is not affiliated with La Marzocco. Use at your own risk. The API client mimics the official app's behavior but is unofficial.

## 🤝 Credits

-   **UI Framework**: [LVGL](https://lvgl.io/)
-   **Inspiration**: [pylamarzocco](https://github.com/zweckj/pylamarzocco) for API reverse engineering.
