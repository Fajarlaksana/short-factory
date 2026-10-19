"""Stock footage: search Pixabay per beat, let a vision model score the candidates, download picks."""
import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import requests

from . import config, llm
from .log import log

PIXABAY_URL = "https://pixabay.com/api/videos/"
SEARCH_CACHE = config.CACHE_DIR / "pixabay_search.json"
USED_FILE = config.DATA_DIR / "used_footage.json"
CANDIDATES_PER_BEAT = 5
MIN_SCORE = 6


def _load_cache() -> dict:
    try:
        data = json.loads(SEARCH_CACHE.read_text(encoding="utf-8"))
        return {k: v for k, v in data.items() if time.time() - v.get("t", 0) < 24 * 3600}
    except Exception:
        return {}


def _recently_used() -> set:
    try:
        return set(json.loads(USED_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def remember_used(ids):
    """Keep the last ~400 clip ids so new videos don't reuse the same footage."""
    try:
        old = json.loads(USED_FILE.read_text(encoding="utf-8"))
    except Exception:
        old = []
    new = [i for i in dict.fromkeys(ids) if i not in old]
    USED_FILE.write_text(json.dumps((old + new)[-400:]), encoding="utf-8")


def search(query: str, cache: dict) -> List[dict]:
    """Pixabay video search (results cached 24h as the API terms require)."""
    if query in cache:
        return cache[query]["hits"]
    for attempt in range(3):
        r = requests.get(PIXABAY_URL, timeout=20, params={
            "key": os.environ.get("PIXABAY_API_KEY"), "q": query[:100], "per_page": 8,
            "safesearch": "true", "video_type": "film"})
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(10 * (attempt + 1))
            continue
        break
    if not r.ok:  # never put the URL (it contains the API key) in the error
        raise RuntimeError(f"Pixabay HTTP {r.status_code}")
    hits = []
    for h in r.json().get("hits", []):
        v = h.get("videos", {})
        large, medium = v.get("large") or {}, v.get("medium") or {}
        ref = large if large.get("url") else medium
        if not ref.get("url") or h.get("duration", 0) < 3:
            continue
        w, hgt = ref.get("width", 0), ref.get("height", 0)
        vertical = hgt > w
        # Vertical: 1080p+ is enough. Landscape gets centre-cropped, so it needs 4K to stay sharp.
        if vertical:
            pick = medium if medium.get("url") and medium.get("width", 0) >= 1080 else ref
        else:
            pick = large if large.get("url") and large.get("height", 0) >= 2000 else ref
        hits.append({
            "id": h["id"], "tags": h.get("tags", ""), "duration": h.get("duration", 0),
            "url": pick["url"], "width": pick.get("width", 0), "height": pick.get("height", 0),
            "vertical": vertical, "thumb": (medium or ref).get("thumbnail", ""),
            "popularity": h.get("downloads", 0) + 20 * h.get("likes", 0),
        })
    cache[query] = {"t": time.time(), "hits": hits}
    return hits


def search_photos(query: str, cache: dict) -> List[dict]:
    """Vertical Pixabay photos: far better coverage than video for objects (razors, receipts...).
    They get a Ken Burns move in the render so the shot still feels alive."""
    key = "photo::" + query
    if key in cache:
        return cache[key]["hits"]
    r = None
    for attempt in range(3):
        r = requests.get("https://pixabay.com/api/", timeout=20, params={
            "key": os.environ.get("PIXABAY_API_KEY"), "q": query[:100], "per_page": 6,
            "image_type": "photo", "orientation": "vertical", "safesearch": "true"})
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(10 * (attempt + 1))
            continue
        break
    if r is None or not r.ok:
        raise RuntimeError(f"Pixabay photos HTTP {r.status_code if r is not None else '?'}")
    hits = [{"id": f"p{h['id']}", "type": "photo", "tags": h.get("tags", ""), "duration": 999,
             "url": h["largeImageURL"], "width": h.get("imageWidth", 0), "height": h.get("imageHeight", 0),
             "vertical": True, "thumb": h.get("webformatURL", h.get("previewURL", "")),
             "popularity": h.get("downloads", 0) + 20 * h.get("likes", 0)}
            for h in r.json().get("hits", []) if h.get("largeImageURL")]
    cache[key] = {"t": time.time(), "hits": hits}
    return hits


def _sharpness_ok(c: dict) -> bool:
    if c.get("type") == "photo":
        return True
    # After centre-cropping to 1080x1920, landscape needs >= 1440 source height to avoid blur
    return c["width"] >= 1080 if c["vertical"] else c["height"] >= 1440


def _search_many(queries, cache) -> List[dict]:
    out, seen = [], set()
    for q in queries:
        try:
            for c in search(q, cache):
                if c["id"] not in seen:
                    seen.add(c["id"])
                    out.append({**c, "query": q})
        except Exception as e:
            log(f"[visuals] search {q!r} failed: {e}")
    return out


def gather_candidates(beats: List[dict], setting_queries: List[str] = ()) -> List[List[dict]]:
    """Candidates per beat; the company's "setting" footage is appended as a fallback pool."""
    cache = _load_cache()
    recent = _recently_used()
    setting = [c for c in _search_many(setting_queries, cache) if c["id"] not in recent and _sharpness_ok(c)]
    per_beat = []
    for b in beats:
        cands = _search_many(b["visual_queries"], cache)
        fresh = [c for c in cands if c["id"] not in recent]
        cands = fresh if len(fresh) >= 3 else cands
        sharp = [c for c in cands if _sharpness_ok(c)]
        pool = sharp if len(sharp) >= 3 else cands
        pool.sort(key=lambda c: (c["vertical"], c["popularity"]), reverse=True)
        pool = pool[:CANDIDATES_PER_BEAT]
        photos = []
        for q in b["visual_queries"][:2]:
            try:
                photos += [{**c, "query": q} for c in search_photos(q, cache)[:2] if c["id"] not in recent]
            except Exception as e:
                log(f"[visuals] photo search {q!r} failed: {e}")
        pool += list({c["id"]: c for c in photos}.values())[:3]
        ids = {c["id"] for c in pool}
        extra = [c for c in setting if c["id"] not in ids]
        random.shuffle(extra)
        per_beat.append(pool + extra[:3])
    SEARCH_CACHE.write_text(json.dumps(cache), encoding="utf-8")
    return per_beat


def _thumb(url: str) -> Optional[bytes]:
    try:
        r = requests.get(url, timeout=20)
        return r.content if r.ok and r.content[:2] == b"\xff\xd8" else None
    except Exception:
        return None


RANK_PROMPT = """You are the picture editor of a business YouTube Short about {company}.
Below are narration lines, each with numbered candidate stock-video thumbnails (the images are
attached in the same numeric order: image 1 is the first attached image, and so on).

{beats}

For EVERY image: first describe in 4-8 words what it actually shows, then score 1-10 for how well
it fits what the narrator says in its line:
10 = shows it literally, 7 = clearly the same subject, 5 = loosely related to the company's world,
2 = unrelated (flowers, random landscapes, abstract) - judge the picture, not the line.
Score 1 for: visible watermarks or large text, cartoons/clip-art, ugly or low quality frames.

Return JSON: {{"images": [{{"image": 1, "shows": "...", "score": 8}}]}}"""

_SYNONYMS = {"tyre": "tire", "tyres": "tire", "colour": "color", "centre": "center"}
_STOP = {"and", "the", "with", "for", "from", "into", "people", "person", "closeup", "close", "shot",
         "footage", "view", "modern", "busy", "aerial", "slow", "motion"}


def _words(text: str) -> set:
    out = set()
    for w in text.lower().replace(",", " ").split():
        w = _SYNONYMS.get(w, w).strip(".-'\"")
        if len(w) > 2 and w not in _STOP:
            out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def rank_with_vision(beats: List[dict], per_beat: List[List[dict]], company: str = "") -> List[dict]:
    """Return {"good": [...], "weak": [...]} per beat, best first, as judged by a vision model.

    Beats are scored in small batches and the model must describe each image first, so it
    actually looks. Clips whose Pixabay tags share no word with any query are capped at 4
    (Pixabay search is loose: "tire plant" also returns flowers).
    """
    flat = [(bi, c) for bi, cs in enumerate(per_beat) for c in cs]
    with ThreadPoolExecutor(8) as ex:
        thumbs = dict(zip([id(c) for _, c in flat], ex.map(lambda x: _thumb(x[1]["thumb"]), flat)))

    scored = [[] for _ in beats]
    batch = 3
    for b0 in range(0, len(beats), batch):
        images, index, lines = [], {}, []
        for bi in range(b0, min(b0 + batch, len(beats))):
            nums = []
            for c in per_beat[bi]:
                img = thumbs.get(id(c))
                if img:
                    images.append(img)
                    index[len(images)] = (bi, c)
                    nums.append(str(len(images)))
            lines.append(f'Line {bi + 1}: "{beats[bi]["text"]}" -> images {", ".join(nums) or "none"}')
        if not images:
            continue
        try:
            result = llm.generate(RANK_PROMPT.format(company=company or "a company", beats="\n".join(lines)),
                                  images=images, temperature=0.1, task="visual-pick")
            entries = result.get("images", []) if isinstance(result, dict) else result
        except Exception as e:
            log(f"[visuals] vision scoring failed ({str(e)[:80]}), using tag matching")
            entries = []
        seen = set()
        for e in entries:
            try:
                num, score = int(e.get("image")), float(e.get("score", 0))
            except (TypeError, ValueError, AttributeError):
                continue
            if num in index and num not in seen:
                seen.add(num)
                bi, c = index[num]
                scored[bi].append((score, c))
        for num, (bi, c) in index.items():  # unscored (model skipped / failed): tag-based guess
            if num not in seen:
                scored[bi].append((6.0 if _words(c["tags"]) & _words(c.get("query", "")) else 3.0, c))

    # Sanity check against Pixabay tags
    for bi, sc in enumerate(scored):
        query_words = set().union(*[_words(q) for q in beats[bi]["visual_queries"]], set())
        for k, (score, c) in enumerate(sc):
            if not _words(c["tags"]) & (query_words | _words(c.get("query", ""))):
                sc[k] = (min(score, 4.0), c)
    ranked = []
    for bi, sc in enumerate(scored):
        # Motion beats stills on a near-tie: videos get a small bonus when ordering
        sc.sort(key=lambda x: x[0] + (0.6 if x[1].get("type") != "photo" else 0), reverse=True)
        good = [{**c, "score": s} for s, c in sc if s >= MIN_SCORE]
        weak = [{**c, "score": s} for s, c in sc if s < MIN_SCORE]
        log(f"[visuals] beat {bi + 1}: {len(good)} good clip(s), best score {sc[0][0] if sc else 0:.0f}")
        ranked.append({"good": good, "weak": weak})
    return ranked


def rescue_empty_beats(beats: List[dict], ranked: List[dict], setting_queries: List[str],
                       company: str = "") -> List[dict]:
    """Second round for beats with no good clip: broader searches + the company's setting footage."""
    empty = [i for i, r in enumerate(ranked) if not r["good"]]
    if not empty:
        return ranked
    log(f"[visuals] second search round for beat(s) {[i + 1 for i in empty]}")
    cache, recent = _load_cache(), _recently_used()
    taken = {c["id"] for r in ranked for c in r["good"]}
    setting = [c for c in _search_many(setting_queries, cache)
               if c["id"] not in recent and c["id"] not in taken and _sharpness_ok(c)]
    sub_cands = []
    for i in empty:
        # Broader searches: the last 1-2 words of each query ("airplane on runway" -> "runway")
        broad = list(dict.fromkeys(" ".join(q.split()[-2:]) for q in beats[i]["visual_queries"]))
        found = [c for c in _search_many(broad, cache)
                 if c["id"] not in recent and c["id"] not in taken and _sharpness_ok(c)]
        for q in beats[i]["visual_queries"][:3]:
            try:
                found = [{**c, "query": q} for c in search_photos(q, cache)[:2]
                         if c["id"] not in taken and c["id"] not in recent] + found
            except Exception:
                pass
        ids = {c["id"] for c in found[:4]}
        sub_cands.append(found[:4] + [c for c in setting if c["id"] not in ids][:4])
    SEARCH_CACHE.write_text(json.dumps(cache), encoding="utf-8")
    sub = rank_with_vision([beats[i] for i in empty], sub_cands, company)
    for i, r in zip(empty, sub):
        ranked[i] = {"good": r["good"], "weak": r["weak"] + ranked[i]["weak"]}
    return ranked


def assign_shots(beats: List[dict], ranked: List[dict], timings: List[tuple]) -> List[List[dict]]:
    """Choose clips for every beat (several short shots for long beats), no clip used twice if possible.

    Preference: good clips for this beat, then good unused clips from other beats
    (often company "setting" footage), then this beat's weak matches.
    """
    used, plan = set(), []
    for bi, (start, end) in enumerate(timings):
        dur = end - start
        want = max(1, min(3, round(dur / config.MAX_SHOT_SECONDS + 0.25)))
        picks = [c for c in ranked[bi]["good"] if c["id"] not in used][:want]
        if not picks:
            # An on-topic "company world" clip (score 5) beats repeating another beat's subject
            near = [c for c in ranked[bi]["weak"] if c["id"] not in used and c.get("score", 0) >= 5]
            others = [c for r in ranked for c in r["good"] if c["id"] not in used]
            weak = [c for c in ranked[bi]["weak"] if c["id"] not in used]
            pool = (near + others + weak) or [c for r in ranked for c in r["good"] + r["weak"]]
            picks = pool[:1]
        used.update(c["id"] for c in picks)
        shot_len = dur / len(picks)
        plan.append([{"clip": c, "duration": shot_len} for c in picks])
    return plan


def download(c: dict) -> str:
    if c.get("type") == "photo":
        path = config.BROLL_CACHE / f"pixabay_{c['id']}.jpg"
    else:
        path = config.BROLL_CACHE / f"pixabay_{c['id']}_{c['height']}p.mp4"
    if path.exists() and path.stat().st_size > 10000:
        return str(path)
    tmp = path.with_suffix(".part")
    for attempt in range(5):  # Pixabay's CDN rate-limits bursts (429): back off and retry
        with requests.get(c["url"], stream=True, timeout=120) as r:
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
        tmp.replace(path)
        return str(path)
    raise RuntimeError(f"Pixabay download kept failing for clip {c['id']}")


def download_plan(plan: List[List[dict]]):
    shots = [s for beat in plan for s in beat]
    with ThreadPoolExecutor(2) as ex:
        paths = list(ex.map(lambda s: download(s["clip"]), shots))
    for s, p in zip(shots, paths):
        s["path"] = p
    log(f"[visuals] {len(shots)} shots ready")
