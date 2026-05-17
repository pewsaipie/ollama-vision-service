# Ollama Vision Service – User Guide

## Overview
This repository provides a **lightweight REST API** that wraps Ollama's vision models. It is deliberately **decoupled** from any specific automation framework, making it easy to call from CI/CD pipelines, test suites, or any language that can make HTTP requests.

---

## 1. Prerequisites
- **Python 3.11+** (for local development)
- **Ollama** running and exposing its HTTP API (default `http://localhost:11434`).
- Optionally **Docker** if you prefer containerised deployment.

---

## 2. Installing the Service
### 2.1 Install via pip (editable mode)
```bash
# From the repository root
pip install -e .[api]
```
The optional `api` extra pulls in FastAPI, Uvicorn, and related dependencies.

### 2.2 Environment variables
| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | URL of the running Ollama server | `http://localhost:11434` |
| `OLLAMA_API_KEY` | Optional shared secret for API‑key authentication. If unset, the service is open to any caller. |
| `OLLAMA_VISION_MODEL` | Default model name used when the client does not specify one. | `llava` |

---

## 3. Running the Service
### 3.1 Development (hot‑reload)
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```
- Health check: `GET http://localhost:8000/health`
- OpenAPI UI: `GET http://localhost:8000/docs`

### 3.2 Production (Docker)
```dockerfile
# Build the image
docker build -t ollama-vision-service .

# Run the container (replace OLLAMA_HOST if Ollama lives elsewhere)
docker run -d \
  -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e OLLAMA_API_KEY=your‑secret-key \
  ollama-vision-service
```
The service will now listen on **port 8000** of the host.

---

## 4. API Reference
### 4.1 Health Endpoint
```
GET /health
Response: {"status": "ok"}
```
### 4.2 Inference Endpoint
```
POST /v1/infer
Content‑Type: application/json
Headers: X-API-Key: <your‑key>   # required only if OLLAMA_API_KEY is set

Body schema:
{
  "model": "llava",          # optional – defaults to env OLLAMA_VISION_MODEL
  "prompt": "Describe the image.",   # optional – defaults to a simple description prompt
  "images": ["https://example.com/img.png"]   # list of 1‑5 URLs (publicly reachable)
}
```
**Response**
```json
{
  "text": "<extracted plain‑text from the image>"
}
```
The endpoint currently forwards only the **first image** in the list to the core library. Extending to multiple images is straightforward – just loop over `req.images`.

---

## 5. Usage Examples
### 5.1 `curl`
```bash
curl -X POST http://localhost:8000/v1/infer \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your‑secret-key" \
     -d '{
           "model": "llava",
           "prompt": "Extract any license‑plate text.",
           "images": ["https://my.cdn.com/vehicle.jpg"]
         }'
```
### 5.2 Python client (using `httpx`)
```python
import httpx

API_URL = "http://localhost:8000/v1/infer"
HEADERS = {"X-API-Key": "your-secret-key"}
payload = {
    "model": "llava",
    "prompt": "Summarize the diagram.",
    "images": ["https://example.com/diagram.png"],
}

resp = httpx.post(API_URL, json=payload, headers=HEADERS)
print(resp.json()["text"])
```
### 5.3 Integration in CI (GitHub Actions)
```yaml
jobs:
  vision-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Call vision API
        run: |
          curl -s -X POST http://localhost:8000/v1/infer \
            -H "Content-Type: application/json" \
            -H "X-API-Key: ${{ secrets.VISION_API_KEY }}" \
            -d '{"images":["${{ github.workspace }}/assets/sample.png"]}'
```
---

## 6. Extending the Service
- **Multiple image handling** – iterate over `req.images` in `routes.py` and aggregate results.
- **Custom prompts** – expose a `mode` flag to switch between OCR, table extraction, etc.
- **Metrics** – plug in `prometheus_fastapi_instrumentator` and expose `/metrics`.
- **Authentication** – replace the simple API‑key with JWT/OAuth2 if needed.

---

## 7. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ConnectionError` from the endpoint | `OLLAMA_HOST` points to a non‑running Ollama server | Start Ollama or adjust the env var. |
| `403 Forbidden` despite sending key | `OLLAMA_API_KEY` mismatch or not set on the server | Ensure both server and client use the same secret. |
| No text returned, empty string | Model didn’t understand the prompt or image URL is inaccessible | Verify the image URL is publicly reachable or host it locally and pass a file URL. |

---

## 8. License
This project is released under the MIT License.

---

**Enjoy rapid, programmable visual inference across your organization!**