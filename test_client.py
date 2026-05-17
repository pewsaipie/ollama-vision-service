#!/usr/bin/env python3
"""
Simple test client for the Ollama Vision API.

Usage:
    python test_client.py --image /path/to/image.jpg --prompt "Describe this image"
"""

import argparse
import json
import sys
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser(description="Test the Ollama Vision API")
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--image", required=True, help="Path to image file")
    parser.add_argument("--prompt", default="Describe this image in detail.", help="Text prompt")
    parser.add_argument("--model", default=None, help="Ollama model (default: server default)")
    args = parser.parse_args()

    if not Path(args.image).is_file():
        print(f"Error: image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "prompt": args.prompt,
        "image_path": str(Path(args.image).resolve()),
    }
    if args.model:
        payload["model"] = args.model

    url = f"{args.host.rstrip('/')}/v1/vision"

    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        resp = httpx.post(url, json=payload, timeout=300.0)
    except httpx.ConnectError:
        print("Error: Could not connect. Is the server running?", file=sys.stderr)
        sys.exit(1)

    # Debug: Print raw response text to see what's being returned
    print(f"Raw response status: {resp.status_code}")
    print(f"Raw response headers: {resp.headers}")
    print(f"Raw response text: {resp.text}")
    print()

    if resp.status_code != 200:
        print(f"Error HTTP {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    # Try to parse as JSON - handle both JSON and plain text responses
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        result = resp.json()
        print("=== JSON Response ===")
        print(f"Model:  {result['model']}")
        print(f"Image:  {result['image_path']}")
        print(f"Prompt: {result['prompt']}")
        print(f"---\n{result['response']}\n---")
    else:
        # Handle non-JSON response - treat as plain text
        print("=== Text Response ===")
        print(resp.text)


if __name__ == "__main__":
    main()
