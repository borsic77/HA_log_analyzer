"""LLM client helpers using LiteLLM."""

from typing import Dict, List

import litellm


def get_litellm_client(provider: str, api_key: str) -> dict:
    """Return parameters used by LiteLLM for authentication."""
    return {"api_key": api_key, "custom_llm_provider": provider}


def fetch_available_models(_: Dict[str, str]) -> List[str]:
    """Return the list of supported models from LiteLLM."""
    try:
        models = litellm.get_model_list()
        if models:
            return models
    except Exception:
        pass
    return litellm.model_list


def get_provider_for_model(model: str) -> str:
    """Infer the provider for the given model using LiteLLM."""
    _, provider, _, _ = litellm.get_llm_provider(model)
    return provider

def generate_prompt(trimmed_log: str) -> str:
    return f"""You are an expert in troubleshooting Home Assistant installations. You are given a preprocessed log file that includes warnings and errors filtered for relevance.

Your job is to provide:

1. **Actionable steps** the user should take to resolve the reported errors and warnings. Include specific references to integrations, platforms, entities, or configuration sections mentioned in the log. Be direct and specific.
2. A **concise summary** (2–4 sentences) describing the overall context — what was happening, what failed, and whether it appears critical or recoverable.

Additional instructions:
- Grouping of similar messages has already been done.
- You may ignore non-actionable or informational messages.
- Output should be in clear bullet-point form where possible.
- Assume the user is technically competent but not a Home Assistant developer.

Log snippet:
{trimmed_log}
"""

def call_llm_summary(client_params: dict, model: str, prompt: str):
    """Call the selected model via LiteLLM and return the response."""
    return litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": "You explain Home Assistant logs and suggest actionable fixes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=800,
        **client_params,
    )