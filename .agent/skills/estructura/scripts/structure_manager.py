#!/usr/bin/env python3
import os
import re
import sys

# Rutas reales del proyecto
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
TEMPLATES_DIR = os.path.join(ROOT, "api/templates")


def list_jinja_blocks(file_path):
    """Lista todos los bloques {% block ... %} en un archivo."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} no encontrado.")
        return []

    with open(file_path, "r") as f:
        content = f.read()

    blocks = re.findall(r"\{%\s*block\s+([\w-]+)\s*%\}", content)
    return list(set(blocks))


def find_extends(file_path):
    """Identifica de qué plantilla extiende el archivo actual."""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        content = f.read()

    match = re.search(r'\{%\s*extends\s+["\'](.*?)["\']\s*%\}', content)
    return match.group(1) if match else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 structure_manager.py blocks <ruta_archivo> | info <ruta_archivo>")
        sys.exit(1)

    action = sys.argv[1]
    target = sys.argv[2]

    # Resolver ruta si es relativa a templates
    full_path = target if os.path.isabs(target) else os.path.join(TEMPLATES_DIR, target)

    if action == "blocks":
        blocks = list_jinja_blocks(full_path)
        print(f"Bloques encontrados en {os.path.basename(full_path)}:")
        for b in sorted(blocks):
            print(f"- {b}")
    elif action == "info":
        parent = find_extends(full_path)
        print(f"Archivo: {os.path.basename(full_path)}")
        print(f"Hereda de: {parent if parent else 'Nada (es base)'}")
        blocks = list_jinja_blocks(full_path)
        print(f"Sobrescribe bloques: {', '.join(blocks) if blocks else 'Ninguno'}")
