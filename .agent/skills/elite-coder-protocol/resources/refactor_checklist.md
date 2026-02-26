# 📋 Checklist de Refactorización Elite (Neuron 4)

Antes de dar por terminada una tarea, el Agente debe verificar internamente (o usando sus Neuronas 1, 2 y 3) estos 10 puntos de control:

## 1. Integridad de Sintaxis y Formato
- [ ] ¿Ejecutaste `clean_format.py` (Neurona 1) en tu archivo objetivo?
- [ ] ¿Están todos los imports organizados? No hay imports huérfanos.
- [ ] ¿Has borrado **todos** los statements de `print()` o `console.log()` usados para debug temporal?

## 2. Complejidad Ciclomática (SoC)
- [ ] ¿Ejecutaste `complexity_analyzer.py` (Neurona 2) en el módulo que acabas de engrosar?
- [ ] ¿Lograste mantener todas tus funciones por debajo de las 40 líneas?
- [ ] ¿Está tu lógica de base de datos separada de la ruta HTTP?

## 3. Integridad Global (Ripple Effect)
- [ ] Si modificaste el nombre de la variable, nombre del archivo, o campos en un `.toml` o `.env`... ¿Ejecutaste `ripple_effect_mapper.py` (Neurona 3)?
- [ ] ¿Actualizaste las importaciones en `tests/` que dependían de la variable antigua?

## 4. Tipado y Estabilidad
- [ ] ¿Agregaste Type Hints a TODOS los argumentos y Type Returns a TODAS las funciones modificadas?
- [ ] ¿Estás usando validación estricta con Pydantic si procesas payloads HTTP?

## 5. Rendimiento Edge / Vercel
- [ ] Si la función tarda más de 3 segundos, ¿moviste la carga a una tarea background (QStash) en lugar de bloquear la ruta HTTP?
- [ ] ¿Verificaste si necesitas un `Cache-Control: no-store` o estás atrapado en caché estático de Vercel?

**Si completaste los 10 puntos, has programado bajo el estándar ELITE.**
