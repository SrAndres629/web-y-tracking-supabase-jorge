#!/usr/bin/env python3
"""
Comando /antigravity quota
Muestra quota disponible en tiempo real
"""

import sys

from client import AntigravityClient


def format_number(n: int) -> str:
    """Formatea números grandes"""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def main():
    print("🔮 Antigravity Quota Monitor")
    print("=" * 50)

    try:
        client = AntigravityClient()
        quota = client.get_quota()

        # Barra de progreso visual
        bar_length = 30
        filled = int(bar_length * quota.percentage_used / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        # Color según uso
        color = "🟢"
        if quota.percentage_used > 70:
            color = "🟡"
        if quota.percentage_used > 90:
            color = "🔴"

        print(f"\n{color} Usage: [{bar}] {quota.percentage_used:.1f}%")
        print("\n📊 Detalles:")
        print(f"   Total:      {format_number(quota.total):>10} tokens")
        print(f"   Usado:      {format_number(quota.used):>10} tokens")
        print(f"   Disponible: {format_number(quota.remaining):>10} tokens")
        print(f"\n🔄 Reset: {quota.reset_date}")

        # Alertas
        if quota.percentage_used > 90:
            print("\n⚠️  ALERTA: Quota crítica (>90%)")
        elif quota.percentage_used > 75:
            print("\n⚡ Atención: Quota alta (>75%)")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Configura tu API key:")
        print("   export ANTIGRAVITY_API_KEY='tu_key'")
        sys.exit(1)


if __name__ == "__main__":
    main()
