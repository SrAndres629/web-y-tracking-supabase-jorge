from fastapi import APIRouter, Request, Response

from app.application.queries.seo.get_page_seo_data_query import GetPageSEODataQuery
from app.core.urls import urls

router = APIRouter()


@router.get(urls.SEO.SITEMAP, response_class=Response, summary="XML Sitemap")
async def sitemap_xml():
    """Generates the sitemap.xml for search engines."""
    # In a real application, this would be dynamically generated from your content.
    # For now, return a basic sitemap.
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://jorgeaguirreflores.com{urls.PAGES.HOME}</loc>
        <lastmod>2026-02-10</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://jorgeaguirreflores.com{urls.PAGES.PRIVACY}</loc>
        <lastmod>2026-02-18</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://jorgeaguirreflores.com{urls.PAGES.TERMS}</loc>
        <lastmod>2026-02-18</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
</urlset>
"""
    return Response(content=content, media_type="application/xml")


@router.get(urls.SEO.ROBOTS, response_class=Response, summary="Robots exclusion file")
async def robots_txt():
    """Provides instructions for web robots."""
    content = f"""User-agent: *
Allow: /

Sitemap: https://jorgeaguirreflores.com{urls.SEO.SITEMAP}
"""
    return Response(content=content, media_type="text/plain")


@router.get(urls.SEO.METADATA, summary="Get SEO metadata for a page (JSON)")
async def get_seo_metadata(request: Request, path: str = "/"):
    """
    Returns SEO metadata (title, description, JSON-LD) for a given page path.
    """
    query = GetPageSEODataQuery()
    # Pass path directly, context_data can be added if needed for dynamic metadata
    seo_data = await query.execute(path=path)
    return seo_data


# The actual SEO metadata for pages will be fetched by the pages themselves
# using GetPageSEODataQuery, not via a separate endpoint from the browser.
# This /seo-meta endpoint is mainly for demonstration or specific integrations.
