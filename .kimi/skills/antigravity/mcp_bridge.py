#!/usr/bin/env python3
"""
Comando /antigravity mcp <name>
Bridge para usar MCPs de Antigravity
"""

import json
import sys

from client import AntigravityClient


def main():
    if len(sys.argv) < 2:
        print("Uso: /antigravity mcp <nombre> [input_json]")
        print("\nMCPs disponibles:")

        try:
            client = AntigravityClient()
            mcps = client.get_mcps()

            for mcp in mcps:
                print(f"  • {mcp.get('name')} - {mcp.get('description', 'N/A')}")
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    mcp_name = sys.argv[1]
    input_data = {}

    if len(sys.argv) > 2:
        try:
            input_data = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("❌ Error: input_json debe ser JSON válido")
            return

    print(f"🔌 Antigravity MCP: {mcp_name}")
    print("=" * 50)

    try:
        client = AntigravityClient()
        result = client.use_mcp(mcp_name, input_data)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        print("\n✅ Resultado:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
