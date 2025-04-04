"""
log_utils.py

Provides helper functions for filtering and preprocessing Home Assistant logs.
Used by both the Streamlit interface and the Home Assistant custom integration.
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Tuple, List

def preprocess_log(raw_log: str, max_lines: int = 100, hours_back: int = 24, reference_time: datetime = None) -> str:
    # Define the log levels of interest
    SEVERITIES = ["ERROR", "WARNING", "CRITICAL", "FATAL"]
    # Regex pattern to match log entries
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+(\w+)\s+\([^)]+\)\s+\[([^\]]+)\]\s+(.*)$")
    reference_time = reference_time or datetime.now()
    time_threshold = reference_time - timedelta(hours=hours_back)

    grouped_logs = defaultdict(list)
    for line in raw_log.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        timestamp_str, level, source, message = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            continue
        # Filter out logs that are not of interest or are older than the time threshold
        if level not in SEVERITIES or timestamp < time_threshold:
            continue
        # Normalize the message for grouping
        normalized = re.sub(r"custom integration \w+", "custom integration ...", message)
        # Group logs by normalized message
        grouped_logs[normalized].append((timestamp_str, line.strip()))

    result_lines = []
    for normalized_msg, occurrences in grouped_logs.items():
        latest_entry = max(occurrences, key=lambda x: x[0])
        count = len(occurrences)
        if count > 1:
            result_lines.append(f"[{count}x] {latest_entry[1]}")
        else:
            result_lines.append(latest_entry[1])

    return "\n".join(result_lines[:max_lines])

def extract_time_range(processed_log: str) -> Tuple[datetime, datetime]:
    timestamps = []
    # Extract timestamps from the processed log to determine the time range
    for line in processed_log.splitlines():
        # Try to extract timestamp from grouped log line (e.g., "[2x] 2025-...") or raw line
        match = re.match(r"\[\d+x\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line) or \
                re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line)
        if match:
            try:
                timestamps.append(datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f"))
            except ValueError:
                continue
    if timestamps:
        return min(timestamps), max(timestamps)
    return None, None