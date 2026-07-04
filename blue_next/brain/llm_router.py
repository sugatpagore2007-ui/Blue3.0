
import json, requests
from blue_next.config.settings import SETTINGS

def ask_ollama(prompt: str, model: str | None = None, timeout: int = 45) -> str:
    model = model or SETTINGS.llm_primary
    try:
        r = requests.post(SETTINGS.ollama_url, json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }, timeout=timeout)
        data = r.json()
        return (data.get("response") or "").strip()
    except Exception as e:
        return f"[local brain unavailable: {e}]"

def ask_gpt4o_optional(prompt: str) -> str:
    # FREE-FIRST: this adapter is intentionally disabled unless user later adds their own key.
    if not SETTINGS.use_paid_services:
        return ""
    try:
        from openai import OpenAI
        client = OpenAI()
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"[gpt optional unavailable: {e}]"

def ask_brain(prompt: str, fast: bool = False) -> str:
    system = """You are Blue, a free-first JARVIS-style desktop assistant.
Be practical, short, safe, and action-oriented. Do not claim you performed actions unless the tool did them."""
    model = SETTINGS.llm_fast if fast else SETTINGS.llm_primary
    local = ask_ollama(system + "\n\nUser: " + prompt + "\nBlue:", model=model)
    if local and not local.startswith("[local brain unavailable"):
        return local[:1200]
    fallback = ask_gpt4o_optional(prompt)
    if fallback:
        return fallback[:1200]
    return "Local brain is not running. Start Ollama and run: ollama run llama3.1:8b"
