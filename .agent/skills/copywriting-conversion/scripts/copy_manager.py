#!/usr/bin/env python3
import os
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
TEMPLATES_DIR = os.path.join(ROOT, "api/templates")


def check_authority_mentions():
    """Verifica si se menciona la autoridad (30 años) en los templates principales."""
    errors = []
    # Archivos críticos para la autoridad
    critical_files = ["sections/hero.html", "components/navbar.html", "sections/services.html"]

    found = False
    for rel_path in critical_files:
        path = os.path.join(TEMPLATES_DIR, rel_path)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                if "30 años" in content or "30 years" in content:
                    found = True
                    break

    if not found:
        msg = "[COPY WARNING] Falta resaltar la autoridad (30 años) en secciones críticas."
        errors.append(msg)
    return errors if errors else ["OK: Autoridad de 30 años detectada."]


def check_generic_ctas():
    """Busca CTAs genéricos que reducen la conversión."""
    warnings = []
    generic_words = ["enviar", "submit", "click aquí", "más información"]

    for root, _dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for word in generic_words:
                        if f">{word}<" in content or f'value="{word}"' in content:
                            rel_path = os.path.relpath(path, ROOT)
                            msg = f"[UX WARNING] CTA genérico '{word}' en {rel_path}."
                            warnings.append(msg)

    return warnings if warnings else ["OK: CTAs orientados a la acción."]


def run_copy_audit():
    print("======== INFORME DE COPYWRITING & CONVERSIÓN ========")

    print("\n[AUTORIDAD] Presencia de Experiencia:")
    for res in check_authority_mentions():
        print(f"  {res}")

    print("\n[VENTA] Análisis de CTAs:")
    for msg in check_generic_ctas():
        print(f"  {msg}")

    print("\n[ESTADO FINAL] Auditoría de copy completada.")
    print("=====================================================")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "audit":
        run_copy_audit()
    else:
        print("Comando no reconocido.")
