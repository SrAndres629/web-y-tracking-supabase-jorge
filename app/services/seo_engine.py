# =================================================================
# SEO_ENGINE.PY - The Silicon Valley Semantic Hub
# Jorge Aguirre Flores Web
# =================================================================
import json
from typing import Dict, Any, List, Optional
from app.config import settings

class SEOEngine:
    """
    Motor avanzado de SEO semántico y estructuración de datos.
    Genera metadatos y JSON-LD de alto impacto para SERPs.
    """
    
    BASE_URL = "https://jorgeaguirreflores.com"
    
    @staticmethod
    def get_global_schema() -> Dict[str, Any]:
        """Schema LocalBusiness: La base de la autoridad local"""
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Jorge Aguirre Flores",
            "image": f"{SEOEngine.BASE_URL}/static/images/og-image.webp",
            "@id": f"{SEOEngine.BASE_URL}/#organization",
            "url": SEOEngine.BASE_URL,
            "telephone": "+59164714751",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Equipetrol Calle 7 Este", # Ajustar si es necesario
                "addressLocality": "Santa Cruz de la Sierra",
                "addressRegion": "Santa Cruz",
                "addressCountry": "BO"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": -17.7667, # Coordenadas de Santa Cruz
                "longitude": -63.1833
            },
            "openingHoursSpecification": {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                "opens": "09:00",
                "closes": "20:00"
            },
            "sameAs": [
                "https://facebook.com/jorgeaguirreflores",
                "https://instagram.com/jorgeaguirreflores",
                "https://tiktok.com/@jorgeaguirreflores"
            ]
        }

    @staticmethod
    def get_service_schema(service: Dict[str, Any]) -> Dict[str, Any]:
        """Schema Service: Optimizado para resultados enriquecidos de servicios"""
        return {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": service.get("title", "Beauty Service"),
            "provider": {
                "@type": "LocalBusiness",
                "name": "Jorge Aguirre Flores"
            },
            "description": service.get("description", ""),
            "areaServed": "Santa Cruz de la Sierra",
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "Catálogo de Micropigmentación",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": service.get("title")
                        }
                    }
                ]
            }
        }

    @staticmethod
    def get_breadcrumb_schema(items: List[Dict[str, str]]) -> Dict[str, Any]:
        """Breadcrumbs: Claridad jerárquica para Google"""
        elements = []
        for i, item in enumerate(items):
            elements.append({
                "@type": "ListItem",
                "position": i + 1,
                "name": item["name"],
                "item": f"{SEOEngine.BASE_URL}{item['path']}"
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": elements
        }

    @staticmethod
    def generate_all_json_ld(schemas: List[Dict[str, Any]]) -> str:
        """Encapsula múltiples schemas en bloques script"""
        output = ""
        for schema in schemas:
            output += f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>\n'
        return output

    @staticmethod
    def get_page_metadata(path: str, custom_meta: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Gestor de metatags dinámicos"""
        defaults = {
            "title": "Jorge Aguirre Flores | Maquillaje Permanente Santa Cruz",
            "description": "30 años de experiencia en Microblading y Micropigmentación. El estándar de oro en estética en Bolivia.",
            "og_title": "Jorge Aguirre Flores | Experto en Mirada",
            "og_image": f"{SEOEngine.BASE_URL}/static/images/og-image.webp",
            "canonical": f"{SEOEngine.BASE_URL}{path}"
        }
        
        if custom_meta:
            defaults.update(custom_meta)
            
        return defaults
