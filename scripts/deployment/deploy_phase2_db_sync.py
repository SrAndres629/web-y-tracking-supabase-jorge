import asyncio
import os
import sys

# Agregamos la ruta del proyecto actual para importar app.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.infrastructure.persistence.database import db

# Force PostgreSQL backend
db._backend = "postgres"

def run_migrations():
    print("🚀 Iniciando migración en producción (Supabase)...")
    
    # 1. Asegurar esquema básico (creará tablas faltantes o alterará si es seguro, init_tables usa CREATE TABLE IF NOT EXISTS)
    print("📦 Ejecutando init_tables()...")
    db.init_tables()
    print("✅ Schema básico asegurado.")

    # 2. Aplicar Row Level Security (RLS)
    print("🔒 Aplicando Row Level Security (RLS) policies...")
    rls_queries = [
        # Activar RLS en todas las tablas
        "ALTER TABLE crm_leads ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE visitors ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE events ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE emq_scores ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE clients ENABLE ROW LEVEL SECURITY;",

        # Eliminar politicas viejas si existen
        "DROP POLICY IF EXISTS \"Service role full access on crm_leads\" ON crm_leads;",
        "DROP POLICY IF EXISTS \"Service role full access on visitors\" ON visitors;",
        "DROP POLICY IF EXISTS \"Service role full access on events\" ON events;",
        "DROP POLICY IF EXISTS \"Service role full access on api_keys\" ON api_keys;",
        
        # Crear política de acceso total solo para service_role
        "CREATE POLICY \"Service role full access on crm_leads\" ON crm_leads FOR ALL USING (auth.role() = 'service_role');",
        "CREATE POLICY \"Service role full access on visitors\" ON visitors FOR ALL USING (auth.role() = 'service_role');",
        "CREATE POLICY \"Service role full access on events\" ON events FOR ALL USING (auth.role() = 'service_role');",
        "CREATE POLICY \"Service role full access on api_keys\" ON api_keys FOR ALL USING (auth.role() = 'service_role');"
    ]
    
    # Fetch URL from settings
    url = db._settings.db.url
    if url and "?" in url:
        url = url.split("?")[0]
        
    import psycopg2
    conn = psycopg2.connect(url, sslmode="require")
    try:
        cur = conn.cursor()
        for query in rls_queries:
            try:
                cur.execute(query)
                print(f"✅ RLS Policy Executed: {query[:50]}...")
            except Exception as e:
                print(f"⚠️ Nota de RLS (ignorando si ya existe): {e}")
        conn.commit()
    finally:
        cur.close()
        conn.close()
        
    print("🎉 Migraciones de Producción Completadas y Políticas RLS Aplicadas Exitosamente.")

if __name__ == "__main__":
    run_migrations()
