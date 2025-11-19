import lvgl as lv
import math
import uasyncio as asyncio
import time

# Constants
SCREEN_SIZE = 360
RADIUS = 140
ICON_SIZE = 60
CENTER_SIZE = 120
SEND_DELAY_MS = 2000 # 2 seconds delay before sending

class PlanetaryUI:
    def __init__(self, display_driver, touch_driver, encoder_driver, machine_client):
        self.disp = display_driver
        self.touch = touch_driver
        self.enc = encoder_driver
        self.client = machine_client
        
        self.scr = lv.obj()
        lv.scr_load(self.scr)
        self.scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        self.items = [
            {"name": "Power", "icon": lv.SYMBOL.POWER, "value": "OFF", "type": "bool"},
            {"name": "Temp", "icon": lv.SYMBOL.SETTINGS, "value": 93.0, "type": "float"},
            {"name": "Steam", "icon": lv.SYMBOL.CHARGE, "value": 1, "type": "int"},
            {"name": "Pre-Inf", "icon": lv.SYMBOL.WIFI, "value": "ON", "type": "bool"},
            {"name": "Timer", "icon": lv.SYMBOL.EYE_OPEN, "value": "0s", "type": "info"},
            {"name": "Stats", "icon": lv.SYMBOL.LIST, "value": "--", "type": "info"},
        ]
        
        self.icon_objs = []
        self.selected_idx = -1 # No selection initially
        self.active_mode = False # False = Perimeter, True = Center/Editing
        self.send_timer_task = None
        
        self._init_ui()
        self._update_layout()

    def _init_ui(self):
        # Center Widget (Click to return)
        self.center_obj = lv.obj(self.scr)
        self.center_obj.set_size(CENTER_SIZE, CENTER_SIZE)
        self.center_obj.center()
        self.center_obj.set_style_radius(lv.RADIUS_CIRCLE, 0)
        self.center_obj.set_style_bg_color(lv.color_hex(0x222222), 0)
        self.center_obj.set_style_border_color(lv.color_hex(0xFFFFFF), 0)
        self.center_obj.set_style_border_width(2, 0)
        self.center_obj.add_event_cb(self._on_center_click, lv.EVENT.CLICKED, None)
        
        self.center_label = lv.label(self.center_obj)
        self.center_label.center()
        self.center_label.set_text("Ready")
        
        # Perimeter Icons
        for i, item in enumerate(self.items):
            obj = lv.btn(self.scr)
            obj.set_size(ICON_SIZE, ICON_SIZE)
            obj.set_style_radius(lv.RADIUS_CIRCLE, 0)
            obj.set_style_bg_color(lv.color_hex(0x333333), 0)
            
            # Store index in user_data or use closure
            # Using closure for simplicity in MicroPython if supported, or just iterate to find
            # We'll use a wrapper lambda or helper
            def make_cb(index):
                return lambda e: self._on_icon_click(index)
            
            obj.add_event_cb(make_cb(i), lv.EVENT.CLICKED, None)
            
            label = lv.label(obj)
            label.set_text(item["icon"])
            label.center()
            
            self.icon_objs.append(obj)

    def _on_icon_click(self, index):
        if self.active_mode and self.selected_idx == index:
            return # Already active
        
        print(f"Icon {index} clicked")
        self.selected_idx = index
        self.active_mode = True
        self._update_layout()

    def _on_center_click(self, e):
        if not self.active_mode:
            return
        # Return to perimeter
        self.active_mode = False
        self.selected_idx = -1
        self._update_layout()

    def _update_layout(self):
        angle_step = 360 / len(self.items)
        
        # Update Center Label
        if self.active_mode and self.selected_idx >= 0:
            item = self.items[self.selected_idx]
            self.center_label.set_text(f"{item['name']}\n{item['value']}")
        else:
            self.center_label.set_text("Ready")

        for i, obj in enumerate(self.icon_objs):
            if self.active_mode and i == self.selected_idx:
                # Move to center
                obj.set_size(CENTER_SIZE, CENTER_SIZE)
                obj.center()
                obj.set_style_bg_color(lv.color_hex(0x0055FF), 0)
                # Hide center obj (or put it behind? We hide it to avoid conflict)
                self.center_obj.add_flag(lv.obj.FLAG.HIDDEN)
                
                # Update label to show value
                label = obj.get_child(0)
                label.set_text(f"{self.items[i]['value']}")
                
            elif self.active_mode:
                # Hide others
                obj.add_flag(lv.obj.FLAG.HIDDEN)
            else:
                # Normal Planetary Layout
                self.center_obj.clear_flag(lv.obj.FLAG.HIDDEN)
                obj.clear_flag(lv.obj.FLAG.HIDDEN)
                obj.set_size(ICON_SIZE, ICON_SIZE)
                obj.set_style_bg_color(lv.color_hex(0x333333), 0)
                
                # Reset label to icon
                label = obj.get_child(0)
                label.set_text(self.items[i]['icon'])
                
                # Calculate position
                # Rotate so 0 is at top (270 deg)
                angle = (i * angle_step) - 90
                rad = math.radians(angle)
                x = int(RADIUS * math.cos(rad)) + (SCREEN_SIZE // 2) - (ICON_SIZE // 2)
                y = int(RADIUS * math.sin(rad)) + (SCREEN_SIZE // 2) - (ICON_SIZE // 2)
                
                obj.set_pos(x, y)
                obj.set_style_border_width(0, 0)

    async def loop(self):
        while True:
            # Handle Encoder (Only for adjustment now)
            diff = self.enc.get_diff()
            if diff != 0 and self.active_mode:
                self._adjust_value(diff)
            
            # Handle Touch is done via LVGL events
            
            lv.task_handler()
            await asyncio.sleep(0.02)

    def _adjust_value(self, diff):
        item = self.items[self.selected_idx]
        
        # Logic to change values based on type
        if item["type"] == "float":
            item["value"] += diff * 0.1
            item["value"] = round(item["value"], 1)
        elif item["type"] == "int":
            item["value"] += diff
        elif item["type"] == "bool":
            if diff != 0:
                val = item["value"]
                item["value"] = "OFF" if val == "ON" else "ON"
        
        # Update UI immediately
        self._update_layout()
        
        # Schedule Auto-Send
        if self.send_timer_task:
            self.send_timer_task.cancel()
        self.send_timer_task = asyncio.create_task(self._auto_send_delay())

    async def _auto_send_delay(self):
        try:
            await asyncio.sleep_ms(SEND_DELAY_MS)
            print(f"Auto-sending value for {self.items[self.selected_idx]['name']}")
            # Call API here
            # await self.client.set_something(...)
            self.send_timer_task = None
        except asyncio.CancelledError:
            pass
