# 🔥 Kimi CLI - Configuración Máxima Poder

Configuración completa de Kimi CLI para el proyecto de Jorge Aguirre con herramientas MCP, pensamiento profundo y modo YOLO.

## 📁 Archivos

| Archivo | Descripción |
|---------|-------------|
| `mcp.json` | Configuración de 10 servidores MCP |
| `config.toml` | Configuración global de Kimi CLI |
| `agent-max.toml` | Agente personalizado "Max-Power" |
| `prompts.md` | Librería de prompts preestablecidos |
| `logs/` | Directorio de logs |

## 🚀 Uso Rápido

### PowerShell (Recomendado)
```powershell
# Modo interactivo máximo poder
.\kimi-max.ps1

# Comandos predefinidos
.\kimi-max.ps1 -Analyze    # Análisis profundo
.\kimi-max.ps1 -Refactor   # Refactorización segura
.\kimi-max.ps1 -Debug      # Debugging avanzado
.\kimi-max.ps1 -Deploy     # Verificación pre-deploy
.\kimi-max.ps1 -Seo        # Optimización SEO
.\kimi-max.ps1 -Track      # Auditoría tracking

# Ejecutar prompt específico
.\kimi-max.ps1 -Prompt "Crea tests para el módulo X"

# Web UI
.\kimi-max.ps1 -Web -Port 8080
```

### Windows CMD
```batch
kimi-max.bat
kimi-max.bat -Analyze
```

## 🔧 Herramientas MCP Configuradas

| Servidor | Descripción | Requiere |
|----------|-------------|----------|
| `filesystem` | Acceso completo al proyecto | - |
| `fetch` | Consultas web | uvx |
| `brave-search` | Búsqueda web avanzada | BRAVE_API_KEY |
| `github` | Gestión de repos | GITHUB_TOKEN |
| `postgresql` | Base de datos | DATABASE_URL |
| `sqlite` | BD local | uvx |
| `memory` | Memoria persistente | - |
| `sequential-thinking` | Pensamiento secuencial | - |
| `puppeteer` | Navegador headless | - |
| `playwright` | Automatización web | - |

## ⚙️ Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# MCP Services
BRAVE_API_KEY=tu_api_key_aqui
GITHUB_TOKEN=tu_token_aqui
DATABASE_URL=postgresql://user:pass@host/db

# Proyecto
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
META_CAPI_ACCESS_TOKEN=xxx
RUDDERSTACK_WRITE_KEY=xxx
```

## 🎨 Características

- ✅ **YOLO Mode**: Auto-acepta todas las operaciones
- ✅ **Thinking Mode**: Pensamiento profundo activado
- ✅ **MCP Completo**: 10 herramientas integradas
- ✅ **Agente Max-Power**: Personalizado para tu proyecto
- ✅ **Prompts Preestablecidos**: Comandos de un click
- ✅ **Logs Detallados**: Debug completo en `.kimi/logs/`

## 📚 Documentación

- Ver `prompts.md` para la librería completa de prompts
- [Documentación oficial Kimi CLI](https://moonshotai.github.io/kimi-cli/)

---

*Configuración creada: 2026-02-13*
