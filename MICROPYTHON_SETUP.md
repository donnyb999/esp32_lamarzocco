# MicroPython + LVGL Setup Guide for ESP32-S3

This project requires a **custom MicroPython firmware** that includes the **LVGL** library. The standard MicroPython firmware downloaded from `micropython.org` **DOES NOT** include LVGL, and running this project on it will result in `ImportError: no module named 'lvgl'`.

## 📋 Device Details
-   **Board**: Waveshare ESP32-S3-Knob-Touch-LCD-1.8
-   **Chip**: ESP32-S3R8 (8MB PSRAM, 16MB Flash)
-   **Architecture**: Xtensa LX7

## 📥 Option 1: Download Pre-built Firmware (Easiest)

The easiest way to get a working firmware is to download a build artifact from the official `lv_micropython` repository's CI (Continuous Integration).

1.  Go to the [lv_micropython Actions page](https://github.com/lvgl/lv_micropython/actions).
2.  Click on the latest successful workflow run (usually titled "MicroPython CI" or similar).
3.  Scroll down to the **Artifacts** section.
4.  Look for a build named `esp32-s3-spiram` or `esp32-s3-idf4.4` (ensure it mentions S3 and SPIRAM/PSRAM).
    *   *Note: You must be logged into GitHub to download artifacts.*
5.  Download and extract the zip file to find the `.bin` file (e.g., `micropython.bin`).

## 🛠 Option 2: Build It Yourself (Advanced)

If you cannot find a working pre-built binary, you can build it using Docker.

1.  **Clone the Repository**:
    ```bash
    git clone --recursive https://github.com/lvgl/lv_micropython.git
    cd lv_micropython
    ```

2.  **Build using Docker**:
    Run the following command to build for ESP32-S3 with SPIRAM support:
    ```bash
    docker run --rm -v $PWD:/project -w /project espressif/idf:release-v4.4 \
    /bin/bash -c "make -C mpy-cross && make -C ports/esp32 BOARD=GENERIC_S3_SPIRAM submodules && make -C ports/esp32 BOARD=GENERIC_S3_SPIRAM"
    ```
    *   *Note: This assumes a Linux/Mac environment or WSL on Windows.*

3.  **Locate Firmware**:
    The built firmware will be at `ports/esp32/build-GENERIC_S3_SPIRAM/micropython.bin`.

## ⚡ Flashing the Firmware

Once you have the `micropython.bin` file, you need to flash it to your board.

### Prerequisites
-   **Python** installed.
-   **esptool** installed: `pip install esptool`

### Flashing Steps

1.  **Connect the Board**: Connect your ESP32-S3 to your computer via USB-C.
2.  **Find the Port**:
    -   **Windows**: Check Device Manager (COMx, e.g., `COM3`).
    -   **Mac/Linux**: `ls /dev/tty*` (e.g., `/dev/tty.usbmodem...`).
3.  **Erase Flash** (Recommended for first time):
    ```bash
    esptool.py --port COMx erase_flash
    ```
    *(Replace `COMx` with your actual port)*
4.  **Flash Firmware**:
    ```bash
    esptool.py --chip esp32s3 --port COMx write_flash -z 0x0 micropython.bin
    ```

## ✅ Verification

1.  Open a serial terminal (like Thonny, PuTTY, or `mpremote`).
2.  Reset the board.
3.  You should see the MicroPython REPL prompt `>>>`.
4.  Type the following to verify LVGL is present:
    ```python
    import lvgl
    print(lvgl.VERSION_MAJOR)
    ```
    If this runs without error, you are ready to upload the project files!
