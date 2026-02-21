# Jorge Aguirre Flores - Guía de Diseño UI

## 🧱 Componentes Core
Nuestra arquitectura se basa en clases de utilidad y componentes personalizados definidos en `static/src/input.css`.

### 💎 Botones (`.btn-*`)
- **Primary**: Degradado de oro, bordes redondeados (full), sombra suave.
- **Secondary**: Fondo traslúcido, borde sutil, efecto glassmorphism.

### 🪟 Efecto Cristal (`.card-glass`)
- Uso de `backdrop-blur-md` y `bg-white/5`.
-Bordes con gradientes sutiles y efectos de iluminación al hacer hover.

### ✍️ Tipografía Social
- Encabezados con degradados de oro (`.text-gradient-gold`).
- Uso extensivo de sombras de texto sutiles para legibilidad sobre fondos oscuros.

## 📐 Layout & Estructura
- El sistema utiliza **Tailwind CSS** como base.
- Los márgenes y paddings deben seguir la escala de espaciado estándar del proyecto.
- Responsividad primero: Asegurar que los componentes `glass` no afecten el rendimiento en móviles.
