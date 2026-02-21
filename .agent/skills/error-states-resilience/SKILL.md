---
name: error-states-resilience
description: El guardián de la robustez. Asegura que el sitio mantenga su prestigio incluso cuando la conexión o los procesos fallan.
---

# 🛡️ Error States & Resilience - Jorge Aguirre Flores

## Propósito
Blindar la confianza del usuario mediante una gestión impecable de los estados de error y carga. Esta skill garantiza que el sitio nunca se "rompa" visualmente ante fallos de red o errores de servidor, manteniendo siempre la estética de lujo.

## 🧠 Lógica de Resiliencia: Fallo Elegante
1.  **Skeleton States**: Uso de placeholders animados elegantes mientras se cargan datos dinámicos.
2.  **Custom Error Pages**: Templates personalizados para 404 (No encontrado) y 500 (Error servidor).
3.  **Feedback de Acción**: Asegurar que cada botón muestre un estado "Cargando" tras el clic para evitar la ansiedad del usuario.

## 📏 Reglas de Oro (Hard Rules)
- **No Blank Screens**: Queda prohibido que una página o componente se quede en blanco sin un spinner o skeleton.
- **Friendly Language**: Los mensajes de error deben ser empáticos y orientados a la solución ("Algo salió mal, pero ya estamos trabajando en ello").
- **Offline Awareness**: Información básica accesible incluso con baja conectividad.
- **Form Protection**: Avisar al usuario si intenta cerrar un formulario con datos no enviados.

## Instructions
1.  **Auditoría de Robustez**: Verifica la existencia de `404.html` y `500.html` en el directorio de templates.
2.  **Placeholders**: Busca componentes dinámicos y asegura que tengan un estado de carga definido.
3.  **UX de Recuperación**: Asegura que cada mensaje de error ofrezca un camino de regreso (ej. botón a Home).

## Métrica de Éxito
- Existencia de páginas de error de marca.
- Feedback visual inmediato en todas las acciones del sitio.
- Reducción del abandono por fallos técnicos percibidos.
