import threading
import requests
import time
import uuid

# Configuration
SERVER_URL = "http://localhost:8001/api/telemetry/ping"
NUM_CLIENTS = 10
DURATION_SECONDS = 30
PING_INTERVAL = 1

def client_simulator(idx):
    license = f"STRESS-TEST-{idx:02d}"
    app_name = f"AlphaBot-{idx}"
    
    end_time = time.time() + DURATION_SECONDS
    count = 0 
    errors = 0
    
    print(f"[{license}] Started.")
    
    while time.time() < end_time:
        try:
            payload = {
                "license_key": license,
                "status": "online",
                "app": app_name,
                "timestamp": time.time(),
                "details": {"cpu": 15, "mem": 1024}
            }
            res = requests.post(SERVER_URL, json=payload, timeout=2)
            if res.status_code == 200:
                count += 1
            else:
                errors += 1
                print(f"[{license}] Error: {res.status_code}")
        except Exception as e:
            errors += 1
            print(f"[{license}] Exception: {e}")
            
        time.sleep(PING_INTERVAL)
        
    print(f"[{license}] Finished. Pings: {count}, Errors: {errors}")

print(f"--- STARTING STRESS TEST ({NUM_CLIENTS} Threads, {DURATION_SECONDS}s) ---")
threads = []
for i in range(NUM_CLIENTS):
    t = threading.Thread(target=client_simulator, args=(i, ))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
    
print("--- STRESS TEST COMPLETE ---")
