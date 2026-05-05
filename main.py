"""
TaxLegal AI — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from backend.startup import run_startup
from backend.routes.auth import router as auth_router
from backend.routes.matters import router as matters_router
from backend.routes.admin import router as admin_router
from backend.routes.laws import router as laws_router
from backend.config import APP_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TaxLegal AI...")
    await run_startup()
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down TaxLegal AI...")


app = FastAPI(
    title="TaxLegal AI",
    description="AI-powered Tax & Legal Advisory Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth_router)
app.include_router(matters_router)
app.include_router(admin_router)
app.include_router(laws_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "TaxLegal AI", "version": "1.0.0"}


@app.get("/api/models")
async def get_models():
    from backend.config import get_available_models
    return {"models": get_available_models()}


# Serve React frontend
_dist = Path(__file__).parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/assets", StaticFiles(directory=str(_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        index = _dist / "index.html"
        return FileResponse(str(index))
else:
    @app.get("/")
    async def root():
        return {"message": "TaxLegal AI API running. Frontend not built yet."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=False)
