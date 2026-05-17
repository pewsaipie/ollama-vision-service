"""
Ollama Vision Model API Service

Serves a single POST endpoint that:
  1. Accepts a prompt and image path in JSON
  2. Reads the image, encodes it as base64
  3. Sends it to Ollama's vision model
  4. Returns the model response as JSON
"""

import base64
import logging
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .vision.client import generate
from .vision.inference import extract_text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_HOST: str = "http://localhost:8080"
DEFAULT_MODEL: str = "qwen3.5:0.8b"  # or "bakllava", "llama3.2-vision", etc.

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
log = logging.getLogger("ollama-vision")

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class VisionRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for the vision model")
    image_path: str = Field(
        ...,
        description="Path to the image file on disk (JPEG, PNG, etc.)",
    )
    model: str = Field(
        default=DEFAULT_MODEL,
        description="Ollama model name (e.g. llava, bakllava, llama3.2-vision)",
    )


class VisionResponse(BaseModel):
    model: str
    prompt: str
    response: str
    image_path: str


class ErrorResponse(BaseModel):
    detail: str


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Ollama Vision API",
    version="1.0.0",
    description=(
        "Proxy endpoint that reads a local image, sends it to an Ollama vision"
        " model, and returns the generated text."
    ),
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _encode_image(image_path: str) -> str:
    """Read an image file and return its base64-encoded string."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@app.post("/v1/vision", response_model=VisionResponse, responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}})
async def vision(req: VisionRequest):
    """
    Accept a prompt and local image path, query an Ollama vision model,
    and return the model's textual response.
    """

    # 1. Read & encode image
    try:
        b64 = _encode_image(req.image_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=f"Permission denied: {exc}")

    # 2. Build the Ollama request payload
    ollama_payload = {
        "model": req.model,
        "prompt": req.prompt,
        "images": [b64],
        "stream": False,
    }

    ollama_url = f"{OLLAMA_HOST}/api/generate"

    # 3. Call Ollama
    log.info(
        "Sending to model=%s  prompt=%.80s  image=%s",
        req.model,
        req.prompt,
        req.image_path,
    )

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(ollama_url, json=ollama_payload)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Could not connect to Ollama at {OLLAMA_HOST}. "
                "Is the Ollama service running?"
            ),
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out (300 s).",
        )

    if resp.status_code != 200:
        detail = resp.text or f"Ollama returned HTTP {resp.status_code}"
        raise HTTPException(status_code=502, detail=detail)

    # 4. Parse response
    try:
        data = resp.json()
        model_response = data.get("response", "")
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to parse Ollama response.",
        )

    log.info("Response received (length=%d chars)", len(model_response))

    return VisionResponse(
        model=req.model,
        prompt=req.prompt,
        response=model_response,
        image_path=req.image_path,
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Simple liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Ollama Vision Service API server."""
    import uvicorn

    uvicorn.run("ollama_vision_service.server:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
