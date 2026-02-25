from dataclasses import dataclass


@dataclass(frozen=True)
class PageRoutes:
    """Rutas de páginas públicas (Frontend)"""
    HOME: str = "/"
    TRACKING_MOTOR: str = "/tracking-motor"
    MICROBLADING: str = "/microblading"
    BROWS: str = "/cejas"
    EYES: str = "/ojos"
    LIPS: str = "/labios"
    ONBOARDING: str = "/onboarding"
    PRIVACY: str = "/privacidad"
    PRIVACY_EN: str = "/privacy"
    TERMS: str = "/terminos"
    TERMS_EN: str = "/terms"
    COOKIES: str = "/cookies"

@dataclass(frozen=True)
class AdminRoutes:
    """Rutas del panel de administración"""
    PREFIX: str = "/admin"
    DASHBOARD: str = "/dashboard"
    STATS: str = "/stats"
    CONFIRM_SALE: str = "/confirm/{visitor_id}"
    SIGNALS: str = "/signals"

@dataclass(frozen=True)
class TrackingRoutes:
    """Rutas del motor de tracking (API)"""
    EVENT: str = "/track/event"
    LEAD: str = "/track/lead"
    INTERACTION: str = "/track/interaction"
    HOOKS_PROCESS: str = "/hooks/process-event"
    HEALTH: str = "/track/health"
    ONBOARDING: str = "/onboarding"  # POST Method

@dataclass(frozen=True)
class HealthRoutes:
    """Rutas de salud y diagnóstico"""
    HEALTH: str = "/health"
    HEALTH_CHECK: str = "/healthcheck"
    DIAGNOSTICS: str = "/health/diagnostics"
    CONFIG: str = "/health/config"
    ASSETS: str = "/health/assets"
    PING: str = "/ping"
    PREWARM_DEBUG: str = "/__prewarm_debug"
    PREWARM: str = "/health/prewarm"

@dataclass(frozen=True)
class SEORoutes:
    """Rutas de SEO y metadatos"""
    SITEMAP: str = "/sitemap.xml"
    ROBOTS: str = "/robots.txt"
    METADATA: str = "/seo-meta"

@dataclass(frozen=True)
class RouteRegistry:
    """Registro central de rutas del sistema"""
    PAGES: PageRoutes = PageRoutes()
    ADMIN: AdminRoutes = AdminRoutes()
    TRACKING: TrackingRoutes = TrackingRoutes()
    HEALTH: HealthRoutes = HealthRoutes()
    SEO: SEORoutes = SEORoutes()

# Instancia global para importar en todo el proyecto
urls = RouteRegistry()
