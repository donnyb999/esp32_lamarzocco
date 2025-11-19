from machine import Pin
import time

class Encoder:
    def __init__(self, pin_a, pin_b, pin_btn=None):
        self.pin_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.pin_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.pin_btn = Pin(pin_btn, Pin.IN, Pin.PULL_UP) if pin_btn else None
        
        self.val = 0
        self.last_val = 0
        self._last_a = self.pin_a.value()
        
        self.pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handler)
        self.pin_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handler)
        
        self.btn_pressed = False
        if self.pin_btn:
            self.pin_btn.irq(trigger=Pin.IRQ_FALLING, handler=self._btn_handler)

    def _handler(self, pin):
        a = self.pin_a.value()
        b = self.pin_b.value()
        
        if a != self._last_a:
            if b != a:
                self.val += 1
            else:
                self.val -= 1
        self._last_a = a

    def _btn_handler(self, pin):
        # Simple debounce
        time.sleep_ms(20)
        if pin.value() == 0:
            self.btn_pressed = True

    def get_diff(self):
        diff = self.val - self.last_val
        self.last_val = self.val
        return diff

    def get_button(self):
        if self.btn_pressed:
            self.btn_pressed = False
            return True
        return False
