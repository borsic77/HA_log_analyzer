import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import custom_components
sys.path.append(str(Path(__file__).resolve().parents[1]))
from custom_components.log_summarizer.log_utils import preprocess_log, extract_time_range, read_log_file
from custom_components.log_summarizer.gpt_client import get_openai_client, generate_prompt, call_openai_summary
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
    raw_log = uploaded_file.read().decode("utf-8")  # Read and decode the uploaded log file
    trimmed_log = preprocess_log(raw_log, max_lines=100, hours_back=hours_back)
    start_time, end_time = extract_time_range(trimmed_log)

    if start_time and end_time:
        st.info(f"⏱️ Analyzing logs from: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("⏱️ No valid timestamps found in filtered logs.")

    if debug_mode:
        st.subheader("🧾 Filtered Log Output (Debug Mode)")
        st.code(trimmed_log, language="text")  # Display the filtered log in debug mode
        st.download_button("Download filtered log", trimmed_log, file_name="filtered_log.txt")  # Option to download filtered log
    else:
        # --- GPT processing ---
        prompt = generate_prompt(trimmed_log)
        with st.spinner("🧠 Thinking..."):
            try:
                client = get_openai_client(api_key)
                response = call_openai_summary(client, "gpt-4o-mini", prompt)
                summary = response.choices[0].message.content  # Extract the summary from the response
                st.subheader("📝 Summary")
                st.markdown(summary)  # Display the summary to the user
            except Exception as e:
                st.error(f"Error contacting OpenAI API: {e}")
else:
    st.info("Please upload a log file to begin.")

# Optional: footer
st.markdown("---")
st.caption("Created by Boris Legradic · Powered by GPT-4 · https://github.com/borsic77/HA_log_analyzer")