import requests
import json

CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
CLOUDFLARE_API_KEY = "6094d6fa8c138d93409de2f59a3774cd8795a"
TOKEN_ID = "d5cc4a77c18eb32fbd8e6df239eb1105"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def update_token():
    url = f"https://api.cloudflare.com/client/v4/user/tokens/{TOKEN_ID}"
    
    # We define the new policies
    # Permission IDs from previous step:
    # Zaraz Read: 5bdbde7e76144204a244274eac3eb0eb
    # Zone Read: c8fed203ed3043cba015a93ad1616f1f
    # Zone Settings Read: 517b21aee92c4d89936c976ba6e4be55
    # Zone DNS Settings Write (Existing): c4df38be41c247b3b4b7702e76eadae0
    # API Tokens Write (Existing): 686d18d5ac6c441c867cbf6771e58a0a
    
    payload = {
        "name": "Editar zona DNS (Senior Audited)",
        "status": "active",
        "policies": [
            {
                "effect": "allow",
                "resources": {"com.cloudflare.api.account.zone.*": "*"},
                "permission_groups": [
                    {"id": "c8fed203ed3043cba015a93ad1616f1f"}, # Zone Read
                    {"id": "517b21aee92c4d89936c976ba6e4be55"}, # Zone Settings Read
                    {"id": "5bdbde7e76144204a244274eac3eb0eb"}, # Zaraz Read
                    {"id": "c4df38be41c247b3b4b7702e76eadae0"}, # Zone DNS Settings Write
                ]
            },
            {
                "effect": "allow",
                "resources": {"com.cloudflare.api.user.*": "*"},
                "permission_groups": [
                    {"id": "686d18d5ac6c441c867cbf6771e58a0a"} # API Tokens Write
                ]
            }
        ]
    }
    
    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        print("✅ SUCCESS: Token updated with Senior permissions.")
    else:
        print(f"❌ ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    update_token()
