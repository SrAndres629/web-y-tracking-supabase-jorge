---
name: yolo-mode
description: Modo YOLO - Ejecución autónoma total con pensamiento profundo para Kimi CLI
---

# Modo YOLO para Kimi CLI

## Descripción

El Modo YOLO (You Only Live Once) es una extensión que permite a Kimi operar con **máxima autonomía** mientras mantiene un **pensamiento profundo** antes de cada acción.

## Características

- ✅ Autoaceptación de tareas rutinarias
- 🧠 Pensamiento profundo multi-nivel antes de actuar
- 📊 Logging exhaustivo de razonamiento
- 🔄 Capacidad de rollback automático
- 🎯 Escalación inteligente solo en casos críticos

## Niveles de Pensamiento

| Nivel | Tiempo | Descripción |
|-------|--------|-------------|
| surface | < 5s | Análisis superficial rápido |
| standard | 5-15s | Análisis estándar |
| **deep** | 15-30s | Pensamiento profundo (default) |
| profound | 30-60s | Pensamiento profundo extendido |
| meta | 60s+ | Análisis meta-cognitivo |

## Uso

### Activar modo YOLO

```bash
# Pensamiento profundo (default)
/yolo

# Pensamiento más profundo
/yolo profound

# Máximo pensamiento
/yolo meta
```

### Desactivar modo YOLO

```bash
/yolo off
```

### Ver estadísticas

```bash
/yolo stats
```

## Comportamiento

Cuando el modo YOLO está activo:

1. **Antes de cada acción**, Kimi realizará un análisis profundo considerando:
   - Riesgos potenciales
   - Alternativas posibles
   - Impacto en la arquitectura
   - Plan de rollback

2. **Autoaceptación** cuando la confianza > 75%:
   - Tareas de análisis
   - Refactorizaciones con tests
   - Documentación
   - Optimizaciones medibles

3. **Escalación humana** cuando:
   - Confianza < 75%
   - Impacto crítico detectado
   - Cambios de seguridad
   - Modificaciones arquitectónicas grandes

## Configuración

El modo YOLO se puede configurar editando `.ai/modes/yolo_config.json`:

```json
{
  "min_confidence": 0.75,
  "default_thought_level": "deep",
  "auto_rollback": true,
  "log_all_decisions": true
}
```

## Integración con NEXUS-7

Este modo se integra con el sistema NEXUS-7 existente:
- Usa el `AutoAcceptanceProtocol` para decisiones
- Se conecta al `MessageBus` para notificaciones
- Guarda decisiones en `.ai/modes/logs/`

## Seguridad

⚠️ **Advertencia**: El modo YOLO está diseñado para desarrolladores expertos.
- Siempre revisa el `rollback_plan` generado
- Monitorea los logs en `.ai/modes/logs/`
- Usa `/yolo off` para volver al modo manual

## Ejemplo de Flujo

```
Usuario: /yolo profound
Kimi: 🚀 MODO YOLO ACTIVADO - Pensamiento: profound

Usuario: Refactoriza este código
Kimi: [Piensa profundamente...]
      📊 Análisis: 5 riesgos identificados
      📊 Confianza: 87%
      🚀 Auto-ejecutando...
      ✅ Completado en 2.3s
```
