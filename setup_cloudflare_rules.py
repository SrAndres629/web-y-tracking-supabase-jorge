import requests
import json

# --- CONFIGURATION (Same as git_sync.py) ---
CLOUDFLARE_ZONE_ID = "19bd9bdd7abf8f74b4e95d75a41e8583"
CLOUDFLARE_API_KEY = "6094d6fa8c138d93409de2f59a3774cd8795a"
CLOUDFLARE_EMAIL = "Acordero629@gmail.com"
# -------------------------------------------------------

BASE_URL = "https://api.cloudflare.com/client/v4"
HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def list_page_rules():
    print("🔍 Listing existing Page Rules...")
    url = f"{BASE_URL}/zones/{CLOUDFLARE_ZONE_ID}/pagerules"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        rules = response.json().get("result", [])
        for rule in rules:
            print(f"   - Rule: {rule['targets'][0]['constraint']['value']} -> {[a['id'] for a in rule['actions']]}")
        return rules
    else:
        print(f"❌ Error listing rules: {response.text}")
        return []

def create_cache_everything_rule():
    print("\n🚀 Activating 'Cache Everything' (Silicon Valley Standard)...")
    url = f"{BASE_URL}/zones/{CLOUDFLARE_ZONE_ID}/pagerules"
    
    # Rule: Cache Everything for the domain
    payload = {
        "targets": [
            {
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": "*jorgeaguirreflores.com/*"
                }
            }
        ],
        "actions": [
            {
                "id": "cache_level",
                "value": "cache_everything"
            },
            {
                "id": "edge_cache_ttl",
                "value": 604800  # 7 Days (We rely on git_sync.py purge)
            },
            {
                "id": "browser_cache_ttl",
                "value": 14400  # 4 Hours (Free Plan Minimum is usually restrictive)
            }
        ],
        "priority": 1,
        "status": "active"
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    data = response.json()
    
    if data.get("success"):
        print("✅ SUCCESS: Cache Everything rule is ACTIVE.")
        print("🌍 Your site is now served from the Edge.")
    else:
        print(f"⚠️ Failed to create rule: {data.get('errors')}")
        print(f"📄 Messages: {data.get('messages')}")

def create_vercel_bypass_rule():
    print("\n🛡️ Securing Vercel Analytics (Bypass Cache)...")
    url = f"{BASE_URL}/zones/{CLOUDFLARE_ZONE_ID}/pagerules"
    
    payload = {
        "targets": [
            {
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": "*jorgeaguirreflores.com/_vercel/*"
                }
            }
        ],
        "actions": [
            {
                "id": "cache_level",
                "value": "bypass"
            },
            {
                "id": "disable_performance"  # Ensure raw script delivery
            }
        ],
        "priority": 1,
        "status": "active"
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    data = response.json()
    
    if data.get("success"):
        print("✅ SUCCESS: Vercel Analytics safeguarded.")
    else:
        print(f"⚠️ Failed to create Vercel rule: {data.get('errors')}")

if __name__ == "__main__":
    current_rules = list_page_rules()
    
    # Check if rule already exists to avoid duplicates
    exists = False
    for rule in current_rules:
        target = rule['targets'][0]['constraint']['value']
        if "jorgeaguirreflores.com/*" in target:
            actions = [a['id'] for a in rule['actions']]
            if "cache_level" in actions:
                print(f"ℹ️ Rule already exists for {target}. Skipping creation.")
                exists = True
                break
    
    if not exists:
        create_cache_everything_rule()
        
    # Check for Vercel rule
    vercel_exists = False
    for rule in current_rules:
        target = rule['targets'][0]['constraint']['value']
        if "_vercel/*" in target:
            print(f"ℹ️ Rule already exists for {target}. Skipping.")
            vercel_exists = True
            break
            
    if not vercel_exists:
        create_vercel_bypass_rule()
