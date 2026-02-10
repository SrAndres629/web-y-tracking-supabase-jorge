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

def minimal_fix():
    url = f"https://api.cloudflare.com/client/v4/user/tokens/{TOKEN_ID}"
    
    # Get current state
    curr = requests.get(url, headers=HEADERS).json().get("result", {})
    
    # Preserve name and policies, but drop condition
    payload = {
        "name": curr.get("name"),
        "status": "active",
        "policies": curr.get("policies"),
        "condition": None
    }
    
    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        print("✅ SUCCESS: IP Restriction removed from token.")
    else:
        print(f"❌ ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    minimal_fix()
