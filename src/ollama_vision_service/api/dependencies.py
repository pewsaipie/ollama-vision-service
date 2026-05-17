import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Simple API‑key auth – load from env (or leave empty for open access)
API_KEY = os.getenv("OLLAMA_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Raise 403 if a non‑empty API key is configured and does not match."""
    if API_KEY and api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    # If no API_KEY configured, or matches, request proceeds.
    return True