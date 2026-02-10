import requests
import os

CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
CLOUDFLARE_API_KEY = "6094d6fa8c138d93409de2f59a3774cd8795a"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def list_tokens():
    url = "https://api.cloudflare.com/client/v4/user/tokens"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        tokens = resp.json().get("result", [])
        print(f"DEBUG: Found {len(tokens)} tokens.")
        for t in tokens:
            print(f"ID: {t['id']} | Name: {t['name']} | Status: {t['status']}")
            for p in t.get('policies', []):
                print(f"  - Policy: {p.get('permission_groups', [])}")
        return tokens
    else:
        print(f"ERROR: {resp.status_code} - {resp.text}")
        return []

if __name__ == "__main__":
    list_tokens()
