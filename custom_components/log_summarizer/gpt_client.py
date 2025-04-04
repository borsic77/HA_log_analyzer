"""OpenAI client setup for log summarization."""

import os
from openai import OpenAI

def get_openai_client() -> OpenAI:
    """Return an OpenAI client instance configured with the API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(api_key=api_key)
