from machine import Pin, I2C
import time

CST816S_ADDR = 0x15

class CST816S:
    def __init__(self, i2c, rst=-1, int_pin=-1):
        self.i2c = i2c
        self.addr = CST816S_ADDR
        
        if rst >= 0:
            self.rst = Pin(rst, Pin.OUT)
            self.reset()
            
        if int_pin >= 0:
            self.int_pin = Pin(int_pin, Pin.IN, Pin.PULL_UP)
        else:
            self.int_pin = None

    def reset(self):
        self.rst.value(0)
        time.sleep_ms(5)
        self.rst.value(1)
        time.sleep_ms(50)

    def read(self):
        """
        Returns (x, y, gesture_id) or None if no touch.
        """
        try:
            data = self.i2c.readfrom_mem(self.addr, 0x00, 7)
            gesture_id = data[1]
            points = data[2]
            
            if points > 0:
                x = ((data[3] & 0x0F) << 8) | data[4]
                y = ((data[5] & 0x0F) << 8) | data[6]
                return x, y, gesture_id
        except Exception:
            pass
        return None
