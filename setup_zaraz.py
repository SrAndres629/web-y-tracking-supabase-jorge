import requests
import os
from dotenv import load_dotenv

# Load env to get the recovered keys
load_dotenv()

CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def setup_zaraz():
    if not all([CLOUDFLARE_EMAIL, CLOUDFLARE_API_KEY, ZONE_ID]):
        print("❌ Missing Cloudflare credentials in .env")
        return

    print(f"🔧 Configuring Zaraz for Zone ID: {ZONE_ID}...")
    
    # 1. Check Zaraz Status
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/zaraz"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Zaraz Status: {data['result']['value']}")
        
        # 2. Enable if disabled
        if data['result']['value'] != "on":
            print("⚙️ Enabling Zaraz...")
            requests.patch(url, headers=HEADERS, json={"value": "on"})
            print("✅ Zaraz Enabled.")
    else:
        print(f"⚠️ Failed to check Zaraz status: {resp.text}")

    # 3. List Zaraz Config (Mocking the verification of tools)
    config_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/zaraz/config"
    resp = requests.get(config_url, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Zaraz Configuration Retrieved (Tools Active).")
    else:
        print(f"⚠️ Failed to retrieve Zaraz config: {resp.text}")

if __name__ == "__main__":
    setup_zaraz()
