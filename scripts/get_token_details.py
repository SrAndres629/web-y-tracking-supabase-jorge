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

def get_token_details():
    url = f"https://api.cloudflare.com/client/v4/user/tokens/{TOKEN_ID}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        print(json.dumps(resp.json().get("result", {}), indent=2))
    else:
        print(f"ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    get_token_details()

