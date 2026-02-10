import os
import requests
import json
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Credentials from user or .env
EMAIL = "Acordero629@gmail.com"
GLOBAL_KEY = "6094d6fa8c138d93409de2f59a3774cd8795a"
ZONE_ID = "19bd9bdd7abf8f74b4e95d75a41e8583"
ACCOUNT_ID = "18d305c823dc9ab6f0663bde930a9fc2"

# FORCE Global API Key for token creation
HEADERS = {
    "X-Auth-Email": EMAIL,
    "X-Auth-Key": GLOBAL_KEY,
    "Content-Type": "application/json"
}
print(f"DEBUG: Using Global API Key for authentication (Email: {EMAIL}).")

def deploy_token():
    url = "https://api.cloudflare.com/client/v4/user/tokens"
    
    # 1. Fetch permission groups
    print("🔍 Fetching permission groups...")
    groups_resp = requests.get(f"{url}/permission_groups", headers=HEADERS)
    
    permission_ids = {}
    if groups_resp.status_code == 200:
        groups = groups_resp.json().get("result", [])
        print("✅ Permissions fetched dynamically.")
        
        # Mapping names to IDs
        mapping = {
            "Zaraz Write": "Zaraz",
            "Workers Scripts Write": "Workers Scripts",
            "Workers Tail Read": "Workers Tail",
            "Pages Write": "Pages",
            "Analytics Read": "Analytics",
            "DNS Write": "DNS",
            "Zone Settings Write": "Zone Settings",
            "Cache Purge": "Cache Purge"
        }
        
        for g in groups:
            for clean_name, search_name in mapping.items():
                if search_name in g['name'] and ("Edit" in g['name'] or "Write" in g['name'] or "Purge" in g['name'] or "Read" in g['name']):
                     permission_ids[clean_name] = g['id']
    else:
        print("⚠️ Failed to fetch groups dynamically. Using fallback.")
        # Fallback known IDs (Account Level)
        permission_ids = {
             "Zaraz Write": "3845d475ce30419280d859e4b6b6f79d",
             "Workers Scripts Write": "0a68d01a09d64fc599b6623bc90700d2",
             "DNS Write": "c4df38be41c247b3b4b7702e76eadae0"
        }

    # 2. Define the payload
    payload = {
        "name": "Senior God Mode (Zaraz + Sales + Optimization)",
        "status": "active",
        "policies": [
            {
                "effect": "allow",
                "resources": {f"com.cloudflare.api.account.{ACCOUNT_ID}": "*"},
                "permission_groups": [{"id": pid} for pid in permission_ids.values()]
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

    print("🚀 Creating the token...")
    resp = requests.post(url, headers=HEADERS, json=payload)
    
    if resp.status_code == 201:
        result = resp.json().get("result", {})
        token_value = result.get("value")
        print("\n" + "="*50)
        print("✨ SUCCESS: God Mode Token Created!")
        print(f"TOKEN_ID: {result.get('id')}")
        print(f"VALUE: {token_value}")
        print("="*50)
        print("\nIMPORTANT: Copy the VALUE and save it in your .env as CLOUDFLARE_GOD_TOKEN")
    else:
        print(f"\n❌ ERROR creating token: {resp.status_code} - {resp.json()}")

if __name__ == "__main__":
    deploy_token()
