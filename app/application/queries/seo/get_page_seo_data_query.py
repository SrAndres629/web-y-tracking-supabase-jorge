from typing import Any, Dict, List, Optional

from app.services.seo_engine import SEOEngine


class GetPageSEODataQuery:
    async def execute(
        self, path: str, context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the query to retrieve SEO metadata and schemas for a given path.
        """
        if context_data is None:
            context_data = {}

        # Page metadata
        seo_meta = SEOEngine.get_page_metadata(
            path,
            {
                "title": "Jorge Aguirre Flores | Experto en Microblading y Estética Avanzada",
                "description": "Transforma tu mirada con el mejor especialista en Microblading de Santa Cruz. 30 años de trayectoria garantizan resultados naturales y artísticos.",
            },
        )

        # Schemas
        schemas: List[Dict[str, Any]] = [
            SEOEngine.get_global_schema(),
            SEOEngine.get_breadcrumb_schema([{"name": "Inicio", "path": "/"}]),
        ]

        # You can add more dynamic schema generation here based on path or context_data

        return {**seo_meta, "json_ld": SEOEngine.generate_all_json_ld(schemas)}
