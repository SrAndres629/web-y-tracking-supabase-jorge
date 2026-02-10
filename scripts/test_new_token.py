import requests
import json

# THE NEW TOKEN
TOKEN = "_f1QrJImGK0Qg5eSACM1DGnkF6xd9yRMGGXvGUA8"
ZONE_ID = "19bd9bdd7abf8f74b4e95d75a41e8583"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_new_token():
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/zaraz/config"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        print("✅ SUCCESS: The New Token works for Zaraz!")
        print(f"Zaraz Settings: {json.dumps(resp.json().get('result', {}).get('settings', {}), indent=2)}")
    else:
        print(f"❌ ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    test_new_token()
