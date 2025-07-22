# 🧠 Home Assistant Log Summarizer

A proof-of-concept project that summarizes recent `home-assistant.log` entries using LiteLLM. By default it queries GPT-4o-mini but you can switch to any supported model. It works from within Home Assistant or via an optional Streamlit debug interface.

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

2. In your `configuration.yaml`, add the following block (you can store the API keys in `secrets.yaml`):

```yaml
log_summarizer:
  api_keys:
    openai: !secret openai_api_key
    anthropic: !secret anthropic_api_key
```

3. In `secrets.yaml`, add:

```yaml
openai_api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
anthropic_api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

This key can be from OpenAI or any provider supported by LiteLLM. If using OpenAI, create a key at [OpenAI's API key page](https://platform.openai.com/account/api-keys).

**Note:** Accessing the OpenAI API is separate from a ChatGPT Plus subscription. Even if you have ChatGPT Plus, you'll need to create a separate OpenAI account at [platform.openai.com](https://platform.openai.com) and set up billing.

The OpenAI API uses a **pay-as-you-go prepaid model**, where you're billed per token (roughly per word). As of April 2025, the pricing is:

- **GPT-4o**: $0.005 / 1K input tokens, $0.015 / 1K output tokens
- **GPT-3.5-turbo**: $0.0005 / 1K input tokens, $0.0015 / 1K output tokens

This integration is designed to be run manually (e.g., on demand, not constantly), so usage costs are typically very low — often just a few cents per run.

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

### 3. Add your API keys

Create a file called `.env` in the project root with the following contents:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Run the app

```bash
streamlit run streamlit_app/main.py
```

---


Created by Boris Legradic · MIT License
