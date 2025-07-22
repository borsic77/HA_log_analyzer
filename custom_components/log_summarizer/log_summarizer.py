"""Log summarization service logic for Home Assistant."""

import os
import logging
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .log_utils import preprocess_log, extract_time_range, save_summary_to_file, read_log_file
from .gpt_client import (
    get_litellm_client,
    generate_prompt,
    call_llm_summary,
    fetch_available_models,
    get_provider_for_model,
)
from homeassistant.components.persistent_notification import async_create as notify

_LOGGER = logging.getLogger(__name__)



def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the log_summarizer service."""
    _LOGGER.info("✅ log_summarizer setup() called")

    # Access provider-specific api_keys under 'log_summarizer' from the configuration
    try:
        api_keys = config.get("log_summarizer", {}).get("api_keys")
        if not isinstance(api_keys, dict):
            raise KeyError("api_keys missing")
    except KeyError:
        _LOGGER.error("Missing 'api_keys' in configuration.yaml under 'log_summarizer'.")
        return False

    hass.data["log_summarizer_api_keys"] = api_keys

    # Fetch available models at startup
    models = fetch_available_models(api_keys)
    hass.data["log_summarizer_models"] = models
    _LOGGER.info("Available models: %s", models)

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
        provider = get_provider_for_model(model)
        api_key = api_keys.get(provider)
        if not api_key:
            _LOGGER.error("No API key configured for provider: %s", provider)
            return

        client_params = await hass.async_add_executor_job(get_litellm_client, provider, api_key)

        prompt = generate_prompt(trimmed_log)
        response = await hass.async_add_executor_job(call_llm_summary, client_params, model, prompt)
        summary = response.choices[0].message.content
        await hass.async_add_executor_job(save_summary_to_file, summary)

        await notify(hass, summary, title="GPT Log Summary")

        # Placeholder summary until GPT logic is integrated
        _LOGGER.info("Preprocessed %s, covering %s to %s", file_path, start, end)
        _LOGGER.debug("Filtered log:\n%s", trimmed_log)

    hass.services.register("log_summarizer", "summarize_logs", handle_summarize_logs)
    _LOGGER.info("✅ log_summarizer.summarize_logs service registered")

    async def handle_update_models(call: ServiceCall):
        models = fetch_available_models(api_keys)
        hass.data["log_summarizer_models"] = models
        _LOGGER.info("Updated available models: %s", models)

    hass.services.register("log_summarizer", "update_models", handle_update_models)
    _LOGGER.info("✅ log_summarizer.update_models service registered")
    return True
