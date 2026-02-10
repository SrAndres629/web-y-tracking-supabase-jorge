@codex /run

### 🧠 ROL: SENIOR ARCHITECT & SRE (SITE RELIABILITY ENGINEER)
Tu objetivo único es llevar el proyecto de "ROJO" (Fallo en Auditoría) a "VERDE" (Deploy Exitoso).

### 📋 SITUACIÓN ACTUAL
El script de orquestación `git_sync.py` se detiene en la fase `Security & Perf Audit`.
- **El Humano confirma:** Las credenciales `.env` son VÁLIDAS y CORRECTAS.
- **El Error Técnico:** `ResourceWarning: unclosed <ssl.SSLSocket>` y excepciones en `test_performance.py`.
- **El Diagnóstico:** El código del test o la implementación del cliente HTTP tiene fugas de memoria, mal manejo de sesiones asíncronas (`asyncio`) o está intentando validar autenticación de forma incorrecta.

### ⚡ TU MISIÓN (AUTO-HEALING)
No quiero que me expliques el error. Quiero que **modifiques el código** para arreglarlo.

### 🛠️ ESTRUCTURA DE PENSAMIENTO CRÍTICO (Chain of Thought)
Para lograr el éxito, debes ejecutar este proceso mental antes de escribir una sola línea:

1.  **ANÁLISIS DE CAUSA RAÍZ (RCA):**
    - Si las claves están bien, ¿por qué falla la conexión?
    - *Hipótesis A:* El test no está cerrando el cliente HTTP (`await client.aclose()` faltante). -> **Acción:** Usar context managers (`async with`).
    - *Hipótesis B:* El test intenta conectar a un entorno real de Facebook en un test de performance, lo cual es inestable. -> **Acción:** ¿Deberíamos mockear la respuesta para medir solo la velocidad interna de la app? Si es un test de integración real, debemos asegurar que el payload sea válido.
    - *Hipótesis C:* Conflictos entre `pytest-asyncio` y el loop de eventos de Windows. -> **Acción:** Asegurar el `scope` correcto de los fixtures.

2.  **ESTRATEGIA DE REFACTORIZACIÓN:**
    - Voy a editar `tests/03_audit/test_performance.py`.
    - Voy a envolver las llamadas externas en bloques `try/except` robustos que impriman el error real del servidor (body response) en lugar de fallar silenciosamente.
    - Voy a asegurar que `dotenv` se cargue explícitamente dentro del test.

### 📝 ORDEN DE EJECUCIÓN (Paso a Paso)

**PASO 1: LECTURA**
Lee el contenido de `tests/03_audit/test_performance.py` y `app/config.py` para entender cómo se cargan las variables.

**PASO 2: REESCRITURA QUIRÚRGICA**
Reescribe `test_performance.py` completo. El nuevo código debe:
- Usar `AsyncClient` de forma segura.
- Imprimir logs de depuración: `print(f"DEBUG: Status {response.status_code}, Body: {response.text[:100]}")`.
- Ser resiliente: Si la API de Meta falla por rate-limit o error 400, el test debe manejarlo elegantemente o saltarse (`pytest.skip`) si es un error externo, pero NO fallar la auditoría de código interno.

**PASO 3: VERIFICACIÓN**
Ejecuta el comando: `python git_sync.py`
- Si pasa: Misión cumplida.
- Si falla: Analiza el nuevo log (que ahora será más detallado) y repite el Paso 2.

### 🚀 EJECUTA LA SOLUCIÓN AHORA
Empieza por leer el archivo `tests/03_audit/test_performance.py` y procede a arreglarlo.