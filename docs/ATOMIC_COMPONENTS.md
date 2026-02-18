# ⚛️ Atomic Components Catalog

Este documento cataloga los componentes atómicos reutilizables disponibles en el sistema de diseño. Los átomos son los bloques de construcción fundamentales de la UI.

| Atomic Component               | Description                                                          | File                                   |
| ------------------------------ | -------------------------------------------------------------------- | -------------------------------------- |
| `btn-gold-liquid`              | Botón principal de llamada a la acción con un efecto de oro líquido. | `atoms/buttons/button-gold-liquid.css` |
| `btn-service-cta`              | Botón secundario para las tarjetas de servicio.                      | `atoms/buttons/button-service-cta.css` |
| `card-glass`                   | Tarjeta con un efecto de vidrio esmerilado.                          | `atoms/cards/card-glass.css`           |
| `card-service-premium`         | Tarjeta premium para mostrar los servicios.                          | `atoms/cards/card-service-premium.css` |
| `text-gradient-gold` (utility) | Clase de utilidad para aplicar un degradado dorado al texto.         | `tokens/colors.css`                    |
| `text-liquid-gold`             | Efecto de texto de oro líquido (similar al botón `btn-gold-liquid`). | `atoms/text/text-liquid-gold.css`      |

## Uso

Para usar un componente atómico, simplemente agrega la clase correspondiente a tu elemento HTML.

**Ejemplo:**

```html
<button class="btn-gold-liquid">Agendar Cita</button>
```

Asegúrate de que la hoja de estilos del átomo esté importada en el archivo `input.css` principal para que Tailwind la procese.
