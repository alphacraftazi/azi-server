import requests
import json
import threading
import time
import os

TELEMETRY_API = "http://127.0.0.1:8001/api/telemetry" # Localhost for now, update for prod

class TelemetryWorker:
    def __init__(self, license_key, app_name, data_dir, api_interface, server_url=None):
        self.license_key = license_key
        self.app_name = app_name
        self.data_dir = data_dir
        self.api = api_interface
        self.is_running = True
        
        # Dynamic URL Support
        base_url = server_url if server_url else "http://localhost:8001"
        self.telemetry_api = f"{base_url.rstrip('/')}/api/telemetry"
        print(f"[{self.app_name}] Telemetry Target: {self.telemetry_api}")
        
    def start(self):
        threading.Thread(target=self._run_loop, daemon=True).start()
        
    def _run_loop(self):
        print(f"[{self.app_name}] Telemetry Loop Started.")
        while self.is_running:
            try:
                self._ping_server()
                self._check_for_commands()
            except Exception as e:
                print(f"Telemetry Error: {e}")
            
            time.sleep(60) # Every 60 seconds

    def _ping_server(self):
        payload = {
            "license_key": self.license_key,
            "status": "online",
            "app": self.app_name,
            "timestamp": time.time()
        }
        try:
            res = requests.post(f"{self.telemetry_api}/ping", json=payload, timeout=5)
            if res.status_code == 200:
                print("Server Ping: OK")
        except:
            print("Server Ping: Failed (Offline?)")

    def _check_for_commands(self):
        # Poll for commands
        try:
            res = requests.get(f"{self.telemetry_api}/command?license={self.license_key}", timeout=5)
            if res.status_code == 200:
                cmd = res.json()
                if cmd and cmd.get('action'):
                    self._execute_command(cmd)
        except:
            pass

    def _execute_command(self, cmd):
        print(f"Executing Command: {cmd['action']}")
        # Basic Actions
        if cmd['action'] == 'sync_data':
            # Upload data
            pass
        elif cmd['action'] == 'popup':
            # Show message (Requires WebView API access, might need callback)
            pass
