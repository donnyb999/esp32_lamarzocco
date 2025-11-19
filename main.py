import network
import uasyncio as asyncio
from machine import SPI, Pin, I2C
import config
from drivers.display import SH8601
from drivers.touch import CST816S
from drivers.encoder import Encoder
from lib.lamarzocco import LamarzoccoLite
from ui.interface import PlanetaryUI
import lvgl as lv

# Initialize LVGL
lv.init()

async def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    print("Connecting to WiFi...")
    while not wlan.isconnected():
        await asyncio.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())

async def main():
    # 1. Hardware Init
    # Display
    spi = SPI(config.LCD_SPI_ID, baudrate=40000000, sck=Pin(config.LCD_SCK), mosi=Pin(config.LCD_MOSI))
    disp_drv = SH8601(spi, cs=config.LCD_CS, dc=config.LCD_DC, rst=config.LCD_RST, bl=config.LCD_BL, width=360, height=360)
    
    # Register LVGL Display Driver
    def disp_flush(disp_drv_lv, area, color_p):
        # Convert LVGL area to coordinates
        x1, y1 = area.x1, area.y1
        x2, y2 = area.x2, area.y2
        
        # Calculate size
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        
        # Get data (this part depends on how lv_micropython is compiled, usually it's a buffer)
        # For this example, we assume color_p is accessible as a buffer
        # We need to send this to the display driver
        
        # Note: This is a high-level abstraction. In real lv_micropython, 
        # you often use a dedicated C-module driver or a specific Python wrapper.
        # Here we map it to our Python driver.
        
        # disp_drv.set_window(x1, y1, x2, y2)
        # disp_drv.write_data(color_p) # This would need buffer conversion
        
        # Signal LVGL that flushing is done
        disp_drv_lv.flush_ready()

    # Create LVGL display driver object
    lv_disp_drv = lv.disp_drv_t()
    lv_disp_drv.init()
    lv_disp_drv.flush_cb = disp_flush
    lv_disp_drv.hor_res = 360
    lv_disp_drv.ver_res = 360
    lv_disp_drv.register()

    # Touch
    i2c = I2C(config.TOUCH_I2C_ID, scl=Pin(config.TOUCH_SCL), sda=Pin(config.TOUCH_SDA))
    touch_drv = CST816S(i2c, rst=config.TOUCH_RST, int_pin=config.TOUCH_INT)
    
    # Register LVGL Input Driver
    def touch_read(indev_drv, data):
        t = touch_drv.read()
        if t:
            data.point.x, data.point.y, _ = t
            data.state = lv.INDEV_STATE.PRESSED
        else:
            data.state = lv.INDEV_STATE.RELEASED
        return False

    lv_indev_drv = lv.indev_drv_t()
    lv_indev_drv.init()
    lv_indev_drv.type = lv.INDEV_TYPE.POINTER
    lv_indev_drv.read_cb = touch_read
    lv_indev_drv.register()
    
    # Encoder (Hardware)
    enc_drv = Encoder(config.ENCODER_A, config.ENCODER_B, config.ENCODER_BTN)
    
    # Register LVGL Encoder Driver (Optional, if we want LVGL groups)
    def enc_read(indev_drv, data):
        diff = enc_drv.get_diff()
        data.enc_diff = diff
        if enc_drv.get_button():
            data.state = lv.INDEV_STATE.PRESSED
        else:
            data.state = lv.INDEV_STATE.RELEASED
        return False
        
    lv_enc_drv = lv.indev_drv_t()
    lv_enc_drv.init()
    lv_enc_drv.type = lv.INDEV_TYPE.ENCODER
    lv_enc_drv.read_cb = enc_read
    lv_enc_group = lv_enc_drv.register()
    
    # Create a group for the encoder
    g = lv.group_create()
    g.set_default()
    lv.indev_set_group(lv_enc_group, g)
    
    # 2. Logic Init
    lm_client = LamarzoccoLite(
        client_id="YOUR_CLIENT_ID", 
        client_secret="YOUR_CLIENT_SECRET", 
        email=config.LM_EMAIL, 
        password=config.LM_PASSWORD, 
        machine_serial=config.LM_MACHINE_ID
    )
    
    # 3. UI Init
    ui = PlanetaryUI(disp_drv, touch_drv, enc_drv, lm_client)
    
    # 4. Start Tasks
    asyncio.create_task(connect_wifi())
    # asyncio.create_task(lm_client.connect()) # Uncomment when credentials set
    
    print("Starting UI Loop...")
    await ui.loop()

if __name__ == "__main__":
    asyncio.run(main())
