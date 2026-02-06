# =================================================================
# SEO.PY - The Google Passport
# Jorge Aguirre Flores Web
# =================================================================
from fastapi import APIRouter, Response, Request
from app.config import settings

router = APIRouter(tags=["SEO"])

@router.get("/robots.txt", response_class=Response)
async def robots_txt():
    """
    Reglas claras para Googlebot.
    Protege áreas privadas (/admin) y expone el mapa del sitio.
    """
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api
Disallow: /maintenance

Sitemap: https://jorgeaguirreflores.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml():
    """
    Mapa del sitio dinámico.
    Lista todas las páginas importantes para indexación rápida.
    """
    base_url = "https://jorgeaguirreflores.com"
    
    # Static pages priority list
    pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
        # Add internal landing page variants if we had clean URLs for them
    ]
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    
    for page in pages:
        xml_content += f"""    <url>
        <loc>{base_url}{page['loc']}</loc>
        <lastmod>2024-02-06</lastmod>
        <changefreq>{page['changefreq']}</changefreq>
        <priority>{page['priority']}</priority>
    </url>
"""
        
    xml_content += "</urlset>"
    
    return Response(content=xml_content, media_type="application/xml")
