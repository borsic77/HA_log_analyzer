"""Log summarization service logic for Home Assistant."""

import os
import logging
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .log_utils import preprocess_log, extract_time_range, save_summary_to_file, read_log_file
from .gpt_client import get_openai_client, generate_prompt, call_openai_summary
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

        raw_log = await hass.async_add_executor_job(read_log_file, file_path)

        # Preprocess and trim log content
        reference_time = datetime.now()
        trimmed_log = await hass.async_add_executor_job(
            preprocess_log, raw_log, 100, 24, reference_time
        )
        start, end = extract_time_range(trimmed_log)

        model = call.data.get("model", "gpt-4o-mini")

        client = await hass.async_add_executor_job(get_openai_client, api_key)

        prompt = generate_prompt(trimmed_log)
        response = await hass.async_add_executor_job(call_openai_summary, client, model, prompt)
        summary = response.choices[0].message.content
        await hass.async_add_executor_job(save_summary_to_file, summary)

        await notify(hass, summary, title="GPT Log Summary")

        # Placeholder summary until GPT logic is integrated
        _LOGGER.info("Preprocessed %s, covering %s to %s", file_path, start, end)
        _LOGGER.debug("Filtered log:\n%s", trimmed_log)

    hass.services.register("log_summarizer", "summarize_logs", handle_summarize_logs)
    _LOGGER.info("✅ log_summarizer.summarize_logs service registered")
    return True
