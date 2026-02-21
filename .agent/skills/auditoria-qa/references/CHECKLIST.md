# QA Elite Checklist - Jorge Aguirre Flores

Este checklist debe ser verificado por la Skill `auditoria-qa` antes de dar por terminada cualquier tarea de frontend.

## 📱 Mobile First & Responsividad
- [ ] No existe scroll horizontal en anchos menores a 320px.
- [ ] Los touch targets (botones, enlaces) tienen al menos 44x44px de área interactiva.
- [ ] Las fuentes en móviles no bajan de 14px (ideal 16px).

## 📐 Sistema de Grid (The 8px Rule)
- [ ] Los margins y paddings son múltiplos de 8px (8, 16, 24, 32, 40, etc.).
- [ ] Los gaps en flex/grid son consistentes.
- [ ] El espaciado vertical entre secciones es uniforme (ej. 96px o 128px).

## 🌑 Contraste & Accesibilidad (WCAG)
- [ ] El texto dorado sobre negro cumple con el contraste mínimo de 4.5:1.
- [ ] Todas las imágenes representativas tienen `alt` tags.
- [ ] El focus state es visible en todos los elementos interactivos.

## ⚡ Performance & Estética
- [ ] No hay FOUC (Flash of Unstyled Content).
- [ ] Las imágenes críticas usan `loading="eager"` y `fetchpriority="high"`.
- [ ] Los degradados dorados son suaves, sin "banding".
- [ ] Las tipografías de lujo (Cormorant, Inter) cargan correctamente.
