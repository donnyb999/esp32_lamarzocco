import time
from machine import Pin, SPI
import micropython

# SH8601 Constants
SH8601_SWRESET = 0x01
SH8601_SLPOUT = 0x11
SH8601_NORON = 0x13
SH8601_INVOFF = 0x20
SH8601_INVON = 0x21
SH8601_DISPON = 0x29
SH8601_CASET = 0x2A
SH8601_RASET = 0x2B
SH8601_RAMWR = 0x2C
SH8601_TEON = 0x35
SH8601_MADCTL = 0x36
SH8601_COLMOD = 0x3A

class SH8601:
    def __init__(self, spi, cs, dc, rst, bl=None, width=360, height=360, rotation=0):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT) if rst is not None else None
        self.bl = Pin(bl, Pin.OUT) if bl is not None else None
        self.width = width
        self.height = height
        
        self.cs.value(1)
        self.dc.value(0)
        if self.rst:
            self.rst.value(1)
            
        self.init_display()
        
        if self.bl:
            self.bl.value(1) # Turn on backlight

    def write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, buf):
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(buf)
        self.cs.value(1)

    def init_display(self):
        # Hardware Reset
        if self.rst:
            self.rst.value(0)
            time.sleep_ms(100)
            self.rst.value(1)
            time.sleep_ms(100)
            
        self.write_cmd(SH8601_SWRESET)
        time.sleep_ms(150)
        
        self.write_cmd(SH8601_SLPOUT)
        time.sleep_ms(150)
        
        self.write_cmd(SH8601_TEON) # Tearing Effect Line On
        self.write_data(b'\x00')

        # MADCTL
        self.write_cmd(SH8601_MADCTL)
        self.write_data(b'\x00') # RGB
        
        # COLMOD
        self.write_cmd(SH8601_COLMOD)
        self.write_data(b'\x05') # 16-bit
        
        # Porch Setting (Example values, might need tuning for specific panel)
        self.write_cmd(0xB2)
        self.write_data(b'\x0C')
        self.write_data(b'\x0C')
        self.write_data(b'\x00')
        self.write_data(b'\x33')
        self.write_data(b'\x33')
        
        self.write_cmd(0xB7) # Gate Control
        self.write_data(b'\x35')
        
        self.write_cmd(0xBB) # VCOM
        self.write_data(b'\x19')
        
        self.write_cmd(0xC0) # LCM Control
        self.write_data(b'\x2C')
        
        self.write_cmd(0xC2) # VDV and VRH Command Enable
        self.write_data(b'\x01')
        
        self.write_cmd(0xC3) # VRH Set
        self.write_data(b'\x12')
        
        self.write_cmd(0xC4) # VDV Set
        self.write_data(b'\x20')
        
        self.write_cmd(0xC6) # Frame Rate
        self.write_data(b'\x0F') # 60Hz
        
        self.write_cmd(0xD0) # Power Control 1
        self.write_data(b'\xA4')
        self.write_data(b'\xA1')
        
        self.write_cmd(0xE0) # Positive Gamma Control
        self.write_data(b'\xD0')
        self.write_data(b'\x04')
        self.write_data(b'\x0D')
        self.write_data(b'\x11')
        self.write_data(b'\x13')
        self.write_data(b'\x2B')
        self.write_data(b'\x3F')
        self.write_data(b'\x54')
        self.write_data(b'\x4C')
        self.write_data(b'\x18')
        self.write_data(b'\x0D')
        self.write_data(b'\x0B')
        self.write_data(b'\x1F')
        self.write_data(b'\x23')
        
        self.write_cmd(0xE1) # Negative Gamma Control
        self.write_data(b'\xD0')
        self.write_data(b'\x04')
        self.write_data(b'\x0C')
        self.write_data(b'\x11')
        self.write_data(b'\x13')
        self.write_data(b'\x2C')
        self.write_data(b'\x3F')
        self.write_data(b'\x44')
        self.write_data(b'\x51')
        self.write_data(b'\x2F')
        self.write_data(b'\x1F')
        self.write_data(b'\x1F')
        self.write_data(b'\x20')
        self.write_data(b'\x23')
        
        self.write_cmd(SH8601_INVON)
        self.write_cmd(SH8601_DISPON)
        time.sleep_ms(100)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(SH8601_CASET)
        self.write_data(bytearray([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self.write_cmd(SH8601_RASET)
        self.write_data(bytearray([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self.write_cmd(SH8601_RAMWR)
