# Log Summarizer

A Home Assistant custom integration that uses OpenAI’s GPT models to summarize logs and suggest actionable fixes.

## Features

- Filters and groups Home Assistant warnings and errors
- Generates concise summaries using GPT-4o-mini
- Displays results via persistent notifications or markdown files
- Optional Streamlit-based debug GUI for local testing

## Installation (via HACS)

1. Add this repository as a custom integration in HACS
2. Install it under HACS → Integrations
3. Add your OpenAI API key to `secrets.yaml` and configure in `configuration.yaml`
4. Restart Home Assistant
5. Use Developer Tools → Actions to call the `log_summarizer.summarize_logs` service

See [GitHub README](https://github.com/borsic77/ha_log_analyzer) for full setup and usage instructions.
