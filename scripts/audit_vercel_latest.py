import os
import requests
import json
from dotenv import load_dotenv, find_dotenv
import sys

# Ensure we look in the project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(find_dotenv())

VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
VERCEL_PROJECT_ID = os.getenv("VERCEL_PROJECT_ID")
VERCEL_TEAM_ID = os.getenv("VERCEL_TEAM_ID")

def get_latest_deployment():
    url = f"https://api.vercel.com/v6/deployments?projectId={VERCEL_PROJECT_ID}&teamId={VERCEL_TEAM_ID}&limit=1"
    headers = {"Authorization": f"Bearer {VERCEL_TOKEN}"}
    
    try:
        print(f"🔍 Querying Vercel API for Project: {VERCEL_PROJECT_ID}...")
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"❌ API Error: {resp.status_code} - {resp.text}")
            return None
            
        data = resp.json()
        if not data.get("deployments"):
            print("⚠️ No deployments found.")
            return None
            
        latest = data["deployments"][0]
        print(f"\n🏷️  Deployment: {latest['url']}")
        print(f"🆔 ID: {latest['uid']}")
        print(f"🚦 State: {latest['state']}")
        print(f"📅 Created: {latest['created']}")
        print(f"❌ Error Code: {latest.get('error', {}).get('code', 'None')}")
        print(f"❌ Error Message: {latest.get('error', {}).get('message', 'None')}")
        
        return latest['uid']
    except Exception as e:
        print(f"🔥 Exception: {e}")
        return None

def get_build_logs(deployment_id):
    if not deployment_id: return
    
    url = f"https://api.vercel.com/v2/deployments/{deployment_id}/events?teamId={VERCEL_TEAM_ID}&direction=backward"
    headers = {"Authorization": f"Bearer {VERCEL_TOKEN}"}
    
    print(f"\n📜 Fetching Build Logs for {deployment_id}...")
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Log Error: {resp.status_code} - {resp.text}")
            return
            
        logs = resp.json()
        print("\n--- BUILD LOG START ---")
        for log in reversed(logs): # Chronological order
            text = log.get("text", "")
            if "error" in text.lower() or "failed" in text.lower():
                 print(f"🔴 {text.strip()}")
            else:
                 print(f"⚪ {text.strip()}")
        print("--- BUILD LOG END ---\n")
        
    except Exception as e:
        print(f"🔥 Log Exception: {e}")

if __name__ == "__main__":
    uid = get_latest_deployment()
    if uid:
        get_build_logs(uid)
