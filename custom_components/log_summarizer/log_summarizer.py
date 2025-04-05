"""Log summarization service logic for Home Assistant."""

import os
import logging
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .log_utils import preprocess_log, extract_time_range
from .gpt_client import get_openai_client

_LOGGER = logging.getLogger(__name__)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the log_summarizer service."""
    _LOGGER.info("✅ log_summarizer setup() called")

    # Access the api_key under 'log_summarizer' from the configuration
    try:
        api_key = config.get("log_summarizer", {}).get("api_key")
        if not api_key:
            raise KeyError("api_key missing")
    except KeyError:
        _LOGGER.error("Missing 'api_key' in configuration.yaml under 'log_summarizer'.")
        return False

    hass.data["log_summarizer_api_key"] = api_key

    def handle_summarize_logs(call: ServiceCall):
        file_path = call.data.get("file_path", "/config/home-assistant.log")

        if not file_path or not os.path.isfile(file_path):
            _LOGGER.error("Invalid file path: %s", file_path)
            return

        if not os.path.abspath(file_path).startswith("/config/"):
            _LOGGER.error("Access to files outside /config is not allowed.")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            raw_log = f.read()

        # Preprocess and trim log content
        reference_time = datetime.now()
        trimmed_log = preprocess_log(raw_log, max_lines=100, hours_back=24, reference_time=reference_time)
        start, end = extract_time_range(trimmed_log)

        model = call.data.get("model", "gpt-4o-mini")

        try:
            client = get_openai_client(api_key)
            prompt = f"""You are an expert in Home Assistant logs. Your task is to analyze the following log snippet and provide:

1. A list of actionable steps the user can take to resolve the reported errors and warnings. Refer to the specific entities or integrations involved (e.g., sensor names, platform names).
2. A brief summary of what was happening in the system.

You do not need to group similar issues — that has already been handled.

Log:
{trimmed_log}
"""
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You explain Home Assistant logs and suggest actionable fixes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
            )
            summary = response.choices[0].message.content

            hass.components.persistent_notification.create(
                summary, title="GPT Log Summary"
            )
        except Exception as e:
            _LOGGER.error("Failed to summarize log using OpenAI: %s", e)

        # Placeholder summary until GPT logic is integrated
        _LOGGER.info("Preprocessed %s, covering %s to %s", file_path, start, end)
        _LOGGER.debug("Filtered log:\n%s", trimmed_log)

    hass.services.register("log_summarizer", "summarize_logs", handle_summarize_logs)
    _LOGGER.info("✅ log_summarizer.summarize_logs service registered")
    return True
