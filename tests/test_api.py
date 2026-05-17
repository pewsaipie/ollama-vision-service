import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from ollama_vision_service.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("ollama_vision_service.api.routes.extract_text")
def test_infer_endpoint(mock_extract):
    mock_extract.return_value = "mocked vision output"
    payload = {
        "model": "llava",
        "prompt": "Describe image",
        "images": ["https://example.com/img.png"]
    }
    response = client.post("/v1/infer", json=payload)
    assert response.status_code == 200
    assert response.json() == {"text": "mocked vision output"}
