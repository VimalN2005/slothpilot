"""LLM interface supporting local Ollama models and open-weight fallbacks."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional
import requests

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "llama3.2:3b")


def query_llm(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL) -> Optional[str]:
    """Queries local Ollama endpoint with fallback support."""
    # Attempt 1: Local Ollama
    try:
        url = f"{DEFAULT_OLLAMA_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser Input:\n{user_prompt}",
            "stream": False,
        }
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            return res.json().get("response")
    except Exception:
        pass

    # Attempt 2: Groq / Open-weight cloud if GROQ_API_KEY is present
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}"},
                json={
                    "model": "gemma2-9b-it",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=8,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return None


def safe_parse_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    """Safely extracts JSON from LLM markdown code blocks."""
    if not text:
        return None
    try:
        clean = text.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()
        return json.loads(clean)
    except Exception:
        return None
