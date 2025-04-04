"""OpenAI client setup for log summarization."""

import os
from openai import OpenAI

from homeassistant.const import CONF_API_KEY

def get_openai_client(hass=None) -> OpenAI:
    if hass:
        api_key = hass.data.get("log_summarizer_api_key")
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OpenAI API key is not set.")
    return OpenAI(api_key=api_key)