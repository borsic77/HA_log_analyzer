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
    # Define severity levels for filtering log entries
    SEVERITIES = ["ERROR", "WARNING", "CRITICAL", "FATAL"]
    # Regular expression pattern to match log entries
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+(\w+)\s+\([^)]+\)\s+\[([^\]]+)\]\s+(.*)$")
    reference_time = reference_time or datetime.now()  # Set reference time if not provided
    time_threshold = reference_time - timedelta(hours=hours_back)  # Calculate time threshold for filtering

    grouped_logs = defaultdict(list)  # Initialize a dictionary to group log messages

    for line in raw_log.splitlines():
        match = pattern.match(line)  # Match each line against the regex pattern
        if not match:
            continue  # Skip lines that do not match the pattern

        timestamp_str, level, source, message = match.groups()  # Extract components from matched line
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")  # Convert timestamp string to datetime object
        except ValueError:
            continue  # Skip lines with invalid timestamp format

        # Filter out logs that are not of the desired severity or are older than the time threshold
        if level not in SEVERITIES or timestamp < time_threshold:
            continue

        # Normalize the message by replacing specific patterns for clarity
        normalized = re.sub(r"custom integration \w+", "custom integration ...", message)
        grouped_logs[normalized].append((timestamp_str, line.strip()))  # Group logs by normalized message

    result_lines = []
    for normalized_msg, occurrences in grouped_logs.items():
        latest_entry = max(occurrences, key=lambda x: x[0])  # Get the latest log entry for each normalized message
        count = len(occurrences)  # Count occurrences of the normalized message
        if count > 1:
            result_lines.append(f"[{count}x] {latest_entry[1]}")  # Indicate multiple occurrences
        else:
            result_lines.append(latest_entry[1])  # Add single occurrence

    return "\n".join(result_lines[:max_lines])  # Return the processed log lines, limited to max_lines

# Load API key from environment variable or Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- Streamlit UI ---
st.set_page_config(page_title="Home Assistant Log Summarizer", layout="centered")
st.title("📘 Home Assistant Log Summarizer")

st.markdown("""
Upload your `home-assistant.log` file and let GPT-4 summarize warnings, errors, and important events.
""")

# --- UI inputs ---
uploaded_file = st.file_uploader("Choose a Home Assistant log file", type=["log", "txt"])

debug_mode = st.checkbox("Skip LLM query (debug mode)")
hours_back = st.slider("How many hours back to analyze?", min_value=1, max_value=168, value=24)

if uploaded_file:
    # --- File processing ---
    raw_log = uploaded_file.read().decode("utf-8", errors="ignore")  # Read and decode the uploaded log file

    reference_time = datetime.now()  # Set the current time as the reference time
    trimmed_log = preprocess_log(raw_log, max_lines=100, hours_back=hours_back, reference_time=reference_time)

    # --- Timestamp analysis ---
    log_timestamps = []  # Initialize a list to store extracted timestamps
    for line in trimmed_log.splitlines():
        match = re.match(r"\[\d+x\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line) or \
                re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line)
        if match:
            try:
                log_timestamps.append(datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f"))  # Parse valid timestamps
            except ValueError:
                pass  # Skip lines with invalid timestamp format

    if log_timestamps:
        start_time = min(log_timestamps)  # Get the earliest timestamp
        end_time = max(log_timestamps)  # Get the latest timestamp
        st.info(f"⏱️ Analyzing logs from: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("⏱️ No valid timestamps found in filtered logs.")

    if debug_mode:
        st.subheader("🧾 Filtered Log Output (Debug Mode)")
        st.code(trimmed_log, language="text")  # Display the filtered log in debug mode
        st.download_button("Download filtered log", trimmed_log, file_name="filtered_log.txt")  # Option to download filtered log
    else:
        # --- GPT processing ---
        prompt = f"""You are an expert in Home Assistant logs. Your task is to analyze the following log snippet and provide:

1. A list of actionable steps the user can take to resolve the reported errors and warnings. Refer to the specific entities or integrations involved (e.g., sensor names, platform names).
2. A brief summary of what was happening in the system.

You do not need to group similar issues — that has already been handled.

Log:
{trimmed_log}
"""
        with st.spinner("🧠 Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You help users understand Home Assistant logs clearly and concisely."},
                        {"role": "user", "content": prompt}  # Send the prompt to the GPT model
                    ],
                    temperature=0.3,
                    max_tokens=800,
                )
                summary = response.choices[0].message.content  # Extract the summary from the response
                st.subheader("📝 Summary")
                st.markdown(summary)  # Display the summary to the user
ß
            except Exception as e:
                st.error(f"Error contacting OpenAI API: {e}")
else:
    st.info("Please upload a log file to begin.")

# Optional: footer
st.markdown("---")
st.caption("Created by Boris Legradic · Powered by GPT-4 · https://github.com/borsic77/HA_log_analyzer")