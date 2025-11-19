import urequests
import ujson
import uasyncio as asyncio
import time

BASE_URL = "https://gw-lmz.lamarzocco.com/v1/home"
TOKEN_URL = "https://cms.lamarzocco.io/oauth/v2/token"

class LamarzoccoLite:
    def __init__(self, client_id, client_secret, email, password, machine_serial):
        self.client_id = client_id
        self.client_secret = client_secret
        self.email = email
        self.password = password
        self.serial = machine_serial
        self.token = None
        self.status = {}
        
        # Debounce / Cooldown tracking
        self.last_api_call = 0
        self.pending_updates = {}

    async def connect(self):
        # Authenticate and get token
        # Note: This is a simplified auth flow. 
        # In a real scenario, you might need the full OAuth dance.
        # For this Lite version, we assume we can get a token via password grant or similar.
        # If not, the user might need to provide a valid token in config.
        print("Authenticating...")
        # Placeholder for actual Auth logic
        self.token = "PLACEHOLDER_TOKEN" 
        print("Connected.")

    async def get_status(self):
        if not self.token:
            return None
            
        url = f"{BASE_URL}/machines/{self.serial}/status"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # In asyncio, we might want to run this in a thread or use a non-blocking socket
            # For simplicity in MicroPython, we often use urequests directly but it blocks.
            # We can wrap it or accept the small block.
            res = urequests.get(url, headers=headers)
            self.status = res.json()
            res.close()
            return self.status
        except Exception as e:
            print(f"Error fetching status: {e}")
            return None

    async def _send_command(self, endpoint, payload):
        if not self.token:
            return
            
        url = f"{BASE_URL}/machines/{self.serial}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            res = urequests.post(url, headers=headers, data=ujson.dumps(payload))
            res.close()
        except Exception as e:
            print(f"Error sending command: {e}")

    async def set_power(self, on):
        await self._send_command("status", {"status": "ON" if on else "STANDBY"})

    async def set_temp(self, temp):
        # Debounce logic should be handled by the caller or a queue
        # But we can enforce a cooldown here
        now = time.time()
        if now - self.last_api_call < 1:
            print("Rate limit: Skipping temp update")
            return
        
        await self._send_command("configuration", {"boiler_target_temperature": temp})
        self.last_api_call = now

    async def set_steam(self, level):
        # Level 1, 2, 3
        await self._send_command("configuration", {"steam_level": level})

    async def set_preinfusion(self, enabled, k_on, k_off):
        payload = {
            "preinfusion_enabled": enabled,
            "preinfusion_k_on": k_on,
            "preinfusion_k_off": k_off
        }
        await self._send_command("configuration", payload)
