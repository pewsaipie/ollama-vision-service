from fastapi import FastAPI
from .routes import router as vision_router

app = FastAPI(
    title="Ollama Vision Service",
    version="0.1.0",
    description="REST API for Ollama vision inference – designed for CI/CD and test‑automation integration."
)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

app.include_router(vision_router, prefix="/v1")