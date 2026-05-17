import httpx
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


async def _request(endpoint: str, payload: dict) -> dict:
    async with httpx.AsyncClient(base_url=OLLAMA_HOST, timeout=30) as client:
        resp = await client.post(endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()


async def generate(model: str, prompt: str, images: list[str] | None = None) -> dict:
    """Low-level call to Ollama's /api/generate endpoint."""
    payload: dict = {"model": model, "prompt": prompt}
    if images:
        payload["images"] = images
    return await _request("/api/generate", payload)