---
name: performance-optimization
description: El arquitecto de velocidad. Garantiza que la interfaz se entregue de forma instantánea y estable, eliminando parpadeos (FOUC) y retrasos.
---

# ⚡ Performance & Stability - Jorge Aguirre Flores

## Propósito
Garantizar que el sitio cargue en menos de 2 segundos y que la estabilidad visual sea perfecta. Esta skill blinda la experiencia técnica para que el diseño de lujo no se vea empañado por tiempos de espera o saltos de contenido.

## 🧠 Lógica de Ejecución: Entrega Instantánea
1. **Critical CSS First**: Cargar el CSS esencial del primer scroll de forma prioritaria.
2. **Asset Lean Management**: Imágenes en WebP, scripts diferidos y fuentes optimizadas.
3. **Zero Layout Shift**: Dimensiones de imagen obligatorias para evitar saltos.

## 📏 Reglas de Oro (Hard Rules)
- **Lazy Loading**: Obligatorio en todas las imágenes que no estén en el viewport inicial.
- **Modern Formats**: Uso preferente de WebP/AVIF con fallback.
- **Async/Defer**: Todo script no crítico debe ser `defer` o `async`.
- **CLS Control**: Reserva de espacio para imágenes y anuncios.

## Instructions
1. **Auditoría de Carga**: Identifica elementos "Render-Blocking" y muévelos al final del body.
2. **Batch Image Audit**: Verifica que no existan PNGs/JPGs pesados sin versión WebP.
3. **Vercel Guard**: Supervisa que el peso de la página no comprometa los límites de la plataforma.

## Métrica de Éxito
- **LCP (Largest Contentful Paint)** < 2.5s.
- **CLS (Cumulative Layout Shift)** < 0.1.
- **TTI (Time to Interactive)** mínimo.
