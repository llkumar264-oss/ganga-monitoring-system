"""
Ganga Guardian - Sensor Data Simulator
Simulates IoT sensors posting pollution data to the API.
"""
import requests
import random
import time

API_URL = "http://127.0.0.1:8000/sensor-data"

LOCATIONS = [
    ("Assi Ghat", 25.2870, 82.9995),
    ("Dashashwamedh Ghat", 25.3109, 83.0107),
    ("Rajghat", 25.3270, 83.0163),
    ("Varanasi Ghat", 25.3176, 82.9739),
]


def main():
    print("Ganga Guardian Sensor Simulator")
    print("Sending data to", API_URL)
    print("-" * 40)
    while True:
        name, lat, lon = random.choice(LOCATIONS)
        ph = round(random.uniform(5, 9), 2)
        turbidity = random.randint(20, 100)
        chemical = random.randint(50, 200)
        payload = {
            "location": name,
            "ph": ph,
            "turbidity": turbidity,
            "chemical": chemical,
            "lat": lat,
            "lon": lon,
        }
        try:
            r = requests.post(API_URL, json=payload, timeout=5)
            data = r.json()
            print(f"[OK] {name} | pH={ph} T={turbidity} C={chemical} -> {data.get('risk_level', '?')}")
        except Exception as e:
            print(f"[ERR] {e}")
        time.sleep(10)


if __name__ == "__main__":
    main()
