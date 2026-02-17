#!/usr/bin/env python3
"""
Comando /antigravity models
Lista todos los modelos disponibles
"""

import sys

from client import AntigravityClient


def main():
    print("🤖 Antigravity Models")
    print("=" * 70)

    try:
        client = AntigravityClient()
        models = client.get_models()

        if not models:
            print("❌ No se encontraron modelos")
            sys.exit(1)

        print(f"\n📚 Total modelos: {len(models)}\n")

        # Agrupar por capacidades
        categories = {}
        for model in models:
            cap = model.capabilities[0] if model.capabilities else "general"
            if cap not in categories:
                categories[cap] = []
            categories[cap].append(model)

        # Mostrar por categoría
        for category, models_list in categories.items():
            print(f"\n{'─' * 70}")
            print(f"🏷️  {category.upper()}")
            print("─" * 70)

            for m in models_list:
                status_icon = "🟢" if m.status == "active" else "🟡"
                print(f"\n{status_icon} {m.name} ({m.id})")
                print(f"   {m.description[:60]}...")
                print(f"   Max tokens: {m.max_tokens:,}")
                print(f"   Pricing: ${m.pricing_input}/1K in | ${m.pricing_output}/1K out")

        print(f"\n{'=' * 70}")
        print("\n💡 Usa un modelo: /antigravity use <model_id>")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
