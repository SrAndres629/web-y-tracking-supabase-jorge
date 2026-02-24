#!/usr/bin/env python3
import os

def audit_turnstile():
    print("🛡️ [Anti-Bot Auditor] Iniciando revisión de seguridad...")
    
    # 1. Check .env
    env_path = "/home/jorand/antigravityobuntu/.env"
    has_site_key = False
    has_secret_key = False
    
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()
            if "TURNSTILE_SITE_KEY" in content and "0x4" in content:
                has_site_key = True
            if "TURNSTILE_SECRET_KEY" in content and "0x4" in content:
                has_secret_key = True
    
    if has_site_key and has_secret_key:
        print("✅ Configuración de .env detectada y válida.")
    else:
        print("❌ Error: Faltan llaves de Turnstile en .env o tienen formato inválido.")

    # 2. Check Templates
    base_html = "/home/jorand/antigravityobuntu/api/templates/layouts/base.html"
    if os.path.exists(base_html):
        with open(base_html, "r") as f:
            content = f.read()
            if "cf-turnstile" in content and "onTurnstileSuccess" in content:
                print("✅ Widget global detectado en base.html.")
            else:
                print("⚠️ Advertencia: No se detectó el widget en base.html.")

    # 3. Check Backend
    tracking_routes = (
        "/home/jorand/antigravityobuntu/app/interfaces/api/routes/tracking.py"
    )
    if os.path.exists(tracking_routes):
        with open(tracking_routes, "r") as f:
            content = f.read()
            if "validate_turnstile" in content:
                print("✅ Validación en el servidor detectada en tracking.py.")
            else:
                msg = "⚠️ Advertencia: No se detectó validación en tracking.py."
                print(msg)

    print("\n🚀 Auditoría finalizada.")

if __name__ == "__main__":
    audit_turnstile()
