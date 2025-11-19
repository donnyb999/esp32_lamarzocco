# Config.py
# Configuration for ESP32-S3 La Marzocco Controller

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# La Marzocco Credentials
LM_EMAIL = "your_email@example.com"
LM_PASSWORD = "your_password"
LM_MACHINE_ID = "your_machine_serial_number" # e.g., "LM123456"

# Hardware Pinout (Waveshare ESP32-S3-Knob-Touch-LCD-1.8)
# PLEASE VERIFY THESE PINS WITH YOUR SPECIFIC BOARD REVISION

# Display (SH8601)
# Note: User specified SH8601.
# Pinout based on common Waveshare S3 board patterns.
LCD_SPI_ID = 1
LCD_CS = 14
LCD_SCK = 13
LCD_MOSI = 15
LCD_MISO = 12 # Not used usually
LCD_DC = 21   # Data/Command (Sometimes shared with Reset or separate)
LCD_RST = 47  # Reset
LCD_BL = 48   # Backlight

# Touch (CST816S)
TOUCH_I2C_ID = 0
TOUCH_SDA = 6  # Placeholder - Verify
TOUCH_SCL = 7  # Placeholder - Verify
TOUCH_RST = -1
TOUCH_INT = -1

# Rotary Encoder
ENCODER_A = 40 # Placeholder - Verify
ENCODER_B = 41 # Placeholder - Verify
ENCODER_BTN = 42 # Placeholder - Verify

# System
DEBOUNCE_MS = 1000 # 1 second debounce for API calls
