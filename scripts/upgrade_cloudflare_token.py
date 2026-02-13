import requests
import json

CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
CLOUDFLARE_API_KEY = "CLOUDFLARE_API_KEY_REEMPLAZAR"
TOKEN_ID = "d5cc4a77c18eb32fbd8e6df239eb1105"
ACCOUNT_ID = "18d305c823dc9ab6f0663bde930a9fc2"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def upgrade_token():
    url = f"https://api.cloudflare.com/client/v4/user/tokens/{TOKEN_ID}"
    
    # Permission IDs:
    # Zaraz Read: 5bdbde7e76144204a244274eac3eb0eb
    # Zone Read: c8fed203ed3043cba015a93ad1616f1f
    # Zone Settings Read: 517b21aee92c4d89936c976ba6e4be55
    # DNS Settings Write: c4df38be41c247b3b4b7702e76eadae0
    
    payload = {
        "name": "Editar zona DNS (Senior Audited)",
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
        ],
        "condition": None
    }
    
    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        print("✅ SUCCESS: Cloudflare Token upgraded with Zaraz/Settings scopes.")
    else:
        print(f"❌ ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    upgrade_token()

