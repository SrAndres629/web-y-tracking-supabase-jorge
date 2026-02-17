#!/usr/bin/env python3
"""
Antigravity Toolkit CLI
Comando principal para iniciar el dashboard visual
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Directorio del toolkit
TOOLKIT_DIR = Path(__file__).parent / "toolkit"
SERVER_SCRIPT = TOOLKIT_DIR / "server.py"


def check_dependencies():
    """Verifica dependencias necesarias"""
    try:
        import requests

        return True
    except ImportError:
        print("⚠️  Instalando dependencias...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
        return True


def start_toolkit(port: int = 8765, no_browser: bool = False):
    """Inicia el Toolkit"""
    check_dependencies()

    if not SERVER_SCRIPT.exists():
        print(f"❌ No se encontró {SERVER_SCRIPT}")
        sys.exit(1)

    print("""
╔══════════════════════════════════════════════════════════════╗
║              🛡️  ANTIGRAVITY TOOLKIT                        ║
╠══════════════════════════════════════════════════════════════╣
║  Dashboard visual para administración de quota y memoria     ║
╚══════════════════════════════════════════════════════════════╝
""")

    cmd = [sys.executable, str(SERVER_SCRIPT), "-p", str(port)]
    if no_browser:
        cmd.append("--no-browser")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Toolkit detenido")


def quick_status():
    """Muestra estado rápido en terminal"""
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        from client import AntigravityClient

        client = AntigravityClient()

        print("\n🛡️  Antigravity Status\n")
        print("─" * 50)

        # Quota
        quota = client.get_quota()
        print("\n⚡ Quota:")
        print(f"   Usado: {quota.used:,} ({quota.percentage_used:.1f}%)")
        print(f"   Restante: {quota.remaining:,}")
        print(f"   Total: {quota.total:,}")
        print(f"   Reset: {quota.reset_date}")

        # Progress bar
        bar_width = 30
        filled = int(bar_width * quota.percentage_used / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        color = "🟢" if quota.percentage_used < 75 else "🟡" if quota.percentage_used < 90 else "🔴"
        print(f"   {color} [{bar}] {quota.percentage_used:.1f}%")

        print("\n" + "─" * 50)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Configura ANTIGRAVITY_API_KEY para ver tu quota real")


def main():
    parser = argparse.ArgumentParser(
        description="🛡️ Antigravity Toolkit - Dashboard visual",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s                    # Inicia el dashboard
  %(prog)s -p 8080           # Usa puerto 8080
  %(prog)s --no-browser      # Sin abrir navegador
  %(prog)s --status          # Estado rápido en terminal
        """,
    )

    parser.add_argument(
        "-p", "--port", type=int, default=8765, help="Puerto para el servidor (default: 8765)"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="No abrir navegador automáticamente"
    )
    parser.add_argument("--status", action="store_true", help="Mostrar estado rápido en terminal")

    args = parser.parse_args()

    if args.status:
        quick_status()
    else:
        start_toolkit(args.port, args.no_browser)


if __name__ == "__main__":
    main()
