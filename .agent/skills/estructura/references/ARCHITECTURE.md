# Jorge Aguirre Flores - Arquitectura de Plantillas

## 🏗️ Estructura Base (base.html)
El archivo principal de toda la aplicación es [`base.html`](file:///home/jorand/antigravityobuntu/api/templates/layouts/base.html). Define el skeleton global, los recursos CSS/JS y la estructura de navegación.

### Bloques de Jinja2 Principales
- `title`: Para el SEO del título de la página.
- `meta_tags`: Para descripción y etiquetas Open Graph.
- `extra_head`: Inserción de estilos específicos de página.
- `content`: El bloque principal donde se renderiza el cuerpo de cada página.
- `extra_scripts`: Para scripts específicos al final del body.

## 🧱 Componentes de Estructura
- **Navbar**: [`components/navbar.html`](file:///home/jorand/antigravityobuntu/api/templates/components/navbar.html) (incluido en base).
- **Footer**: [`components/footer.html`](file:///home/jorand/antigravityobuntu/api/templates/components/footer.html) (incluido en base).

## 📐 Flujo de Herencia
Cualquier nueva página debe extender de `layouts/base.html`:
```html
{% extends "layouts/base.html" %}
{% block title %}Nueva Página{% endblock %}
{% block content %}
  <!-- Contenido aquí -->
{% endblock %}
```
