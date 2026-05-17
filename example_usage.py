"""
Example usage of the ollama-vision-service library.

This file demonstrates two ways to use the library:
1. Using the core vision client directly (without the FastAPI server).
2. Running the FastAPI server (if you want to provide an HTTP endpoint).

Note: To actually get responses from Ollama, you need to have the Ollama service running
and a vision model available (e.g., `llava`, `bakllava`, etc.).
"""

# Example 1: Using the core vision client directly
async def example_direct_usage():
    """Example of using the vision client directly."""
    from ollama_vision_service.vision.client import generate
    from ollama_vision_service.vision.inference import extract_text
    import base64
    from pathlib import Path

    # Example: Describe an image using the low-level generate function
    image_path = "path/to/your/image.jpg"  # Replace with your image path
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Call Ollama's generate endpoint
    result = await generate(
        model="llava",  # or any vision model you have installed in Ollama
        prompt="Describe the image in detail.",
        images=[base64_image],
    )
    print("Direct client result:")
    print(result.get("response", ""))

    # Example: Using the convenience extract_text function
    # Note: extract_text expects a file path, not base64
    text_result = await extract_text(image_path, model="llava")
    print("\nExtract text result:")
    print(text_result)


# Example 2: Running the FastAPI server
def example_run_server():
    """Example of how to run the server programmatically."""
    import uvicorn
    from ollama_vision_service.server import app

    # Run the server on http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # To run the direct usage example, you would need to be in an async context.
    # For simplicity, we'll just show how to import and note that you need to run it in an async loop.
    print("To use the direct vision client, call the async functions from an async context.")
    print("For example:")
    print("  import asyncio")
    print("  asyncio.run(example_direct_usage())")
    print()
    print("To run the server, you can execute:")
    print("  uvicorn ollama_vision_service.server:app --host 0.0.0.0 --port 8000")
    print("Or run this script and it will start the server (comment/uncomment as needed).")
    print()
    # Uncomment the following line to run the server when this script is executed.
    # example_run_server()