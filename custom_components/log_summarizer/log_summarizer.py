"""Log summarization service logic for Home Assistant."""

import os
import logging
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .log_utils import preprocess_log, extract_time_range
from .gpt_client import get_openai_client
from homeassistant.components.persistent_notification import async_create as notify

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

    async def handle_summarize_logs(call: ServiceCall):
        file_path = call.data.get("file_path", "/config/home-assistant.log")

        if not file_path or not os.path.isfile(file_path):
            _LOGGER.error("Invalid file path: %s", file_path)
            return

        if not os.path.abspath(file_path).startswith("/config/"):
            _LOGGER.error("Access to files outside /config is not allowed.")
            return

        def _read_file(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        raw_log = await hass.async_add_executor_job(_read_file, file_path)

        # Preprocess and trim log content
        reference_time = datetime.now()
        trimmed_log = await hass.async_add_executor_job(
            preprocess_log, raw_log, 100, 24, reference_time
        )
        start, end = extract_time_range(trimmed_log)

        model = call.data.get("model", "gpt-4o-mini")

        client = await hass.async_add_executor_job(get_openai_client, api_key)

        def _call_openai():
            prompt = f"""You are an expert in Home Assistant logs. Your task is to analyze the following log snippet and provide:

1. A list of actionable steps the user can take to resolve the reported errors and warnings. Refer to the specific entities or integrations involved (e.g., sensor names, platform names).
2. A brief summary of what was happening in the system.

You do not need to group similar issues — that has already been handled.

Log:
{trimmed_log}
"""
            return client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You explain Home Assistant logs and suggest actionable fixes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
            )

        response = await hass.async_add_executor_job(_call_openai)
        summary = response.choices[0].message.content

        await notify(hass, summary, title="GPT Log Summary")

        # Placeholder summary until GPT logic is integrated
        _LOGGER.info("Preprocessed %s, covering %s to %s", file_path, start, end)
        _LOGGER.debug("Filtered log:\n%s", trimmed_log)

    hass.services.register("log_summarizer", "summarize_logs", handle_summarize_logs)
    _LOGGER.info("✅ log_summarizer.summarize_logs service registered")
    return True
