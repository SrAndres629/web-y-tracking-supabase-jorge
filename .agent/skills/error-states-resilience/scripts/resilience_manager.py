#!/usr/bin/env python3
import os
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
TEMPLATES_DIR = os.path.join(ROOT, 'api/templates')

def check_error_pages():
    """Verifica si existen templates personalizados de error."""
    errors = []
    required_pages = ['errors/404.html', 'errors/500.html']
    
    for page in required_pages:
        path = os.path.join(TEMPLATES_DIR, page)
        if not os.path.exists(path):
            errors.append(f"[RESILIENCE WARNING] Falta el template de error personalizado: {page}")
        else:
            errors.append(f"OK: Template {page} detectado.")
    return errors

def run_resilience_audit():
    print("======== INFORME DE ROBUSTEZ Y RESILIENCIA ========")
    
    print("\n[ERRORS] Páginas de Fallo:")
    for res in check_error_pages():
        print(f"  {res}")
        
    print("\n[ESTADO FINAL] Auditoría de resiliencia completada.")
    print("=====================================================")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "audit":
        run_resilience_audit()
    else:
        print("Comando no reconocido.")
