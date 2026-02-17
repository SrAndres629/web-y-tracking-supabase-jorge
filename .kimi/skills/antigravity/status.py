#!/usr/bin/env python3
"""
Comando /antigravity status
Status completo de Antigravity
"""

import logging
import sys

from client import AntigravityClient

logger = logging.getLogger(__name__)


def main():
    logger.info("🔮 Antigravity System Status")
    logger.info("=" * 60)

    try:
        client = AntigravityClient()
        status = client.get_status()

        # Quota
        quota = status["quota"]
        logger.info("\n📊 QUOTA")
        logger.info(f"   Total:      {quota.total:,} tokens")
        logger.info(f"   Usado:      {quota.used:,} tokens ({quota.percentage_used:.1f}%)")
        logger.info(f"   Disponible: {quota.remaining:,} tokens")
        logger.info(f"   Reset:      {quota.reset_date}")

        # Modelos
        models = status["models"]
        active = sum(1 for m in models if m.status == "active")
        logger.info(f"\n🤖 MODELOS ({len(models)} total, {active} activos)")

        for m in models[:5]:  # Top 5
            icon = "🟢" if m.status == "active" else "🟡"
            logger.info(f"   {icon} {m.name}")

        if len(models) > 5:
            logger.info(f"   ... y {len(models) - 5} más")

        # MCPs
        mcps = status["mcps"]
        print(f"\n🔌 MCPS ({len(mcps)} disponibles)")

        for mcp in mcps[:5]:
            print(f"   • {mcp.get('name', 'Unknown')}")

        if len(mcps) > 5:
            print(f"   ... y {len(mcps) - 5} más")

        print(f"\n{'=' * 60}")
        print(f"🕐 Última actualización: {status['timestamp']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
