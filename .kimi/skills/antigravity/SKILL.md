---
name: antigravity
description: Extensión nativa para Antigravity - Quota, modelos, MCP y Toolkit visual
version: 2.0.0
author: NEXUS-7
---

# 🛡️ Antigravity Extension para Kimi CLI

Extensión profesional para integración nativa con la plataforma Antigravity.

## 🚀 Nuevo: Toolkit Visual v2.0

Dashboard completo con autocapeo inteligente:

```bash
# Iniciar dashboard
/antigravity toolkit

# Ver estado rápido
/antigravity toolkit --status
```

## Features

- 📊 **Toolkit Visual** - Dashboard web para gestión de quota y memoria
- 🎯 **Autocapeo Inteligente** - Límites automáticos con 3 modos
- 📈 **Quota en tiempo real** - Monitorea tu uso de API
- 🤖 **Modelos disponibles** - Lista todos los modelos de Antigravity
- 🔌 **MCP Nativo** - Usa los MCPs de Antigravity desde Kimi CLI
- ⚡ **Auto-configuración** - Setup automático de credenciales
- 🔄 **Sync continuo** - Actualización en tiempo real

## Requisitos

```bash
export ANTIGRAVITY_API_KEY="tu_api_key"
export ANTIGRAVITY_BASE_URL="https://api.antigravity.ai/v1"
```

## Comandos

```bash
# 🎨 Dashboard Visual
/antigravity toolkit              # Iniciar dashboard
/antigravity toolkit --status     # Estado rápido en terminal
/antigravity toolkit -p 8080      # Puerto personalizado

# 📊 Quota y Modelos
/antigravity quota                # Ver quota disponible
/antigravity models               # Listar modelos
/antigravity status               # Status completo

# 🔌 MCP
/antigravity mcp <nombre>         # Usar MCP específico
/antigravity setup                # Configurar MCP
```

## 🎯 Autocapeo Inteligente

El toolkit incluye un sistema de autocapeo con 3 modos:

| Modo | Límite Quota | Límite Memoria | Uso |
|------|--------------|----------------|-----|
| 🛡️ Conservador | 50% | 60% | Máxima seguridad |
| ⚖️ Balanceado | 80% | 90% | Uso óptimo (default) |
| 🚀 Rendimiento | 95% | 95% | Máximo rendimiento |

**Acciones automáticas:**
- Limpieza de memoria al llegar al límite
- Cambio a modelo económico
- Notificaciones en tiempo real

## 🔧 Configuración

Los MCPs se configuran automáticamente en `.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "antigravity": {
      "command": "python",
      "args": ["-m", "antigravity.mcp"],
      "env": {
        "ANTIGRAVITY_API_KEY": "${ANTIGRAVITY_API_KEY}"
      }
    }
  }
}
```

## 📁 Estructura

```
.kimi/skills/antigravity/
├── toolkit/              # 🎨 Dashboard Visual
│   ├── server.py         # Servidor API
│   ├── toolkit.py        # CLI
│   ├── static/
│   │   ├── toolkit.css   # Estilos
│   │   └── toolkit.js    # Lógica frontend
│   └── templates/
│       └── index.html    # Dashboard
├── client.py             # Cliente API
├── mcp_server.py         # Servidor MCP
├── quota.py              # Comando quota
├── models.py             # Comando models
└── ...
```
