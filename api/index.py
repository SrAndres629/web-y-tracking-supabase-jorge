from fastapi import FastAPI
from fastapi.responses import JSONResponse

# ZERO DEPENDENCY TEST
app = FastAPI()

@app.get("/{full_path:path}")
async def health(full_path: str):
    return JSONResponse(content={
        "status": "baseline_success",
        "message": "If you see this, Vercel Ruby/Python runtime is WORKING",
        "path": full_path
    })

handler = app
