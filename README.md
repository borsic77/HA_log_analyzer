# 🧠 Home Assistant Log Summarizer

A proof-of-concept project that summarizes recent `home-assistant.log` entries using OpenAI’s GPT-4o-mini.

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

## Getting Started

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
