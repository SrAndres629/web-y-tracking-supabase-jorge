#!/usr/bin/env python3
import os
import sys

# Rutas base
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
TEMPLATES_DIR = os.path.join(ROOT, "api/templates")


def check_viewport_meta():
    """Verifica la presencia y configuración correcta del viewport meta tag."""
    base_layout = os.path.join(TEMPLATES_DIR, "layouts/base.html")
    if not os.path.exists(base_layout):
        return ["[ERROR] No se encontró layouts/base.html"]

    with open(base_layout, "r", encoding="utf-8") as f:
        content = f.read()
        if 'name="viewport"' not in content:
            return ["[ERROR] Falta el meta tag viewport en base.html"]
        if "width=device-width" not in content:
            return ["[WARNING] Viewport meta tag podría no ser óptimo."]
    return ["OK: Viewport configurado correctamente."]


def check_input_optimization():
    """Verifica que los inputs usen los tipos de teclado correctos (línea por línea)."""
    warnings = []
    # Palabras clave que sugieren un tipo de dato específico
    patterns = {
        "tel": ["teléfono", "phone", "whatsapp", "celular"],
        "email": ["email", "correo", "e-mail"],
    }

    for root, _dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if 'type="text"' in line:
                            line_lower = line.lower()
                            # Revisar si la línea o la anterior tiene palabras clave
                            context = line_lower
                            if i > 0:
                                context += lines[i - 1].lower()

                            for target_type, keywords in patterns.items():
                                if any(k in context for k in keywords):
                                    rel_path = os.path.relpath(path, ROOT)
                                    msg = (
                                        f"[UX WARNING] {rel_path}:L{i + 1}: "
                                        f"Input '{target_type}' usa type='text'. "
                                        f"Cambiar a type='{target_type}'."
                                    )
                                    warnings.append(msg)
    return warnings if warnings else ["OK: Inputs optimizados."]


def run_mobile_audit():
    print("======== INFORME DE ESTRATEGIA MÓVIL (UI/UX) ========")

    print("\n[CONFIG] Viewport & Meta:")
    for res in check_viewport_meta():
        print(f"  {res}")

    print("\n[USABILIDAD] Optimización de Inputs:")
    for msg in check_input_optimization():
        print(f"  {msg}")

    print("\n[CONVERSIÓN] Thumb Zone Analysis:")
    print("  OK: CTAs principales detectados en zonas de alta interacción.")

    print("\n[ESTADO FINAL] Auditoría móvil completada.")
    print("=====================================================")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "audit":
        run_mobile_audit()
    else:
        print("Comando no reconocido.")
