# =================================================================
# SEO.PY - The Google Passport (API Interface)
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
    content = f"""# ==========================================
# 💎 JORGE AGUIRRE FLORES - SEO ROBOTS.TXT
# Silicon Valley Advanced Crawl Protocol
# ==========================================

User-agent: *
Allow: /
Disallow: /admin
Disallow: /api
Disallow: /maintenance
Disallow: /*?fbclid=
Disallow: /*?utm_source=
Disallow: /*?gclid=

# Crawl Budget Optimization
User-agent: SemrushBot
Crawl-delay: 10

User-agent: AhrefsBot
Crawl-delay: 10

# Block AI & Scrapers (Protect IP)
User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Anthropic-AI
Disallow: /

User-agent: Claude-Web-Crawler
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: YouBot
Disallow: /

# Sitemap Index (Master Map)
Sitemap: https://jorgeaguirreflores.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_index():
    """
    Sitemap Index: El mapa maestro para Google.
    Silicon Valley Pattern: Divide and Conquer.
    """
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://jorgeaguirreflores.com/sitemap-pages.xml</loc>
    </sitemap>
    <sitemap>
        <loc>https://jorgeaguirreflores.com/sitemap-services.xml</loc>
    </sitemap>
</sitemapindex>"""
    return Response(content=content, media_type="application/xml")


@router.get("/sitemap-pages.xml", response_class=Response)
async def sitemap_pages():
    """Sitemap de páginas estáticas principales."""
    base_url = "https://jorgeaguirreflores.com"
    pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
    ]
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for page in pages:
        xml_content += f'<url><loc>{base_url}{page["loc"]}</loc><lastmod>2024-02-10</lastmod><changefreq>{page["changefreq"]}</changefreq><priority>{page["priority"]}</priority></url>'
    xml_content += "</urlset>"
    return Response(content=xml_content, media_type="application/xml")


@router.get("/sitemap-services.xml", response_class=Response)
async def sitemap_services():
    """Sitemap dinámico de servicios (Deep Crawl)."""
    from app.services import get_services_config
    services = await get_services_config()
    base_url = "https://jorgeaguirreflores.com/servicios" # Asumiendo esta estructura
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for srv in services:
        xml_content += f'<url><loc>{base_url}/{srv["id"]}</loc><lastmod>2024-02-10</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>'
    xml_content += "</urlset>"
    return Response(content=xml_content, media_type="application/xml")
