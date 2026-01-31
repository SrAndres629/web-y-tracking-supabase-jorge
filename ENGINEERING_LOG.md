# 📟 LIVE ENGINEERING LOG: PROJECT ISOLATION CORE

**SISTEMA DE COMUNICACIÓN ARQUITECTO (A) <-> INGENIERO (I)**

---

## 🏛️ DIRECTIVAS DEL ARQUITECTO
**ESTADO ACTUAL:** EVALUACIÓN DE INTEGRIDAD DE RAÍZ

### [A-001] FASE 1: SINCRONIZACIÓN DE DATOS & PERFORMANCE LOCAL
El Ingeniero debe garantizar que la base de datos no sea una "Caja Negra".
1. **Acción**: Ejecutar `python app/database.py` directamente o vía script de prueba para validar que todas las tablas de **CRM Natalia v2.0** existen en el entorno local.
2. **Acción**: Verificar que el pool de conexiones de Supabase usa el port `6543`.
3. **Reporte**: El Ingeniero debe confirmar si hay discrepancias entre el Schema local y el remoto.

### [A-002] FASE 2: BALANCE DE SEÑAL META (CAPI + PIXEL)
1. **Acción**: Realizar un "Mock Conversion Test". El Ingeniero debe interceptar una llamada a `/track/event` y validar que el objeto `user_data` contiene el hash SHA256 correcto para `external_id`.
2. **Acción**: Confirmar que el `event_id` generado en `tracking.js` persiste hasta después del redirect de WhatsApp.
3. **Reporte**: Declarar el nivel de EMQ (Event Match Quality) esperado.

### [A-003] FASE 3: DEPLOYMENT LOCKDOWN (VERCEL)
1. **Acción**: Ejecutar `vercel link` y `vercel env pull` para sincronizar entorno.
2. **Acción**: Validar configuración en `vercel.json` (Python Runtime).
3. **Reporte**: [URL Vercel](https://web-y-tracking-supabase-jorge.vercel.app) (Activa).

---

## 🛠️ REPORTE DEL INGENIERO
**FASE 1 y 2 COMPLETADAS. LISTO PARA LOCKDOWN.**

| ID Acción | Estado   | Resultado / Logs                                                     |
| :-------- | :------- | :------------------------------------------------------------------- |
| A-001.1   | ✅ ÉXITO  | Tablas Natalia v2.0 sincronizadas (SQLite Local).                    |
| A-001.2   | ⚠️ ALERTA | El `.env` actual NO tiene :6543. Corregir antes de Prod.             |
| A-002.1   | ✅ ÉXITO  | Hash SHA256 validado. Deduplicación por `event_id` verificada.       |
| A-003.1   | ✅ LISTO  | `vercel.json` validado. Handler `Mangum` activo para AWS Lambda.     |
| A-003.2   | 🚀 LIVE   | Despliegue Exitoso. https://web-y-tracking-supabase-jorge.vercel.app |

---

**ARQUITECTO:** "Ingeniero, no toleraré placeholders. Si una tabla falta, crashea el sistema. Procede con el comando de integridad de DB ahora."
