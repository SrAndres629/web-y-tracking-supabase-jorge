import os
import sys
import time
import requests
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

import subprocess
from dotenv import load_dotenv

# Cargar .env antes de cualquier cosa
load_dotenv()

# --- CONFIGURACIÓN (Carga desde variables de entorno para seguridad) ---
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')
PIXEL_ID = os.getenv('META_PIXEL_ID')
SITE_URL = os.getenv('SITE_URL', "https://jorgeaguirreflores.com")

def check_lighthouse():
    """Ejecuta Lighthouse CLI si está disponible."""
    print_status("Iniciando auditoría de Lighthouse (LCP/CLS)...", "INFO")
    try:
        # Usar --quiet para no ensuciar la terminal
        cmd = ["lighthouse", SITE_URL, "--quiet", "--chrome-flags='--headless'", "--only-categories=performance", "--output=json"]
        # Solo verificar si el comando existe primero
        subprocess.run(["lighthouse", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        start = time.time()
        # No guardamos el JSON por ahora, solo validamos que corra y el tiempo
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        duration = time.time() - start
        
        if result.returncode == 0:
            print_status(f"Lighthouse completado en {duration:.2f}s", "OK")
            # Podríamos parsear el JSON aquí para dar el Score exacto
        else:
            print_status("Lighthouse falló o devolvió error", "WARN")
    except Exception:
        print_status("Lighthouse CLI no instalado (`npm install -g lighthouse`)", "INFO")

def print_status(message, status="INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌", "CRITICAL": "🔥"}
    print(f"{icons.get(status, '')} [{status}] {message}")

def audit_infrastructure():
    print("--- 🕵️‍♂️ INICIANDO AUDITORÍA DE INFRAESTRUCTURA DE MARKETING (MVP) ---")
    
    # 0. PERFORMANCE DEEP AUDIT
    check_lighthouse()
    
    # 1. AUDITORÍA DE VELOCIDAD Y DISPONIBILIDAD (Vital para CPM bajo)
    try:
        start_time = time.time()
        response = requests.get(SITE_URL, timeout=10)
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            print_status(f"Sitio web online ({response.status_code})", "OK")
            print_status(f"Tiempo de respuesta: {load_time:.2f}s", "INFO")
            
            if load_time < 1.0:
                print_status("Velocidad: EXCELENTE (CPM optimizado)", "OK")
            elif load_time < 2.5:
                print_status("Velocidad: ACEPTABLE", "WARN")
            else:
                print_status("Velocidad: CRÍTICA (>2.5s). El CPC subirá.", "CRITICAL")
                
            # Verificar Pixel en el HTML (Lado Cliente)
            if "fbevents.js" in response.text or (PIXEL_ID and str(PIXEL_ID) in response.text):
                print_status("Pixel de Meta detectado en el código fuente (Cliente)", "OK")
            else:
                print_status("No se encuentra el script del Pixel en el HTML", "ERROR")
        else:
            print_status(f"El sitio devolvió error: {response.status_code}", "CRITICAL")
            return False

    except Exception as e:
        print_status(f"Error conectando al sitio: {e}", "CRITICAL")
        return False

    # 2. AUDITORÍA DE API DE CONVERSIONES (CAPI) (Vital para no perder ventas)
    if not ACCESS_TOKEN or not AD_ACCOUNT_ID:
        print_status("Faltan credenciales de Meta en el entorno (.env)", "WARN")
        print("   -> Exporta META_ACCESS_TOKEN y META_AD_ACCOUNT_ID para probar CAPI.")
    else:
        try:
            FacebookAdsApi.init(access_token=ACCESS_TOKEN)
            account = AdAccount(AD_ACCOUNT_ID)
            pixels = account.get_ads_pixels()
            
            pixel_found = False
            for pixel in pixels:
                if PIXEL_ID and pixel['id'] == PIXEL_ID:
                    pixel_found = True
                    print_status(f"Conexión CAPI establecida con Pixel: {pixel['name']} (ID: {pixel['id']})", "OK")
                    break
            
            if not pixel_found and PIXEL_ID:
                print_status(f"El Token es válido pero no tiene acceso al Pixel {PIXEL_ID}", "ERROR")
            elif not PIXEL_ID:
                print_status("META_PIXEL_ID no definido, conexión básica a cuenta exitosa.", "OK")

        except Exception as e:
            print_status(f"Fallo crítico en conexión con Meta Ads: {e}", "ERROR")

    print("\n--- 🏁 CONCLUSIÓN ---")
    print("Si ves todo en VERDE, tu infraestructura técnica soporta escalar la inversión.")

if __name__ == "__main__":
    audit_infrastructure()
