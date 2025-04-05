# 🧠 Home Assistant Log Summarizer

A proof-of-concept project that summarizes recent `home-assistant.log` entries using OpenAI’s GPT-4o-mini, either from within Home Assistant or via an optional Streamlit debug interface.

This repository includes:
- A Streamlit-based log viewer and LLM-powered summarizer in `streamlit_app/`
- A scaffold for a Home Assistant custom integration in `custom_components/log_summarizer/`

## Features

- Filters and groups warnings, errors, and critical messages
- Allows time range selection (e.g., last 24h, 48h, etc.)
- Summarizes log issues using GPT-4o-mini
- Highlights actionable fixes and affected entities
- Debug mode for viewing and exporting filtered logs
- Built with future Home Assistant integration in mind

## Installing as a Home Assistant Custom Component

1. Copy the contents of `custom_components/log_summarizer/` into your Home Assistant's `config/custom_components/log_summarizer/` directory.

2. In your `configuration.yaml`, add the following block (you can store the API key in `secrets.yaml`):

```yaml
log_summarizer:
  api_key: !secret openai_api_key
```

3. In `secrets.yaml`, add:

```yaml
openai_api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

To get your API key, create an account and generate a key at [OpenAI's API key page](https://platform.openai.com/account/api-keys).

4. Restart Home Assistant.

5. Use **Developer Tools → Actions** to call the `log_summarizer.summarize_logs` service and optionally provide the `file_path` and `model`.

---

## Optional: Run in Debug Mode with Streamlit

### 1. Clone the repository

```bash
git clone https://github.com/your-username/HA_log_analyzer.git
cd HA_log_analyzer
```

### 2. Set up the virtual environment (using `uv`)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 3. Add your OpenAI API key

Create a file called `.env` in the project root with the following contents:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Run the app

```bash
streamlit run streamlit_app/main.py
```

---

## Roadmap

- [ ] Convert to a Home Assistant custom integration with manual service trigger
- [ ] Display summaries in Lovelace
- [ ] Optional deployment via add-on or Docker

---

Created by Boris Legradic · MIT License
