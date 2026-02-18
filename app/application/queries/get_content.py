"""
📝 Get Content Query.

Consulta: Obtener contenido dinámico (servicios, contacto).
Con cache de 3 niveles: RAM -> Redis -> DB.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.application.interfaces.cache_port import ContentCachePort
from app.core.result import Result


@dataclass(frozen=True)
class GetContentQuery:
    """Input para la query."""

    key: str
    use_fallback: bool = True  # Usar fallback si no está en cache


class GetContentHandler:
    """
    Handler para obtener contenido con cache.

    Implementa patrón Cache-Aside:
    1. Intentar leer de cache (RAM/Redis)
    2. Si miss: leer de DB
    3. Guardar en cache para próximas lecturas
    """

    # Fallbacks hardcodeados para resilience
    FALLBACKS = {
        "services_config": [
            {
                "id": "microblading",
                "title": "Microblading 3D",
                "subtitle": "Efecto Pelo a Pelo",
                "description": "Técnica pelo a pelo para cejas ultra naturales.",
                "icon": "fa-eye-dropper",
                "image": "/static/images/service_brows.webp",
                "rating": "4.9",
                "clients": "+620",
                "badges": ["Más Pedido", "100% Natural", "2-3 años"],
                "benefits": ["2 hrs sesión", "Sin dolor", "Retoque incluido"],
            },
            {
                "id": "eyeliner",
                "title": "Delineado Permanente",
                "subtitle": "Efecto Pestañas",
                "description": "Despierta con una mirada intensa y expresiva.",
                "icon": "fa-eye",
                "image": "/static/images/service_eyes.webp",
                "rating": "4.9",
                "clients": "+480",
                "badges": ["Sin Dolor", "Efecto Pestañas", "2-3 años"],
                "benefits": ["1.5 hrs sesión", "Anestesia tópica", "Resultados inmediatos"],
            },
            {
                "id": "lips",
                "title": "Labios Full Color",
                "subtitle": "Corrección y Volumen",
                "description": "Correcciones y luce una boca jugosa y saludable.",
                "icon": "fa-kiss-wink-heart",
                "image": "/static/images/service_lips.webp",
                "rating": "5.0",
                "clients": "+400",
                "badges": ["Premium", "Color Natural", "1-2 años"],
                "benefits": ["2 hrs sesión", "Corrige volumen", "Efecto rejuvenecedor"],
            },
        ],
        "contact_config": {
            "whatsapp": "https://wa.me/59164714751",
            "phone": "+591 647 14 751",
            "email": "info@jorgeaguirreflores.com",
            "address": "Santa Cruz de la Sierra, Bolivia",
            "maps_url": "https://maps.google.com/?q=Santa+Cruz+de+la+Sierra+Bolivia",
            "location": "Santa Cruz de la Sierra",
            "instagram": "https://instagram.com/jorgeaguirreflores",
            "facebook": "https://facebook.com/jorgeaguirreflores",
            "tiktok": "https://tiktok.com/@jorgeaguirreflores",
            "cta_text": "Hola Jorge, vi su web y me interesa una valoración para micropigmentación.",
            "cta_assessment": "Hola Jorge, quiero agendar mi diagnóstico gratuito y ver la geometría de mi rostro.",
        },
    }

    def __init__(self, cache: ContentCachePort):
        self.cache = cache

    async def handle(self, query: GetContentQuery) -> Result[Any, str]:
        """
        Obtiene contenido con estrategia de fallback.

        1. Intentar cache
        2. Si miss y use_fallback: retornar fallback
        3. En background: refrescar cache desde DB
        """
        try:
            # 1. Intentar cache
            cached = await self.cache.get(query.key)
            if cached is not None:
                return Result.ok(cached)

            # 2. Si tenemos fallback permitido, usarlo inmediatamente
            if query.use_fallback and query.key in self.FALLBACKS:
                fallback_data = self.FALLBACKS[query.key]

                # En background: refrescar desde DB
                import asyncio

                asyncio.create_task(self._refresh_cache(query.key))

                return Result.ok(fallback_data)

            # 3. No hay fallback, intentar DB directo
            db_data = await self._fetch_from_db(query.key)
            if db_data is not None:
                await self.cache.set(query.key, db_data, ttl=3600)
                return Result.ok(db_data)

            return Result.err(f"Content not found: {query.key}")

        except Exception as e:
            # Fallback último recurso
            if query.use_fallback and query.key in self.FALLBACKS:
                return Result.ok(self.FALLBACKS[query.key])
            return Result.err(str(e))

    async def _refresh_cache(self, key: str) -> None:
        """Refresca cache desde DB (background)."""
        try:
            data = await self._fetch_from_db(key)
            if data:
                await self.cache.set(key, data, ttl=3600)
        except Exception:
            pass  # Silencioso en background

    async def _fetch_from_db(self, key: str) -> Optional[Any]:
        """Fetch desde base de datos."""
        # TODO: Implementar con repositorio de contenido
        # Por ahora retorna None para usar fallback
        return None
