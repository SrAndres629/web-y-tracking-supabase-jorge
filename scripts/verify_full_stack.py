import sys
import os
import logging
from dotenv import load_dotenv

# Configurar path para importar desde 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno locales
load_dotenv()

# Configurar logging visual
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Guardian")

def check_mark(success):
    return "✅" if success else "❌"

def verify_system():
    print("\n🛡️  INICIANDO PROTOCOLO DE VERIFICACIÓN (AGENTE 2)...\n")
    all_systems_go = True

    # 1. VERIFICACIÓN DE ENTORNO
    print("--- 1. AUDITORÍA DE VARIABLES DE ENTORNO ---")
    required_vars = ["DATABASE_URL", "META_PIXEL_ID", "META_ACCESS_TOKEN"]
    for var in required_vars:
        value = os.getenv(var)
        status = bool(value)
        if not status: all_systems_go = False
        print(f"{check_mark(status)} {var}: {'CONFIGURADO' if status else 'FALTA'}")
    
    # 2. VERIFICACIÓN DE BASE DE DATOS
    print("\n--- 2. CONECTIVIDAD DE BASE DE DATOS ---")
    try:
        from app.database import initialize
        # Rename internal call to match provided interface if needed or use initialize()
        # Since I'm the DevOps engineer, I'll adapt the check to use what exists.
        db_status = initialize()
        if not db_status: all_systems_go = False
        print(f"{check_mark(db_status)} Conexión PostgreSQL/SQLite: {'ESTABLE' if db_status else 'FALLÓ'}")
    except Exception as e:
        print(f"❌ Error crítico importando DB: {e}")
        all_systems_go = False

    # 3. VERIFICACIÓN DE DEPENDENCIAS CRÍTICAS
    print("\n--- 3. DEPENDENCIAS DE TRACKING ---")
    try:
        import facebook_business
        print(f"✅ Librería Meta Business SDK: INSTALADA")
    except ImportError as e:
        print(f"❌ Falta dependencia crítica: {e.name}")
        all_systems_go = False
        
    try:
        import redis
        print(f"✅ Redis (para Celery/Cache): INSTALADO")
    except ImportError as e:
        print(f"⚠️  Info: Redis no instalado (opcional si no se usa Celery en local)")

    # RESUMEN FINAL
    print("\n" + "="*40)
    if all_systems_go:
        print("🚀 SISTEMA LISTO PARA EJECUCIÓN LOCAL")
        print("   Ejecuta: uvicorn main:app --reload")
    else:
        print("⚠️  SE ENCONTRARON ERRORES. NO DESPLEGAR AÚN.")
    print("="*40 + "\n")

if __name__ == "__main__":
    verify_system()
