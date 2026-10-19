"""Pick the next business case study, avoiding companies already covered."""
import json
import random
from datetime import date
from typing import Optional

from . import config, llm
from .log import log


def load_history() -> list:
    try:
        return json.loads(config.HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(entry: dict):
    history = load_history()
    history.append({**entry, "date": date.today().isoformat()})
    config.HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


TOPIC_PROMPT = """You plan a YouTube Shorts channel of business case studies
("how company X really makes money", "the hidden business model behind X",
"why X is so cheap", "how X went from zero to billions", "why X failed").
Audience: curious viewers in the US and Indonesia, age 18-35.

Propose {n} video ideas. Rules:
- Real, well-known companies or brands (global ones Indonesians also know are great:
  e.g. tech, food chains, retail, games, airlines, sports, Indonesian unicorns).
- Each idea needs ONE sharp, surprising angle with a concrete money mechanism
  (not "the history of X"). The angle must be checkable on Wikipedia.
- Do NOT use any of these already-covered companies: {used}
{hint}
Return JSON: {{"ideas": [{{
  "company": "...",
  "wikipedia_title": "exact English Wikipedia article title",
  "angle": "one sentence: the surprising money mechanism",
  "working_title": "punchy title under 60 chars",
  "curiosity": 1-10
}}]}}"""


def pick_topic(hint: Optional[str] = None) -> dict:
    """Return {company, wikipedia_title, angle, working_title}."""
    history = load_history()
    used = sorted({h["company"].lower() for h in history if h.get("company")})
    if hint:
        # The user chose the subject: every idea is a different angle on it, history doesn't apply
        hint_line = (f"- IMPORTANT: every idea must be about exactly this subject: {hint}. "
                     "Give different angles on it.")
        used = []
    else:
        hint_line = ""
    result = llm.generate(TOPIC_PROMPT.format(n=5 if hint else 10, used=", ".join(used) or "none",
                                              hint=hint_line),
                          temperature=1.0, task="topic")
    ideas = result.get("ideas", []) if isinstance(result, dict) else result
    ideas = [i for i in ideas if i.get("company") and i["company"].lower() not in used]
    if hint:
        words = [w for w in hint.lower().split() if len(w) > 2]
        matching = [i for i in ideas if any(w in (i["company"] + " " + i.get("wikipedia_title", "")).lower()
                                            for w in words)]
        if matching:
            ideas = matching
        else:
            log(f"[topic] no idea matched {hint!r}; using the hint as the company")
            ideas = [{"company": hint, "wikipedia_title": None, "angle": f"how {hint} really makes money",
                      "working_title": f"How {hint} Really Makes Money", "curiosity": 5}]
    if not ideas:
        raise llm.LLMError("topic: no usable ideas returned")
    ideas.sort(key=lambda i: float(i.get("curiosity", 0) or 0), reverse=True)
    # Some variety among the top ideas
    pick = random.choice(ideas[:3]) if not hint else ideas[0]
    log(f"[topic] {pick['company']}: {pick.get('angle', '')}")
    return pick
