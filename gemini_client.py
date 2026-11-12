"""Gemini API ラッパー(google-genai SDK)。"""

from collections.abc import Iterator

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-2.5-flash"
MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash-lite"]


def stream_text(
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    temperature: float = 0.8,
) -> Iterator[str]:
    """テキストを逐次生成して返す。"""
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
    )
    for chunk in client.models.generate_content_stream(
        model=model, contents=prompt, config=config
    ):
        if chunk.text:
            yield chunk.text
