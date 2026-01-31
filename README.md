# Jorge Aguirre Flores - Web & Tracking (Isolated)

Este es el núcleo independiente de la página web y tracking, diseñado para despliegue serverless en Vercel.

## 🚀 Estructura del Proyecto
- `app/`: Lógica central (FastAPI + Pydantic + Supabase).
- `static/`: Activos estáticos servidos por CDN (incluye **Tailwind CSS Compiled**).
- `templates/`: Plantillas Jinja2 con diseño **Tailwind CSS**.
- `api/index.py`: Adaptador Mangum para Vercel.
- `main.py`: Punto de entrada de la aplicación.

## 🛠️ Despliegue en Vercel
1. Conecta este repositorio a un nuevo proyecto en Vercel.
2. Configura las variables de entorno (`DATABASE_URL`, `META_PIXEL_ID`, `META_ACCESS_TOKEN`).
3. El despliegue es automático vía Git.

## 🛡️ Política de Seguridad
Este proyecto implementa **Postgres-Enforcement**. Si la conexión a la base de datos falla en producción, la aplicación lanzará un error 500 para evitar pérdida de datos en almacenamiento efímero.
