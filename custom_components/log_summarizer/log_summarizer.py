"""Log summarization service logic for Home Assistant."""

import os
import logging
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .log_utils import preprocess_log, extract_time_range

_LOGGER = logging.getLogger(__name__)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the log_summarizer service."""
    
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

        # Placeholder summary until GPT logic is integrated
        _LOGGER.info("Preprocessed %s, covering %s to %s", file_path, start, end)
        _LOGGER.debug("Filtered log:\n%s", trimmed_log)

        # This is where the GPT logic will be added later

    hass.services.register("log_summarizer", "summarize_logs", handle_summarize_logs)
    _LOGGER.info("log_summarizer integration initialized")
    return True
