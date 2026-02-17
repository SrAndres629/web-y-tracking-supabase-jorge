# 🔮 Antigravity Extension para Kimi CLI

Extensión profesional para integración nativa con la plataforma Antigravity.

## 🚀 Instalación Rápida

```bash
cd .kimi/skills/antigravity
python3 setup_mcp.py
```

Esto configurará:
- Variables de entorno
- MCP server en `~/.kimi/mcp.json`
- Comandos slash disponibles

## 📋 Requisitos

```bash
export ANTIGRAVITY_API_KEY="tu_api_key_aqui"
```

O déjalo que el setup lo configure automáticamente.

## 🎯 Comandos

### `/antigravity quota`
Muestra quota disponible en tiempo real con barras de progreso visuales.

```
🔮 Antigravity Quota Monitor
==================================================

🟢 Usage: [████████████████░░░░░░░░░░░░░░] 45.2%

📊 Detalles:
   Total:      1.0M tokens
   Usado:      452.3K tokens
   Disponible: 547.7K tokens

🔄 Reset: 2025-03-01
```

### `/antigravity models`
Lista todos los modelos disponibles organizados por capacidades.

```
🤖 Antigravity Models
======================================================================

📚 Total modelos: 12

──────────────────────────────────────────────────────────────────────
🏷️  CHAT
──────────────────────────────────────────────────────────────────────

🟢 GPT-4 Turbo (gpt-4-turbo)
   Modelo avanzado para conversaciones complejas
   Max tokens: 128,000
   Pricing: $0.01/1K in | $0.03/1K out

🟢 Claude 3 Opus (claude-3-opus)
   Mejor rendimiento en tareas complejas
   Max tokens: 200,000
   Pricing: $0.015/1K in | $0.075/1K out
```

### `/antigravity status`
Status completo del sistema en una vista.

### `/antigravity mcp <nombre>`
Usa un MCP específico de Antigravity.

## 🔌 MCP Tools (Integración Nativa)

Una vez configurado, los MCPs de Antigravity están disponibles nativamente en Kimi CLI:

### `get_quota`
```json
{
  "name": "get_quota",
  "description": "Obtiene quota disponible de Antigravity"
}
```

### `list_models`
```json
{
  "name": "list_models",
  "description": "Lista modelos disponibles",
  "inputSchema": {
    "filter": "chat"  // Opcional: filtrar por capacidad
  }
}
```

### `use_model`
```json
{
  "name": "use_model",
  "description": "Usa un modelo específico",
  "inputSchema": {
    "model": "gpt-4-turbo",
    "prompt": "Tu prompt aquí",
    "temperature": 0.7
  }
}
```

### MCPs Custom de Antigravity

Todos los MCPs que tengas en tu cuenta de Antigravity se exponen automáticamente:

- `code_analyzer` - Análisis de código
- `doc_generator` - Generación de documentación
- `test_writer` - Escritura de tests
- Y cualquier otro que tengas configurado

## 🏗️ Estructura del Proyecto

```
.kimi/skills/antigravity/
├── __init__.py           # Package initialization
├── client.py             # Cliente API unificado
├── config.json           # Configuración del skill
├── mcp_server.py         # Servidor MCP (stdio)
├── mcp_bridge.py         # Bridge para comandos MCP
├── models.py             # Comando /models
├── quota.py              # Comando /quota
├── setup_mcp.py          # Script de instalación
├── SKILL.md              # Metadata del skill
└── README.md             # Esta documentación
```

## 🔧 API Python

También puedes usar el cliente directamente:

```python
from antigravity import AntigravityClient

client = AntigravityClient()

# Quota
quota = client.get_quota()
print(f"Disponible: {quota.remaining} tokens")

# Modelos
models = client.get_models()
for m in models:
    print(f"{m.name}: {m.max_tokens} tokens")

# Usar MCP
result = client.use_mcp("code_analyzer", {
    "code": "def hello(): pass",
    "language": "python"
})
```

## 📝 Configuración Manual

Si prefieres configurar manualmente, crea `~/.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "antigravity": {
      "command": "python3",
      "args": [
        ".kimi/skills/antigravity/mcp_server.py"
      ],
      "env": {
        "ANTIGRAVITY_API_KEY": "tu_key"
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Error: "ANTIGRAVITY_API_KEY no configurada"
```bash
export ANTIGRAVITY_API_KEY="tu_key"
# O agrega a ~/.bashrc
```

### Error: "No module named antigravity"
```bash
cd .kimi/skills/antigravity
python3 -c "import sys; sys.path.insert(0, '.'); from client import AntigravityClient"
```

### MCP no aparece en Kimi CLI
1. Verifica `~/.kimi/mcp.json` existe
2. Reinicia Kimi CLI
3. Ejecuta `python3 .kimi/skills/antigravity/setup_mcp.py`

## 📊 Características

- ✅ **Tiempo real** - Datos actualizados en cada llamada
- ✅ **Cache inteligente** - Evita rate limits
- ✅ **Error handling** - Mensajes claros de error
- ✅ **Visual** - Barras de progreso y colores
- ✅ **Extensible** - Fácil agregar nuevos comandos

## 🤝 Contribuir

Para agregar nuevos comandos:

1. Crea archivo `.py` en `.kimi/skills/antigravity/`
2. Agrega a `config.json` → `commands`
3. Documenta en README

## 📄 Licencia

MIT - NEXUS-7 Team

---

**Desarrollado con 🧠 por NEXUS-7 para la comunidad Kimi CLI**
