#!/usr/bin/env python3
import os
import requests  # noqa: F401

def audit_zaraz():
    print("📊 [Zaraz Auditor] Iniciando análisis de arquitectura de tracking...")
    
    # 1. Verificar variables de entorno CAPI
    env_path = "/home/jorand/antigravityobuntu/.env"
    capi_keys = ["META_PIXEL_ID", "META_ACCESS_TOKEN"]
    missing_keys = []
    
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()
            for key in capi_keys:
                if key not in content:
                    missing_keys.append(key)
    
    if not missing_keys:
        print("✅ Meta CAPI credentials detected in .env.")
    else:
        print(f"❌ Missing Meta CAPI keys: {', '.join(missing_keys)}")

    # 2. Verificar Engine en el Frontend
    tracking_engine_path = (
        "/home/jorand/antigravityobuntu/static/engines/tracking/index.js"
    )
    if os.path.exists(tracking_engine_path):
        with open(tracking_engine_path, "r") as f:
            content = f.read()
            if "Zaraz" in content or "zaraz" in content:
                print("✅ TrackingEngine logic includes Zaraz awareness.")
            else:
                print("⚠️ TrackingEngine source might lack deep Zaraz integration.")
    else:
        print("❌ TrackingEngine not found at expected path.")

    # 3. Verificar Configuración Global
    tracking_config = "/home/jorand/antigravityobuntu/static/engines/tracking/config.js"
    if os.path.exists(tracking_config):
        print("✅ Tracking configuration file exists.")
    else:
        print("❌ Tracking configuration file missing.")

    print("\n[FIN] Informe de integridad de tracking generado.")

if __name__ == "__main__":
    audit_zaraz()
