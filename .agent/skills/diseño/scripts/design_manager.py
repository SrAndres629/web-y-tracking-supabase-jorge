#!/usr/bin/env python3
import os
import re
import sys

# Rutas reales del proyecto
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
INPUT_CSS = os.path.join(ROOT, "static/src/input.css")


def get_component_definition(class_name):
    """Busca y devuelve la definición de una clase CSS en input.css."""
    if not os.path.exists(INPUT_CSS):
        print(f"Error: {INPUT_CSS} no encontrado.")
        return None

    with open(INPUT_CSS, "r") as f:
        content = f.read()

    # Regex para encontrar bloques CSS (simplificado)
    pattern = rf"\.{class_name}\s*\{{(.*?)\}}"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None


def list_all_components():
    """Lista todas las clases personalizadas en la sección de componentes."""
    if not os.path.exists(INPUT_CSS):
        return []

    with open(INPUT_CSS, "r") as f:
        content = f.read()

    # Busca clases dentro de @layer components
    components_match = re.search(r"@layer components\s*\{(.*)\}", content, re.DOTALL)
    if not components_match:
        return []

    classes = re.findall(r"\.([\w-]+)\s*\{", components_match.group(1))
    return list(set(classes))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 design_manager.py list|get <clase>")
        sys.exit(1)

    action = sys.argv[1]
    if action == "list":
        comps = list_all_components()
        print("Componentes encontrados:")
        for c in sorted(comps):
            print(f"- {c}")
    elif action == "get" and len(sys.argv) == 3:
        definition = get_component_definition(sys.argv[2])
        if definition:
            print(definition)
        else:
            print(f"Clase {sys.argv[2]} no encontrada.")
