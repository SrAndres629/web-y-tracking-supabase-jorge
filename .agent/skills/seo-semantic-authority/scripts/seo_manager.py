#!/usr/bin/env python3
import os
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
TEMPLATES_DIR = os.path.join(ROOT, "api/templates")


def check_schema_presence():
    """Verifica si existe el bloque de datos estructurados JSON-LD."""
    errors = []
    base_layout = os.path.join(TEMPLATES_DIR, "layouts/base.html")

    found = False
    if os.path.exists(base_layout):
        with open(base_layout, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "application/ld+json" in content or 'type="ld+json"' in content:
                found = True

    if not found:
        errors.append("[SEO WARNING] No se detectó JSON-LD (Schema.org) en base.html.")
    else:
        errors.append("OK: JSON-LD detectado.")
    return errors


def check_heading_hierarchy():
    """Analiza la jerarquía de encabezados básica."""
    warnings = []
    for root, _dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    h1_count = content.count("<h1")
                    if h1_count > 1:
                        rel_path = os.path.relpath(path, ROOT)
                        warnings.append(f"[SEO WARNING] Múltiples H1 ({h1_count}) en {rel_path}.")
    return warnings if warnings else ["OK: Jerarquía de encabezados (H1) controlada."]


def run_seo_audit():
    print("======== INFORME DE AUTORIDAD SEMÁNTICA (SEO) ========")

    print("\n[SCHEMA] Datos Estructurados:")
    for res in check_schema_presence():
        print(f"  {res}")

    print("\n[ESTRUCTURA] Jerarquía Semántica:")
    for msg in check_heading_hierarchy():
        print(f"  {msg}")

    print("\n[ESTADO FINAL] Auditoría SEO completada.")
    print("======================================================")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "audit":
        run_seo_audit()
    else:
        print("Comando no reconocido.")
