from fastapi import FastAPI
from app.core.settings import settings

app = FastAPI(title=settings.app_name)

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "env": settings.app_env}
