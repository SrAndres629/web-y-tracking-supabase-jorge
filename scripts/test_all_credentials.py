import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# List of credentials to test
CREDENTIALS = [
    {
        "name": "User Provided Token (7kVI...)",
        "token": "7kVIFNy4qq0wwUgC82czs8kzMeYxNgIIoV9cvReL",
        "type": "token"
    },
    {
        "name": "Found Token (_f1Q...)",
        "token": "_f1QrJImGK0Qg5eSACM1DGnkF6xd9yRMGGXvGUA8",
        "type": "token"
    },
    {
        "name": "User Provided Global Key (6094...)",
        "email": "Acordero629@gmail.com",
        "key": "6094d6fa8c138d93409de2f59a3774cd8795a",
        "type": "global"
    },
    {
        "name": ".env Global Key (d2e7...)",
        "email": "Acordero629@gmail.com",
        "key": "d2e7046c39d277ae1e1d2afa9eccd2058c860",
        "type": "global"
    },
    {
        "name": ".env API Token (if any)",
        "token": os.getenv("CLOUDFLARE_API_TOKEN"),
        "type": "token"
    }
]

def test_credential(cred):
    if cred["type"] == "token":
        if not cred["token"]: return None
        headers = {
            "Authorization": f"Bearer {cred['token']}",
            "Content-Type": "application/json"
        }
    else:
        if not cred["key"] or not cred["email"]: return None
        headers = {
            "X-Auth-Email": cred["email"],
            "X-Auth-Key": cred["key"],
            "Content-Type": "application/json"
        }

    print(f"\n--- Testing: {cred['name']} ---")
    
    # 1. Verify Authentication
    verify_url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
    if cred["type"] == "global":
        verify_url = "https://api.cloudflare.com/client/v4/user" # Global key verify
        
    try:
        resp = requests.get(verify_url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ Auth Success!")
            # 2. Test Zone Access
            zones_resp = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers, timeout=10)
            if zones_resp.status_code == 200:
                zones = zones_resp.json().get("result", [])
                print(f"✅ Zone Access: Found {len(zones)} zones.")
                for z in zones[:2]:
                    print(f"   - {z['name']} ({z['id']})")
            else:
                print(f"❌ Zone Access Failure: {zones_resp.status_code}")
                
            # 3. Test Token Management (If applicable)
            if cred["type"] == "global" or "Token" in cred["name"]:
                token_perms_url = "https://api.cloudflare.com/client/v4/user/tokens/permission_groups"
                perms_resp = requests.get(token_perms_url, headers=headers, timeout=10)
                if perms_resp.status_code == 200:
                    print(f"✅ Token Management: Can list permissions.")
                else:
                    print(f"❌ Token Management Failure: {perms_resp.status_code}")
        else:
            print(f"❌ Auth Failure: {resp.text}")
    except Exception as e:
        print(f"💥 Request Error: {e}")

if __name__ == "__main__":
    for c in CREDENTIALS:
        test_credential(c)
