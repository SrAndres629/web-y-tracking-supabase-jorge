from app.infrastructure.config.settings import settings

# Legacy names for backward compatibility
# These allow older code to continue using 'from app.config import DATABASE_URL' etc.
DATABASE_URL = settings.db.url
UPSTASH_REDIS_REST_URL = settings.redis.rest_url
UPSTASH_REDIS_REST_TOKEN = settings.redis.rest_token
META_PIXEL_ID = settings.meta.pixel_id
META_ACCESS_TOKEN = settings.meta.access_token
TEMPLATES_DIR = settings.templates_dir
STATIC_DIR = settings.static_dir

# Methods
resolve_tenant = settings.resolve_tenant
is_tenant_allowed = settings.is_tenant_allowed

# Compatibility export for 'settings.XXX' access
# Instead of a complex wrapper, we just use the new settings object directly
# as it already covers most names via Pydantic aliases or properties.
# If some legacy names are missing on the object, we can add them as monkeypatches
# or just ensure code uses the exported constants above.
