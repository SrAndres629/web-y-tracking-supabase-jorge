#!/usr/bin/env python3
import os
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
TEMPLATES_DIR = os.path.join(ROOT, 'api/templates')
STATIC_DIR = os.path.join(ROOT, 'static')

def check_lazy_loading():
    """Busca imágenes que no tengan lazy-loading (excluyendo el hero)."""
    warnings = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            # Excluir hero ya que debe cargar rápido
            if file.endswith('.html') and 'hero.html' not in file:
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '<img' in content and 'loading="lazy"' not in content:
                        rel_path = os.path.relpath(path, ROOT)
                        msg = f"[PERF WARNING] Imágenes sin lazy-loading en {rel_path}"
                        warnings.append(msg)
    return warnings if warnings else ["OK: Lazy-loading implementado."]

def check_scripts_blocking():
    """Detecta scripts que bloquean el renderizado."""
    warnings = []
    base_layout = os.path.join(TEMPLATES_DIR, 'layouts/base.html')
    if os.path.exists(base_layout):
        with open(base_layout, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<script' in content and 'src=' in content:
                if 'defer' not in content and 'async' not in content:
                    msg = "[PERF WARNING] Se detectaron scripts síncronos en base.html."
                    warnings.append(msg)
    return warnings if warnings else ["OK: Scripts optimizados (defer/async)."]

def check_image_formats():
    """Busca imágenes en formatos antiguos (PNG/JPG) sin WebP."""
    warnings = []
    for root, dirs, files in os.walk(STATIC_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Verificar si existe una version .webp
                webp_path = os.path.splitext(os.path.join(root, file))[0] + '.webp'
                if not os.path.exists(webp_path):
                    rel_path = os.path.relpath(os.path.join(root, file), ROOT)
                    warnings.append(f"[PERF WARNING] {rel_path} no tiene version WebP.")
    return warnings if warnings else ["OK: Cobertura de WebP completa."]

def run_perf_audit():
    print("======== INFORME DE OPTIMIZACIÓN DE PERFORMANCE ========")
    
    print("\n[ENTREGA] Imagenes & Lazy-loading:")
    for res in check_lazy_loading():
        print(f"  {res}")
        
    print("\n[INTERFACES] Estabilidad & Bloqueo:")
    for msg in check_scripts_blocking():
        print(f"  {msg}")

    print("\n[ASSETS] Formatos Modernos:")
    for msg in check_image_formats():
        if "node_modules" not in msg:
            print(f"  {msg}")

    print("\n[ESTADO FINAL] Auditoría de performance completada.")
    print("========================================================")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "audit":
        run_perf_audit()
    else:
        print("Comando no reconocido.")
