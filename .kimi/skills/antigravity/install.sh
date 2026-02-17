#!/bin/bash
# Script de instalación para Antigravity Extension

echo "🔮 Instalando Antigravity Extension..."
echo "=============================================="

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SKILL_DIR"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

echo "✅ Python3 encontrado"

# Crear symlink para imports
if [ ! -L "antigravity" ]; then
    ln -s . antigravity
    echo "✅ Symlink creado"
fi

# Instalar dependencias si hay requirements
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Dependencias instaladas"
fi

# Ejecutar setup
python3 setup_mcp.py

echo ""
echo "=============================================="
echo "🎉 Instalación completa!"
echo ""
echo "Prueba con:"
echo "  /antigravity status"
