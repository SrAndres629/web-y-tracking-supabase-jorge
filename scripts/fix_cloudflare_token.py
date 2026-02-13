import requests
import json

CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
CLOUDFLARE_API_KEY = "CLOUDFLARE_API_KEY_REEMPLAZAR"
TOKEN_ID = "d5cc4a77c18eb32fbd8e6df239eb1105"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def fix_token():
    url = f"https://api.cloudflare.com/client/v4/user/tokens/{TOKEN_ID}"
    
    # Permission IDs:
    # Zaraz Read: 5bdbde7e76144204a244274eac3eb0eb
    # Zone Read: c8fed203ed3043cba015a93ad1616f1f
    # Zone Settings Read: 517b21aee92c4d89936c976ba6e4be55
    # API Tokens Write: 686d18d5ac6c441c867cbf6771e58a0a
    
    payload = {
        "name": "Editar zona DNS (Senior Audited)",
        "status": "active",
        "policies": [
            {
                "effect": "allow",
                "resources": {"com.cloudflare.api.account.18d305c823dc9ab6f0663bde930a9fc2": "*"},
                "permission_groups": [
                    {"id": "686d18d5ac6c441c867cbf6771e58a0a"}, # API Tokens Write (User level but often works here)
                    {"id": "c8fed203ed3043cba015a93ad1616f1f"}, # Zone Read
                    {"id": "517b21aee92c4d89936c976ba6e4be55"}, # Zone Settings Read
                    {"id": "5bdbde7e76144204a244274eac3eb0eb"}, # Zaraz Read
                ]
            },
            {
                "effect": "allow",
                "resources": {"com.cloudflare.api.user.*": "*"},
                "permission_groups": [
                    {"id": "686d18d5ac6c441c867cbf6771e58a0a"} # API Tokens Write
                ]
            }
        ],
        "condition": None # REMOVE IP RESTRICTION
    }
    
    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        print("✅ SUCCESS: Cloudflare Token corrected (IP Lock removed + Zaraz scopes added).")
    else:
        print(f"❌ ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    fix_token()

