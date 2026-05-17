from .client import generate
import os
from typing import Optional

async def extract_text(image_path: str, model: Optional[str] = None) -> str:
    """
    Convenience wrapper: call Ollama's vision model with a prompt to get plain text.
    By default uses model name from env var or "llava".
    """
    effective_model = model or os.getenv("OLLAMA_VISION_MODEL", "llava")
    result = await generate(
        model=effective_model,
        prompt="Describe the image in plain text.",
        images=[image_path],
    )
    # Ollama returns: {"choices":[{"message":{"content":"..."}}...]}
    return result["choices"][0]["message"]["content"]