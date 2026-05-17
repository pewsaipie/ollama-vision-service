"""Ollama Vision Service.

A lightweight REST API wrapper around Ollama vision models for CI/CD and automation.
"""

from .vision.client import generate
from .vision.inference import extract_text

__all__ = [
    "generate",
    "extract_text",
]