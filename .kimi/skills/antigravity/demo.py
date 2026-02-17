#!/usr/bin/env python3
"""
Demo de la extensión Antigravity
Muestra todas las capacidades
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import AntigravityClient


def demo():
    print("🔮 DEMO: Antigravity Extension")
    print("=" * 60)

    try:
        client = AntigravityClient()

        # Demo 1: Quota
        print("\n1️⃣  QUOTA INFO")
        print("-" * 40)
        quota = client.get_quota()
        print(f"   Total:      {quota.total:,} tokens")
        print(f"   Usado:      {quota.used:,} tokens")
        print(f"   Restante:   {quota.remaining:,} tokens")
        print(f"   Porcentaje: {quota.percentage_used:.1f}%")

        # Demo 2: Modelos
        print("\n2️⃣  MODELOS DISPONIBLES")
        print("-" * 40)
        models = client.get_models()
        for m in models[:3]:
            print(f"   • {m.name} ({m.id})")
            print(f"     Max tokens: {m.max_tokens}")
        if len(models) > 3:
            print(f"   ... y {len(models) - 3} más")

        # Demo 3: MCPs
        print("\n3️⃣  MCPS DISPONIBLES")
        print("-" * 40)
        mcps = client.get_mcps()
        for mcp in mcps[:3]:
            print(f"   • {mcp.get('name', 'Unknown')}")
        if len(mcps) > 3:
            print(f"   ... y {len(mcps) - 3} más")

        print("\n" + "=" * 60)
        print("✅ Demo completado exitosamente!")
        print("\nComandos disponibles:")
        print("   /antigravity quota")
        print("   /antigravity models")
        print("   /antigravity status")
        print("   /antigravity mcp <nombre>")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de configurar:")
        print("   export ANTIGRAVITY_API_KEY='tu_key'")


if __name__ == "__main__":
    demo()
