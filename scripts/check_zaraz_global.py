import os
import requests
import json

CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
ZONE_ID = "19bd9bdd7abf8f74b4e95d75a41e8583"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def check_zaraz():
    print(f"Checking Zaraz for Zone: {ZONE_ID}")
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/zaraz/config"
    resp = requests.get(url, headers=HEADERS)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Zaraz is active!")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"❌ Error: {resp.text}")

if __name__ == "__main__":
    check_zaraz()
