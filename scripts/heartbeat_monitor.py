import requests
import sys
import os

# =================================================================
# 💓 SILICON VALLEY HEARTBEAT MONITOR
# =================================================================
# This script performs external health validation of the production stack.
# Designed to be triggered by GitHub Actions or a local Cron job.

# Configuración
TARGET_URL = "https://jorgeaguirreflores.com/health"
# Opcional: Webhook de Discord/Slack para avisar
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL") 

def send_alert(message):
    print(f"🚨 ALERTA: {message}")
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": f"🔥 **SISTEMA CAÍDO [jorgeaguirreflores.com]:** {message}"}, timeout=5)
        except Exception as e:
            print(f"Failed to send Discord alert: {e}")

def run_check():
    try:
        print(f"🔍 Probing {TARGET_URL}...")
        response = requests.get(TARGET_URL, timeout=15)
        
        # 1. HTTP Status Check (L1)
        if response.status_code != 200:
            send_alert(f"HTTP Error: {response.status_code}")
            sys.exit(1)
            
        data = response.json()
        
        # 2. Logic Check (L2 - Database & Redis)
        if data.get("status") != "ok":
            details = data.get("details", {})
            db_status = details.get("database", "unknown")
            redis_status = details.get("redis", "unknown")
            msg = f"Internal Logic Failure - DB: {db_status}, Redis: {redis_status}"
            send_alert(msg)
            sys.exit(1)

        print("✅ HEARTBEAT OK: Diamond Standard Maintained.")
        return True

    except requests.exceptions.Timeout:
        send_alert("Timeout (15s) reached. The site is likely hanging.")
        sys.exit(1)
    except Exception as e:
        send_alert(f"Connectivity Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_check()
