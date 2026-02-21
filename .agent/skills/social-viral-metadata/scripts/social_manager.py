#!/usr/bin/env python3
import os
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
TEMPLATES_DIR = os.path.join(ROOT, 'api/templates')

def check_social_tags():
    """Verifica la presencia de etiquetas Meta para Redes Sociales."""
    errors = []
    base_layout = os.path.join(TEMPLATES_DIR, 'layouts/base.html')
    
    required_tags = [
        'og:title', 'og:description', 'og:image',
        'twitter:card', 'twitter:title'
    ]
    
    if os.path.exists(base_layout):
        with open(base_layout, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            for tag in required_tags:
                if tag not in content:
                    errors.append(f"[SOCIAL WARNING] Falta la etiqueta: {tag}")
                else:
                    errors.append(f"OK: Tag {tag} detectado.")
    return errors

def run_social_audit():
    print("======== INFORME DE METADATOS SOCIALES ========")
    
    print("\n[OPENGRAPH] Tags de Redes Sociales:")
    for res in check_social_tags():
        print(f"  {res}")
        
    print("\n[ESTADO FINAL] Auditoría social completada.")
    print("===============================================")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "audit":
        run_social_audit()
    else:
        print("Comando no reconocido.")
