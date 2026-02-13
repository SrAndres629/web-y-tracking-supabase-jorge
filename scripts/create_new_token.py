import requests
import json

CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
CLOUDFLARE_API_KEY = "CLOUDFLARE_API_KEY_REEMPLAZAR"
ACCOUNT_ID = "18d305c823dc9ab6f0663bde930a9fc2"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def create_new_token():
    url = "https://api.cloudflare.com/client/v4/user/tokens"
    
    payload = {
        "name": "Antigravity Senior MCP Token",
        "status": "active",
        "policies": [
            {
                "effect": "allow",
                "resources": {f"com.cloudflare.api.account.{ACCOUNT_ID}": "*"},
                "permission_groups": [
                    {"id": "c8fed203ed3043cba015a93ad1616f1f"}, # Zone Read
                    {"id": "517b21aee92c4d89936c976ba6e4be55"}, # Zone Settings Read
                    {"id": "5bdbde7e76144204a244274eac3eb0eb"}, # Zaraz Read
                    {"id": "c4df38be41c247b3b4b7702e76eadae0"}  # Zone DNS Settings Write
                ]
            }
        ]
    }
    
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        result = resp.json().get("result", {})
        print(f"✅ SUCCESS: New Token Created.")
        print(f"TOKEN_VALUE: {result.get('value')}")
    else:
        print(f"❌ ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    create_new_token()

