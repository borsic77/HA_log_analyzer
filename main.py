import streamlit as st
from openai import OpenAI
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

def preprocess_log(raw_log: str, max_lines: int = 100, hours_back: int = 24, reference_time: datetime = None) -> str:
    """
    Extracts relevant log lines from the last `hours_back` hours and groups duplicates,
    preserving the latest timestamp and variable content.
    """
    SEVERITIES = ["ERROR", "WARNING", "CRITICAL", "FATAL"]
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

        if level not in SEVERITIES or timestamp < time_threshold:
            continue

        normalized = re.sub(r"custom integration \w+", "custom integration ...", message)
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

# Load API key from environment variable or Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- Streamlit UI ---
st.set_page_config(page_title="Home Assistant Log Summarizer", layout="centered")
st.title("📘 Home Assistant Log Summarizer")

st.markdown("""
Upload your `home-assistant.log` file and let GPT-4 summarize warnings, errors, and important events.
""")

# --- File uploader ---
uploaded_file = st.file_uploader("Choose a Home Assistant log file", type=["log", "txt"])

debug_mode = st.checkbox("Skip LLM query (debug mode)")
hours_back = st.slider("How many hours back to analyze?", min_value=1, max_value=168, value=24)

if uploaded_file:
    raw_log = uploaded_file.read().decode("utf-8", errors="ignore")

    reference_time = datetime.now()
    trimmed_log = preprocess_log(raw_log, max_lines=100, hours_back=hours_back, reference_time=reference_time)

    # Extract actual timestamps from trimmed lines
    log_timestamps = []
    for line in trimmed_log.splitlines():
        match = re.match(r"\[\d+x\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line) or \
                re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line)
        if match:
            try:
                log_timestamps.append(datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f"))
            except ValueError:
                pass

    if log_timestamps:
        start_time = min(log_timestamps)
        end_time = max(log_timestamps)
        st.info(f"⏱️ Analyzing logs from: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("⏱️ No valid timestamps found in filtered logs.")

    if debug_mode:
        st.subheader("🧾 Filtered Log Output (Debug Mode)")
        st.code(trimmed_log, language="text")
        st.download_button("Download filtered log", trimmed_log, file_name="filtered_log.txt")
    else:
        prompt = f"""You are an expert in Home Assistant logs. Your task is to analyze the following log snippet and provide:

1. A list of actionable steps the user can take to resolve the reported errors and warnings. Refer to the specific entities or integrations involved (e.g., sensor names, platform names).
2. A brief summary of what was happening in the system.

You do not need to group similar issues — that has already been handled.

Log:
{trimmed_log}
"""
        
                    messages=[
                        {"role": "system", "content": "You help users understand Home Assistant logs clearly and concisely."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800,
                )
                summary = response.choices[0].message.content
                st.subheader("📝 Summary")
                st.markdown(summary)

            except Exception as e:
                st.error(f"Error contacting OpenAI API: {e}")
else:
    st.info("Please upload a log file to begin.")

# Optional: footer
st.markdown("---")
st.caption("Created by [Boris Legradic] ·  [GitHub link coming soon]")