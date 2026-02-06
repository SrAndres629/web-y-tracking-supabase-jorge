try:
    from main import app
    from mangum import Mangum
    handler = Mangum(app)
except Exception as e:
    import traceback
    error_msg = f"CRITICAL BOOT ERROR: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    from fastapi import FastAPI
    from mangum import Mangum
    
    fallback_app = FastAPI()
    
    @fallback_app.get("/{path:path}")
    async def catch_all(path: str):
        return {
            "status": "CRITICAL_BOOT_FAILURE",
            "error": str(e),
            "traceback": traceback.format_exc().splitlines()
        }
        
    handler = Mangum(fallback_app)
