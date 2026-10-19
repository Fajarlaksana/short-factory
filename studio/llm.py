"""Text / vision LLM calls with model fallback. Gemini (REST) first, then Groq."""
import base64
import json
import os
import re
import time
from typing import List, Optional

import requests

from . import config
from .log import log

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Models that failed permanently (404 / zero quota) during this run
_dead = set()
# Models rate-limited during this run -> skip until this timestamp
_cooldown = {}


class LLMError(RuntimeError):
    pass


def parse_json(text: str):
    """Pull a JSON object/array out of a model reply (handles fences and preambles)."""
    if not text:
        raise ValueError("empty reply")
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    for block in reversed(re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)):
        try:
            return json.loads(block.strip())
        except Exception:
            continue
    decoder = json.JSONDecoder()
    last = None
    pos = min([p for p in (text.find("{"), text.find("[")) if p != -1], default=-1)
    while pos != -1 and pos < len(text):
        try:
            obj, end = decoder.raw_decode(text, pos)
            last = obj
            nxt = [p for p in (text.find("{", end), text.find("[", end)) if p != -1]
            pos = min(nxt) if nxt else -1
        except Exception:
            nxt = [p for p in (text.find("{", pos + 1), text.find("[", pos + 1)) if p != -1]
            pos = min(nxt) if nxt else -1
    if last is None:
        raise ValueError("no JSON found in reply")
    return last


def _available(model: str) -> bool:
    return model not in _dead and _cooldown.get(model, 0) <= time.time()


def _note_failure(model: str, status: int, body: str):
    low = body.lower()
    if status == 404 or "limit: 0" in low or "no longer available" in low:
        _dead.add(model)
    elif status in (429, 503, 500):
        _cooldown[model] = time.time() + (60 if status == 429 else 20)


def _gemini(model: str, parts: list, json_mode: bool, temperature: float, max_tokens: int) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY not set")
    gen = {"temperature": temperature, "maxOutputTokens": max_tokens}
    if json_mode:
        gen["responseMimeType"] = "application/json"
    r = requests.post(GEMINI_URL.format(model), params={"key": key}, timeout=120,
                      json={"contents": [{"parts": parts}], "generationConfig": gen})
    if not r.ok:
        _note_failure(model, r.status_code, r.text)
        raise LLMError(f"{model}: HTTP {r.status_code} {r.text[:120]}")
    cand = (r.json().get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    if not text.strip():
        raise LLMError(f"{model}: empty reply ({cand.get('finishReason')})")
    return text


def _groq(model: str, prompt: str, json_mode: bool, temperature: float, max_tokens: int) -> str:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise LLMError("GROQ_API_KEY not set")
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": max_tokens}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
    if not r.ok:
        _note_failure(model, r.status_code, r.text)
        raise LLMError(f"{model}: HTTP {r.status_code} {r.text[:120]}")
    text = r.json()["choices"][0]["message"].get("content") or ""
    if not text.strip():
        raise LLMError(f"{model}: empty reply")
    return text


def generate(prompt: str, *, json_mode: bool = True, images: Optional[List[bytes]] = None,
             temperature: float = 0.7, max_tokens: int = 8192, task: str = "llm",
             strong: bool = False):
    """Run a prompt through the model chain. Returns parsed JSON when json_mode, else text.

    images: optional list of JPEG bytes (vision; Gemini only).
    strong: writing tasks - try the strongest models (incl. Groq) before the "lite" ones.
    """
    parts = [{"text": prompt}]
    for img in images or []:
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(img).decode()}})

    errors = []
    for attempt in range(2):
        chain = [("gemini", m) for m in config.GEMINI_TEXT_MODELS]
        if not images:
            chain += [("groq", m) for m in config.GROQ_TEXT_MODELS]
        if strong and not images:
            top = [c for c in chain if c[1] in config.STRONG_MODELS]
            top.sort(key=lambda c: config.STRONG_MODELS.index(c[1]))
            chain = top + [c for c in chain if c not in top]
        for provider, model in chain:
            if not _available(model):
                continue
            try:
                if provider == "gemini":
                    text = _gemini(model, parts, json_mode, temperature, max_tokens)
                else:
                    text = _groq(model, prompt, json_mode, temperature, max_tokens)
                result = parse_json(text) if json_mode else text.strip()
                log(f"[{task}] {model} ok")
                return result
            except (LLMError, ValueError, requests.RequestException) as e:
                errors.append(str(e)[:160])
                log(f"[{task}] {model} failed: {str(e)[:110]}")
        if attempt == 0:
            # Everything rate-limited at once: wait out the shortest cooldown and retry once
            waits = [t - time.time() for m, t in _cooldown.items() if m not in _dead]
            wait = max(5, min(waits)) if waits else 0
            if not waits or wait > 90:
                break
            log(f"[{task}] all models busy, waiting {wait:.0f}s")
            time.sleep(wait)
    raise LLMError(f"[{task}] all models failed: " + " | ".join(errors[-4:]))
