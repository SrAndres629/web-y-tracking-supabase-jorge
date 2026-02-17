#!/usr/bin/env python3
"""
Handler principal para comandos slash /antigravity
Rutea a los subcomandos correspondientes
"""

import os
import sys

# Add skill dir to path
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, skill_dir)


def main():
    if len(sys.argv) < 2:
        print("🔮 Antigravity Extension")
        print("=" * 50)
        print("\nComandos disponibles:")
        print("  /antigravity quota   - Ver quota disponible")
        print("  /antigravity models  - Listar modelos")
        print("  /antigravity status  - Status completo")
        print("  /antigravity mcp     - Usar MCP")
        print("  /antigravity toolkit - Dashboard visual")
        print("\nConfiguración:")
        print("  export ANTIGRAVITY_API_KEY='tu_key'")
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "quota":
        from quota import main as quota_main

        quota_main()

    elif command == "models":
        from models import main as models_main

        models_main()

    elif command == "status":
        from status import main as status_main

        status_main()

    elif command == "mcp":
        from mcp_bridge import main as mcp_main

        sys.argv = [sys.argv[0]] + args
        mcp_main()

    elif command == "setup":
        from setup_mcp import setup_mcp

        setup_mcp()

    elif command == "toolkit":
        from toolkit import main as toolkit_main

        sys.argv = [sys.argv[0]] + args
        toolkit_main()

    else:
        print(f"❌ Comando desconocido: {command}")
        print("\nComandos válidos: quota, models, status, mcp, toolkit, setup")
        sys.exit(1)


if __name__ == "__main__":
    main()
