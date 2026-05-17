# Ollama Vision Service

A lightweight REST API wrapper around Ollama vision models for CI/CD and automation, packaged as a Python library.

## Features

- Simple Python client for interacting with Ollama's vision models.
- Optional FastAPI server for providing an HTTP endpoint.
- Support for various Ollama vision models (e.g., `llava`, `bakllava`, `llama3.2-vision`).
- Easy integration into automation scripts and CI/CD pipelines.

## Installation

You can install the library directly from PyPI (once published) or from a local clone.

### From PyPI (when available)

```bash
pip install ollama-vision-service
```

### From Source (Development)

Clone the repository and install in development mode:

```bash
git clone <repository-url>
cd ollama-vision-service
pip install -e .
```

To install with the optional API dependencies (for running the server):

```bash
pip install -e .[api]
```

## Usage

### As a Library

You can use the vision client directly in your Python code without running a server.

#### Basic Example

```python
import asyncio
from ollama_vision_service.vision.client import generate
from ollama_vision_service.vision.inference import extract_text

async def main():
    # Example: Describe an image using the low-level generate function
    image_path = "path/to/your/image.jpg"
    
    # Using the low-level generate function (requires base64 encoded image)
    import base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    result = await generate(
        model="llava",  # or any vision model you have installed in Ollama
        prompt="Describe the image in detail.",
        images=[base64_image],
    )
    print("Generate result:", result.get("response", ""))
    
    # Using the convenience extract_text function (takes a file path)
    text_result = await extract_text(image_path, model="llava")
    print("Extract text result:", text_result)

if __name__ == "__main__":
    asyncio.run(main())
```

### As a Server

If you prefer to interact with the service via HTTP, you can run the provided FastAPI server.

#### Starting the Server

After installing with the `[api]` extra:

```bash
ollama-vision-serve
```

Or using uvicorn directly:

```bash
uvicorn ollama_vision_service.server:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`.

#### API Endpoints

- `POST /v1/vision`: Accepts a prompt and local image path, queries an Ollama vision model, and returns the generated text.
- `GET /health`: Simple liveness probe.

#### Example Request (using curl)

```bash
curl -X POST "http://localhost:8000/v1/vision" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Describe this image in detail",
    "image_path": "/path/to/image.jpg",
    "model": "llava"
  }'
```

#### Example Request (using the provided test client)

```bash
python test_client.py --image /path/to/image.jpg --prompt "Describe this image"
```

### Server Entities

The server expects a JSON payload with the following fields for the `/v1/vision` endpoint:

- `prompt` (string, required): The text prompt for the vision model.
- `image_path` (string, required): Path to the image file on disk (JPEG, PNG, etc.).
- `model` (string, optional): Ollama model name (defaults to the value of `DEFAULT_MODEL` in the server configuration, which is set to `"qwen3.5:0.8b"` by default).

## Configuration

The server can be configured via environment variables:

- `OLLAMA_HOST`: URL of the local Ollama service (default: `http://localhost:11434`).
- `DEFAULT_MODEL`: Model name used when none is supplied in the request (default: `qwen3.5:0.8b`).

## Development

### Running Tests

To run the tests, install the package with test dependencies (if any) and run pytest:

```bash
pip install -e .[api]  # or just . if you don't need the API for tests
pytest
```

### Building the Package

To build a distribution file for uploading to PyPI:

```bash
pip install build
python -m build
```

This will create a source distribution and a wheel in the `dist/` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Ollama team for providing the vision models.
- Built with FastAPI and Pydantic for fast and reliable API development.