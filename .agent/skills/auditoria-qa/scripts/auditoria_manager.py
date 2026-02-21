#!/usr/bin/env python3
import os
import re
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
TEMPLATES_DIR = os.path.join(ROOT, "api/templates")
STATIC_DIR = os.path.join(ROOT, "static")


def check_404_routes():
    """Busca posibles enlaces rotos o rutas estáticas mal formadas."""
    errors = []
    for root, _dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "/static/" in content and "url_for" not in content:
                        rel_path = os.path.relpath(path, ROOT)
                        msg = f"[WARNING] Ruta estática hardcodeada en {rel_path}"
                        errors.append(msg)

    return errors if errors else ["OK: No hay rutas hardcodeadas críticas."]


def check_8px_grid():
    """Valida que los valores de espaciado en CSS sigan la regla de 8px."""
    css_files = []
    for root, _dirs, files in os.walk(os.path.join(STATIC_DIR, "src")):
        for file in files:
            if file.endswith(".css"):
                css_files.append(os.path.join(root, file))

    errors = []
    for css_path in css_files:
        with open(css_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                match = re.search(r"(\d+)px", line)
                if match:
                    val = int(match.group(1))
                    if val % 4 != 0 and val > 4:
                        rel_path = os.path.relpath(css_path, ROOT)
                        msg = f"[GRID ERROR] {rel_path}:L{i + 1} -> {val}px no es múltiplo de 4/8"
                        errors.append(msg)

    return errors if errors else ["OK: Grid de 4/8px consistente."]


def run_audit():
    print("======== INFORME DE AUDITORÍA QA DE ÉLITE ========")

    print("\n[RUTA] Verificación de enlaces:")
    for err in check_404_routes():
        print(f"  {err}")

    print("\n[DISEÑO] Verificación de Grid 8px:")
    for err in check_8px_grid():
        print(f"  {err}")

    print("\n[ESTADO FINAL] Auditoría completada.")
    print("==================================================")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "validate":
        run_audit()
    else:
        print("Comando no reconocido.")
