try:
    from main import app
    from mangum import Mangum
    handler = Mangum(app)
except Exception as e:
    import traceback
    error_msg = f"CRITICAL BOOT ERROR: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    from fastapi import FastAPI
    # Try local fallback if mangum missing? No, we need it.
    try:
        from mangum import Mangum
        HAS_MANGUM = True
    except:
        HAS_MANGUM = False

    fallback_app = FastAPI()
    
    @fallback_app.get("/{path:path}")
    async def catch_all(path: str):
        return {
            "status": "CRITICAL_BOOT_FAILURE",
            "error": str(e),
            "traceback": traceback.format_exc().splitlines(),
            "has_mangum": HAS_MANGUM
        }
        
    if HAS_MANGUM:
        handler = Mangum(fallback_app)
    else:
        # Last resort: raw WSGI/ASGI adapter or just fail (will be 500 if mangum missing)
        # But we caught the error earlier, so let's try to survive just to print logs
        raise e
