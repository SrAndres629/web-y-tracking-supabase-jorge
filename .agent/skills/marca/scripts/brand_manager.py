#!/usr/bin/env python3
import os
import re
import sys

# Rutas reales del proyecto
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
COLORS_CSS = os.path.join(ROOT, "static/design-system/tokens/colors.css")
TYPO_CSS = os.path.join(ROOT, "static/design-system/tokens/typography.css")
TAILWIND_CONFIG = os.path.join(ROOT, "tailwind.config.js")


def update_color_token(token_name, new_value):
    """Actualiza un token en colors.css y su equivalente en tailwind.config.js si existe."""
    if not os.path.exists(COLORS_CSS):
        print(f"Error: No se encuentra {COLORS_CSS}")
        return False

    with open(COLORS_CSS, "r") as f:
        content = f.read()

    # regex para --luxury-gold: #C5A059;
    pattern = rf"({token_name}:\s*)(#[A-Fa-f0-9]{{3,6}}|rgb\(.*?\)|var\(.*?\))"
    if not re.search(pattern, content):
        print(f"Token {token_name} no encontrado en CSS.")
        return False

    new_content = re.sub(pattern, rf"\1{new_value}", content)

    with open(COLORS_CSS, "w") as f:
        f.write(new_content)
    print(f"Token {token_name} actualizado en colors.css a {new_value}.")

    # Sincronizar con Tailwind si es un color principal
    # Mapeo simple: --luxury-gold -> luxury-gold
    tw_key = token_name.replace("--", "")
    if os.path.exists(TAILWIND_CONFIG):
        with open(TAILWIND_CONFIG, "r") as f:
            tw_content = f.read()

        tw_pattern = rf"('{tw_key}':\s*)'#[A-Fa-f0-9]{{3,6}}'"
        if re.search(tw_pattern, tw_content):
            tw_new_content = re.sub(tw_pattern, rf"\1'{new_value}'", tw_content)
            with open(TAILWIND_CONFIG, "w") as f:
                f.write(tw_new_content)
            print(f"Token {tw_key} sincronizado en tailwind.config.js.")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 brand_manager.py color <token> <nuevo_valor>")
        sys.exit(1)

    action = sys.argv[1]
    if action == "color":
        update_color_token(sys.argv[2], sys.argv[3])
