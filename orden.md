Rol: DevOps & Backend Lead.

Problema: Error 500 en producción (Vercel). Jinja2 no encuentra pages/public/home.html en /var/task/templates.

Solución Táctica:

Edita app/config.py (o donde definas templates = Jinja2Templates(...)): Cambia la definición del directorio de templates para que use rutas absolutas basadas en os.path.dirname(__file__).

Si estamos en Vercel (os.getenv("VERCEL")), busca en os.path.join(os.getcwd(), 'templates').

Imprime un print(f"DEBUG: Template dir set to: {template_dir}") para verlo en los logs de Vercel.

Edita vercel.json: Asegúrate de que la sección includeFiles en api/index.py sea robusta:

JSON
"includeFiles": ["templates/**", "static/**"]
(Esto ya parece estar hecho, pero verifícalo).

Ejecuta: git_sync.py "fix: absolute paths for jinja2 templates in vercel"

Explicación: En Vercel, el "Current Working Directory" (os.getcwd()) suele ser la raíz del proyecto (/var/task). Al forzar la ruta absoluta desde ahí, Jinja2 dejará de adivinar y encontrará los archivos que includeFiles copió.