import lvgl as lv
import math
import uasyncio as asyncio

# Constants
SCREEN_W = 240 # GC9A01 is usually 240x240, User said 360x360. 
# Wiki says 1.28" is 240x240, 1.8" is 360x360? 
# User said 1.8" 360x360. I will use 360.
SCREEN_SIZE = 360
RADIUS = 140
ICON_SIZE = 60
CENTER_SIZE = 120

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
            {"name": "Temp", "icon": lv.SYMBOL.SETTINGS, "value": "93.0", "type": "float"},
            {"name": "Steam", "icon": lv.SYMBOL.CHARGE, "value": "1", "type": "int"},
            {"name": "Pre-Inf", "icon": lv.SYMBOL.WIFI, "value": "ON", "type": "bool"},
            {"name": "Timer", "icon": lv.SYMBOL.EYE_OPEN, "value": "0s", "type": "info"},
            {"name": "Stats", "icon": lv.SYMBOL.LIST, "value": "--", "type": "info"},
        ]
        
        self.icon_objs = []
        self.selected_idx = 0
        self.active_mode = False # False = Navigating, True = Editing
        
        self._init_ui()
        self._update_layout()

    def _init_ui(self):
        # Center Widget
        self.center_obj = lv.obj(self.scr)
        self.center_obj.set_size(CENTER_SIZE, CENTER_SIZE)
        self.center_obj.center()
        self.center_obj.set_style_radius(lv.RADIUS_CIRCLE, 0)
        self.center_obj.set_style_bg_color(lv.color_hex(0x222222), 0)
        self.center_obj.set_style_border_color(lv.color_hex(0xFFFFFF), 0)
        self.center_obj.set_style_border_width(2, 0)
        
        self.center_label = lv.label(self.center_obj)
        self.center_label.center()
        self.center_label.set_text("Ready")
        
        # Perimeter Icons
        for i, item in enumerate(self.items):
            obj = lv.btn(self.scr)
            obj.set_size(ICON_SIZE, ICON_SIZE)
            obj.set_style_radius(lv.RADIUS_CIRCLE, 0)
            obj.set_style_bg_color(lv.color_hex(0x333333), 0)
            
            label = lv.label(obj)
            label.set_text(item["icon"])
            label.center()
            
            self.icon_objs.append(obj)

    def _update_layout(self):
        angle_step = 360 / len(self.items)
        
        for i, obj in enumerate(self.icon_objs):
            if self.active_mode and i == self.selected_idx:
                # Move to center
                obj.set_size(CENTER_SIZE, CENTER_SIZE)
                obj.center()
                obj.set_style_bg_color(lv.color_hex(0x0055FF), 0)
                # Hide center obj
                self.center_obj.add_flag(lv.obj.FLAG.HIDDEN)
            elif self.active_mode:
                # Hide others
                obj.add_flag(lv.obj.FLAG.HIDDEN)
            else:
                # Normal Planetary Layout
                self.center_obj.clear_flag(lv.obj.FLAG.HIDDEN)
                obj.clear_flag(lv.obj.FLAG.HIDDEN)
                obj.set_size(ICON_SIZE, ICON_SIZE)
                
                # Calculate position
                # Rotate so selected is at top (270 deg)
                angle = (i * angle_step) - (self.selected_idx * angle_step) - 90
                rad = math.radians(angle)
                x = int(RADIUS * math.cos(rad)) + (SCREEN_SIZE // 2) - (ICON_SIZE // 2)
                y = int(RADIUS * math.sin(rad)) + (SCREEN_SIZE // 2) - (ICON_SIZE // 2)
                
                obj.set_pos(x, y)
                
                if i == self.selected_idx:
                    obj.set_style_border_color(lv.color_hex(0xFFFFFF), 0)
                    obj.set_style_border_width(3, 0)
                else:
                    obj.set_style_border_width(0, 0)

    async def loop(self):
        while True:
            # Handle Encoder
            diff = self.enc.get_diff()
            if diff != 0:
                if self.active_mode:
                    self._adjust_value(diff)
                else:
                    self.selected_idx = (self.selected_idx + diff) % len(self.items)
                    self._update_layout()
            
            if self.enc.get_button():
                self.active_mode = not self.active_mode
                self._update_layout()
            
            # Handle Touch (Simplified)
            # In a real app, we'd map touch X/Y to objects.
            # For now, just use encoder for navigation as requested.
            
            lv.task_handler()
            await asyncio.sleep(0.02)

    def _adjust_value(self, diff):
        item = self.items[self.selected_idx]
        # Logic to change values based on type
        # Update label
        pass
