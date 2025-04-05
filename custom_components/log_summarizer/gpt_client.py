"""OpenAI client setup for log summarization."""

import os
from openai import OpenAI

def get_openai_client(api_key: str) -> OpenAI:
    """Return an OpenAI client configured with the given API key."""
    return OpenAI(api_key=api_key)