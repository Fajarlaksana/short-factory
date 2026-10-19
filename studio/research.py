"""Fact sources from Wikipedia (free, citable) so scripts stick to real numbers."""
from typing import Optional

import requests

from .log import log

HEADERS = {"User-Agent": "ViralShortsStudio/1.0 (educational shorts; contact via GitHub)"}
MAX_CHARS = 14000


def _api(lang: str, params: dict) -> dict:
    params = {"format": "json", "formatversion": 2, **params}
    r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def find_title(query: str, lang: str = "en") -> Optional[str]:
    hits = _api(lang, {"action": "query", "list": "search", "srsearch": query, "srlimit": 1})
    results = hits.get("query", {}).get("search", [])
    return results[0]["title"] if results else None


def get_article(title: str, lang: str = "en") -> Optional[dict]:
    """Return {title, url, text} for an article (plain text, trimmed), following redirects."""
    data = _api(lang, {"action": "query", "prop": "extracts|info", "explaintext": 1,
                       "redirects": 1, "inprop": "url", "titles": title})
    pages = data.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return None
    page = pages[0]
    text = page.get("extract", "")
    # Drop reference-only tail sections
    for cut in ("\n== See also ==", "\n== References ==", "\n== Lihat pula ==", "\n== Referensi =="):
        if cut in text:
            text = text.split(cut)[0]
    return {"title": page["title"], "url": page.get("fullurl", ""), "text": text[:MAX_CHARS]}


def translated_title(title: str, from_lang: str, to_lang: str) -> Optional[str]:
    data = _api(from_lang, {"action": "query", "prop": "langlinks", "lllang": to_lang,
                            "redirects": 1, "titles": title})
    pages = data.get("query", {}).get("pages", [])
    links = pages[0].get("langlinks", []) if pages else []
    return links[0]["title"] if links else None


def research(company: str, wiki_title: Optional[str] = None) -> dict:
    """Collect source text about a company. Returns {sources: [...], text: str}."""
    title = wiki_title or find_title(company, "en")
    sources = []
    if title:
        art = get_article(title, "en")
        if not art and company:
            alt = find_title(company, "en")
            art = get_article(alt, "en") if alt else None
        if art:
            sources.append(art)
            # A dedicated "business model"/"history" article often has the money details
            for extra in (f"{art['title']} business model", f"History of {art['title']}"):
                t = find_title(extra, "en")
                if t and t != art["title"] and art["title"].split()[0].lower() in t.lower():
                    extra_art = get_article(t, "en")
                    if extra_art:
                        extra_art["text"] = extra_art["text"][:6000]
                        sources.append(extra_art)
                    break
    if not sources:
        log(f"[research] no Wikipedia article found for {company!r}")
    text = "\n\n".join(f"SOURCE: {s['title']} ({s['url']})\n{s['text']}" for s in sources)
    log(f"[research] {len(sources)} source(s), {len(text)} chars")
    return {"sources": [{"title": s["title"], "url": s["url"]} for s in sources], "text": text}
