#!/usr/bin/env python3
"""
Setup MCP para Antigravity
Configura integración nativa con Kimi CLI
"""

import json
import os
import sys
from pathlib import Path


def setup_mcp():
    """Configura MCP en .kimi/mcp.json"""

    print("🔮 Antigravity MCP Setup")
    print("=" * 50)

    # Detectar shell
    shell = os.environ.get("SHELL", "").split("/")[-1]
    rc_file = os.path.expanduser(f"~/.{shell}rc")

    # Preguntar API key si no existe
    api_key = os.environ.get("ANTIGRAVITY_API_KEY")

    if not api_key:
        print("\n⚠️  ANTIGRAVITY_API_KEY no encontrada")
        print("\nPor favor ingresa tu API key de Antigravity:")
        api_key = input("> ").strip()

        if not api_key:
            print("❌ API key requerida")
            sys.exit(1)

        # Agregar a shell rc
        with open(rc_file, "a") as f:
            f.write("\n# Antigravity API Key\n")
            f.write(f"export ANTIGRAVITY_API_KEY='{api_key}'\n")

        print(f"✅ API key guardada en {rc_file}")
        print("   Recarga tu shell: source ~/.bashrc")

    # Crear mcp.json
    kimi_dir = Path.home() / ".kimi"
    kimi_dir.mkdir(exist_ok=True)

    mcp_config = {
        "mcpServers": {
            "antigravity": {
                "command": sys.executable,
                "args": ["-m", "antigravity.mcp_server"],
                "cwd": str(Path(__file__).parent),
                "env": {
                    "ANTIGRAVITY_API_KEY": api_key or "${ANTIGRAVITY_API_KEY}",
                    "PYTHONPATH": str(Path(__file__).parent),
                },
            }
        }
    }

    mcp_path = kimi_dir / "mcp.json"

    # Merge si ya existe
    if mcp_path.exists():
        with open(mcp_path, "r") as f:
            existing = json.load(f)
        existing["mcpServers"].update(mcp_config["mcpServers"])
        mcp_config = existing

    with open(mcp_path, "w") as f:
        json.dump(mcp_config, f, indent=2)

    print(f"\n✅ MCP configurado en: {mcp_path}")

    # Crear symlink para importación
    skill_dir = Path(__file__).parent
    antigravity_link = skill_dir / "antigravity"

    if not antigravity_link.exists():
        antigravity_link.symlink_to(skill_dir)

    print("✅ Symlink creado para imports")

    # Test
    print("\n🧪 Probando conexión...")
    try:
        sys.path.insert(0, str(skill_dir))
        from client import AntigravityClient

        client = AntigravityClient(api_key=api_key)
        quota = client.get_quota()

        print("✅ Conexión exitosa!")
        print(f"   Quota disponible: {quota.remaining:,} tokens")

    except Exception as e:
        print(f"⚠️  Error de conexión: {e}")
        print("   Verifica tu API key")

    print("\n" + "=" * 50)
    print("🎉 Setup completo!")
    print("\nComandos disponibles:")
    print("   /antigravity quota   - Ver quota")
    print("   /antigravity models  - Listar modelos")
    print("   /antigravity status  - Status completo")
    print("\nMCP tools disponibles en Kimi CLI:")
    print("   - get_quota")
    print("   - list_models")
    print("   - use_model")


if __name__ == "__main__":
    setup_mcp()
