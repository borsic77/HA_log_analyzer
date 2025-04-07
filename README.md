# 🧠 Home Assistant Log Summarizer

A proof-of-concept project that summarizes recent `home-assistant.log` entries using OpenAI’s GPT-4o-mini, either from within Home Assistant or via an optional Streamlit debug interface.

This repository includes:
- A Streamlit-based log viewer and LLM-powered summarizer in `streamlit_app/`
- A Home Assistant custom integration in `custom_components/log_summarizer/`

## Features

	•	Filters and groups warnings, errors, and critical messages
	•	Summarizes recent logs using GPT-4o-mini
	•	Provides actionable fixes with context
	•	Lets you choose a time window (e.g. last 24h)
	•	Persistent notification and optional markdown output
	•	Debug mode for viewing and exporting filtered logs



## Installing via HACS (Home Assistant Community Store)

You can also install this integration via HACS as a custom repository:

1. In Home Assistant, go to **HACS → Integrations**.
2. Click the three-dot menu in the upper right → **Custom repositories**.
3. Enter the repository URL: `https://github.com/borsic77/HA_log_analyzer`
4. Select **Integration** as the category and click **Add**.
5. You’ll now see **Log Summarizer** available to install under HACS → Integrations.
6. After installation, restart Home Assistant and follow the same configuration steps as below, starting from step 3.

This method ensures easier future updates and visibility through HACS.

---

## Installing as a Home Assistant Custom Component (ignore steps 1 and 2 if you use HACS)

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
