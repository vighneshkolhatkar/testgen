from __future__ import annotations

import os
from typing import Iterator

import anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-sonnet-4-6"
FAST_MODEL = "claude-haiku-4-5-20251001"


def stream_tests(
    system_prompt: str,
    user_prompt: str,
    fast: bool = False,
) -> Iterator[str]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is missing. Set it in your environment or .env file."
        )

    client = anthropic.Anthropic(api_key=api_key)
    model = FAST_MODEL if fast else DEFAULT_MODEL

    try:
        with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text
    except anthropic.AuthenticationError:
        raise ValueError(
            "ANTHROPIC_API_KEY is missing or invalid. Set it in your environment or .env file."
        )
    except anthropic.RateLimitError:
        raise ValueError("Rate limit hit. Wait a moment and retry.")
