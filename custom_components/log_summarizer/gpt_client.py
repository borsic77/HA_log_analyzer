"""OpenAI client setup for log summarization."""

import os
from openai import OpenAI

def get_openai_client(api_key: str) -> OpenAI:
    """Return an OpenAI client configured with the given API key."""
    return OpenAI(api_key=api_key)

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

def call_openai_summary(client, model: str, prompt: str):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You explain Home Assistant logs and suggest actionable fixes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800,
    )