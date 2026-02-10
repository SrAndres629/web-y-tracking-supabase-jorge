import requests
import json

CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
CLOUDFLARE_API_KEY = "6094d6fa8c138d93409de2f59a3774cd8795a"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def list_permission_groups():
    url = "https://api.cloudflare.com/client/v4/user/tokens/permission_groups"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        groups = resp.json().get("result", [])
        # We search for relevant ones
        relevant = ["Zone", "Zaraz", "Analytics", "Settings"]
        for g in groups:
            if any(r in g['name'] for r in relevant):
                print(f"ID: {g['id']} | Name: {g['name']}")
    else:
        print(f"ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    list_permission_groups()
