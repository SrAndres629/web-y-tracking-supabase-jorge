# 🛡️ Antigravity Toolkit

Dashboard visual para administrar tu quota y memoria de Antigravity con autocapeo inteligente.

![Toolkit Preview](https://i.imgur.com/toolkit-preview.png)

## ✨ Características

### 📊 Dashboard Visual
- **Quota Circle**: Visualización circular del quota usado con color coding
- **Timer Reset**: Cuenta regresiva hasta el reset de quota
- **Memory Bar**: Barra de progreso del uso de memoria
- **Gráfico Histórico**: Uso de los últimos 7 días

### 🧠 Administración de Memoria
- Lista de contextos activos
- Búsqueda y filtrado
- Archivar / Eliminar contextos
- Limpieza automática

### 🎯 Autocapeo Inteligente
Tres modos preconfigurados:
- **Conservador**: Límites bajos (50%/60%), máxima seguridad
- **Balanceado**: Límites medios (80%/90%), equilibrio óptimo
- **Rendimiento**: Límites altos (95%/95%), máximo uso

Acciones automáticas:
- Limpieza de memoria al llegar al límite
- Cambio a modelo económico
- Notificaciones en tiempo real

## 🚀 Instalación

```bash
# Desde el directorio del skill
cd .kimi/skills/antigravity

# El toolkit ya está incluido
python toolkit.py
```

## 📖 Uso

### Iniciar Dashboard
```bash
# Inicia el servidor y abre el navegador
python toolkit.py

# Puerto personalizado
python toolkit.py -p 8080

# Sin abrir navegador
python toolkit.py --no-browser
```

### Estado Rápido (Terminal)
```bash
python toolkit.py --status
```

Salida:
```
🛡️  Antigravity Status

──────────────────────────────────────────────────

⚡ Quota:
   Usado: 650,000 (65.0%)
   Restante: 350,000
   Total: 1,000,000
   Reset: 2026-02-20T00:00:00
   🟢 [████████████████░░░░░░░░░░░░░░] 65.0%

──────────────────────────────────────────────────
```

## 🔌 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/quota` | Información de quota |
| GET | `/api/memory` | Uso de memoria |
| GET | `/api/contexts` | Lista de contextos |
| POST | `/api/memory/clear` | Limpiar memoria |
| POST | `/api/contexts/{id}/archive` | Archivar contexto |
| DELETE | `/api/contexts/{id}` | Eliminar contexto |
| POST | `/api/autocap/config` | Configurar autocapeo |

## 🎨 Personalización

### Configurar Autocapeo

Via API:
```bash
curl -X POST http://localhost:8765/api/autocap/config \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "conservative",
    "quota_limit": 70,
    "memory_limit": 80,
    "auto_clear_memory": true
  }'
```

Via UI:
1. Abre el dashboard
2. Ve a "Configuración de Autocapeo"
3. Selecciona modo y ajusta límites
4. Guarda

## 🔧 Integración con Antigravity

El toolkit se integra automáticamente con el cliente de Antigravity:

```python
from antigravity.toolkit.server import AntigravityToolkitAPI

api = AntigravityToolkitAPI()

# Obtener quota
quota = api.get_quota()
print(f"Usado: {quota['percentage']:.1f}%")

# Verificar autocapeo
memory = api.get_memory()
autocap = api.check_autocap(quota, memory)
```

## 🛟 Comandos CLI

```bash
# Iniciar dashboard
/antigravity toolkit

# Ver estado
/antigravity toolkit --status

# Puerto específico  
/antigravity toolkit -p 3000
```

## 📁 Estructura

```
toolkit/
├── server.py          # Servidor Flask/FastAPI
├── toolkit.py         # CLI wrapper
├── static/
│   ├── toolkit.css    # Estilos del dashboard
│   └── toolkit.js     # Lógica del frontend
├── templates/
│   └── index.html     # Dashboard HTML
└── README.md          # Esta documentación
```

## 🔒 Seguridad

- API local únicamente (localhost)
- No expone información sensible
- Autocapeo previene uso excesivo

## 📝 Changelog

### v2.0.0
- Dashboard visual completo
- Sistema de autocapeo
- Gráficos de uso histórico
- Modo emergencia

---

**Made with 💜 for Antigravity**
