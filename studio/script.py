"""Write the narration: English draft -> fact-check/polish -> natural Indonesian adaptation."""
import re

from . import config, llm
from .log import log

SCRIPT_SCHEMA = """{
  "title": "YouTube title, max 60 chars, curiosity-driven, no clickbait lies",
  "banner": "small label shown at the top of the video, max 24 chars, e.g. COSTCO'S HOT DOG TRICK",
  "hook_title": "big opening headline shown in the first 3 seconds, 3-6 words, wrap the ONE key word in *stars*, e.g. 'They LOSE money on *hot dogs*'",
  "thumb_text": "thumbnail text, 2-4 punchy words, ONE key word in *stars*, e.g. 'TIRES SOLD *DINNER*' or '$1.50 *FOREVER*?'",
  "thumb_badge": "short sticker for the thumbnail, max 14 chars: a striking number or fact, e.g. '$26 BILLION' or 'SINCE 1985'",
  "hook": "copy of beat 1 text",
  "beats": [
    {"text": "1-2 short spoken sentences",
     "visual_queries": ["3 different 2-4 word English stock-footage searches showing this beat literally"]}
  ],
  "setting_queries": ["5 stock-footage searches showing this company's world: its kind of stores,
     products, customers, staff at work (e.g. 'fast food restaurant counter', 'drive thru window')"],
  "description": "2-3 sentence YouTube description",
  "hashtags": ["#shorts", "...4-6 more"],
  "music_mood": "one of: documentary, corporate, tension, upbeat, lofi",
  "facts_used": ["each number/claim used, with the source sentence it came from"]
}"""

WRITE_PROMPT = """You are a top YouTube Shorts scriptwriter for a business channel
(style: Wall Street Millennial, Business Casual, Logically Answered - but 50 seconds).

Topic: {company} - {angle}

SOURCE MATERIAL (the ONLY facts you may use; never invent numbers):
<<<
{source}
>>>

Write a {lo}-{hi} word narration split into {b_lo}-{b_hi} beats (about 15-18 words per beat).
Count the words before answering - under {lo} words is a failure.

This is ONE story that answers ONE question, not a list of facts.
Structure:
1. HOOK (beat 1, under 14 words): a specific, surprising contradiction about the money,
   with a concrete detail (a price, a number, an object). It opens a question in the viewer's head.
   No "Did you know", no "In this video", no greetings, no vague "secret".
2. Setup (1 beat): what the viewer assumes, and why that assumption is wrong.
3. Reveal (3-4 beats): the real money mechanism as a chain of cause and effect
   ("because... so... which means..."). Use 2-3 numbers from the source that PROVE the mechanism.
4. Click (1 beat): the consequence or twist that makes the whole thing make sense.
5. Payoff (1 beat): answer the hook's question directly, calling back to its concrete detail.
   Then exactly this CTA as the last sentence: "{cta}"

Hard rules:
- Every beat must push toward answering the hook. Delete any fact that doesn't explain the money
  (rankings, store counts, founding dates, "largest company" trivia) unless it is the mechanism.
- If the hook names a detail (e.g. a price), the script must say that detail and explain it.
- Never say "exactly" with a number, never claim things about the future.
Style: spoken, punchy, short sentences, second person ("you"), concrete nouns, no jargon,
no filler words, no emojis. Write numbers as digits ("19 billion", "$4.5 billion", "1972").
Every claim must come from the source: do not invent causes, uses or stories the source doesn't state.
Visual queries: concrete SCENES a stock-video site has, with people or objects doing something,
set in this company's world (e.g. "burger on restaurant tray", "drive thru window", "warehouse
shelves forklift", "cashier credit card payment", "business people signing contract").
Never abstract words alone ("land", "profit", "growth", "strategy", "success") - those return
random nature footage. No brand names or logos (stock sites don't have them). Use simple American English
("tire" not "tyre"), 2-3 common words, and avoid words with a second meaning
("plant" = flowers, "family" = flowers, "star" = sky, "guide" = random,
"blade" = helicopters/fences - say "razor" or "shaving" instead).

Return JSON only, in this shape:
{schema}"""

POLISH_PROMPT = """You are the fact-checker and editor for this Shorts script.

SOURCE MATERIAL:
<<<
{source}
>>>

SCRIPT (JSON):
{script}

Do all of this and return the corrected script in the same JSON shape:
1. Every number or factual claim must be supported by the source. Fix or remove anything that is not.
   Rounding is fine ("about 4.5 billion").
2. The hook must create a curiosity gap that the payoff closes, calling back to the hook's
   concrete detail. Sharpen it if weak.
3. It must read as one cause-and-effect story. Replace trivia beats (rankings, store counts,
   dates) with beats that explain the money mechanism, using the source.
4. Keep total narration {lo}-{hi} words and {b_lo}-{b_hi} beats; cut filler, not substance.
5. Every sentence must sound natural read aloud by a narrator.
6. Keep the final CTA sentence exactly: "{cta}"
7. Keep 3 visual_queries per beat, concrete and literal."""

ADAPT_PROMPT = """Adapt this English YouTube Shorts script for an Indonesian audience.

SCRIPT (JSON):
{script}

Rules:
- Natural spoken Bahasa Indonesia like a popular Indonesian business YouTuber: casual-smart,
  "kamu" not "Anda", short sentences. Not a literal translation.
- Same number of beats, same meaning and facts per beat. Keep numbers accurate; say money
  in dollars ("sekitar 4 miliar dolar") and you may add a rupiah comparison only if exact.
- Common English business terms Indonesians use are fine (membership, profit, margin).
- Keep "visual_queries" in English, unchanged.
- Translate title, banner (max 24 chars), hook_title and thumb_text as natural punchy Indonesian
  (not word-for-word; keep the *stars* around the
  key word, keep them short), thumb_badge (max 14 chars, never "€8 EURO"), description; hashtags: mix Indonesian and English, include #shorts.
- The last sentence of the last beat must be exactly: "{cta}"
- "facts_used" can stay in English.
Return JSON only in the same shape."""


PROOFREAD_ID_PROMPT = """Kamu editor naskah YouTube Shorts berbahasa Indonesia untuk channel bisnis.
Periksa naskah ini (JSON) baris per baris:

{script}

Perbaiki:
- Kata yang salah arti atau salah pakai (contoh: "franchisor" vs "franchisee/mitra waralaba",
  "ngelewatin" padahal maksudnya "ngejalanin"). Istilah bisnis harus tepat.
- Kalimat kaku hasil terjemahan; buat terdengar seperti YouTuber bisnis Indonesia yang cerdas
  dan santai ("kamu", kalimat pendek), tapi jangan lebay atau terlalu banyak slang.
- Angka harus sama persis dengan versi aslinya.
- Jumlah beat dan urutan tetap sama; "visual_queries" jangan diubah.
- Teks layar (banner, hook_title, thumb_text, thumb_badge) harus pendek, nendang, tanpa salah ketik;
  pertahankan tanda *bintang* di sekitar kata kunci.
- Kalimat terakhir tetap persis: "{cta}"
Kembalikan JSON dengan bentuk yang sama."""


def _word_count(script: dict) -> int:
    return sum(len(b.get("text", "").split()) for b in script.get("beats", []))


def _validate(script: dict, label: str) -> dict:
    if isinstance(script, list):  # some models answer with a bare array
        if len(script) == 1 and isinstance(script[0], dict) and "beats" in script[0]:
            script = script[0]
        else:
            script = {"beats": script}
    beats = [b for b in script.get("beats", []) if isinstance(b, dict) and str(b.get("text", "")).strip()]
    if len(beats) < 4:
        raise llm.LLMError(f"{label}: only {len(beats)} beats")
    for b in beats:
        q = [s for s in b.get("visual_queries", []) if isinstance(s, str) and s.strip()]
        b["visual_queries"] = q[:3] or ["business city skyline"]
    script["beats"] = beats
    script["hook"] = beats[0]["text"]
    # *stars* only mark key words in on-screen text; never in the YouTube title/description
    script["title"] = re.sub(r"\s{2,}", " ", script.get("title", "").replace("*", "")).strip()
    script["description"] = script.get("description", "").replace("*", "")
    banner = (script.get("banner") or script.get("title", "")).strip().replace("*", "")
    script["banner"] = banner if len(banner) <= 30 else banner[:30].rsplit(" ", 1)[0]
    script["hook_title"] = (script.get("hook_title") or script["banner"]).strip()
    script["thumb_text"] = (script.get("thumb_text") or script["hook_title"]).strip()
    script["thumb_badge"] = (script.get("thumb_badge") or "").strip()[:16]
    script["emoji"] = (script.get("emoji") or "").strip()[:4]
    script["thumb_template"] = script.get("thumb_template") if script.get("thumb_template") in ("claim", "split") else "claim"
    for key in ("split_top", "split_bottom", "thumb_focus"):
        script[key] = (script.get(key) or "").strip()
    if script["thumb_template"] == "split" and not (script["split_top"] and script["split_bottom"]):
        script["thumb_template"] = "claim"
    for key in ("banner", "hook_title", "thumb_text", "thumb_badge", "split_top", "split_bottom"):
        script[key] = tidy_screen_text(script[key])
    for key in ("banner", "thumb_badge", "split_top", "split_bottom"):  # no key-word marks here
        script[key] = script[key].replace("*", "").strip()
    if not re.search(r"\d", script["thumb_badge"]):  # a sticker must carry a number, else none
        script["thumb_badge"] = ""
    script["setting_queries"] = [q for q in script.get("setting_queries", [])
                                 if isinstance(q, str) and q.strip()][:5]
    if "#shorts" not in [h.lower() for h in script.get("hashtags", [])]:
        script.setdefault("hashtags", []).insert(0, "#shorts")
    log(f"[script:{label}] {len(beats)} beats, {_word_count(script)} words")
    return script


EXPAND_PROMPT = """This Shorts script is too short: {words} words, it must be {lo}-{hi} words
(about 50 seconds of narration). Expand it using MORE concrete facts and numbers from the source,
not filler. Keep the hook, keep {b_lo}-{b_hi} beats (about 15-18 words each), keep the final CTA
sentence exactly: "{cta}". Every beat keeps 3 visual_queries.

SOURCE MATERIAL:
<<<
{source}
>>>

SCRIPT (JSON):
{script}

Return the expanded script as JSON in the same shape."""


def _ensure_length(s: dict, fmt: dict, label: str) -> dict:
    import json
    for _ in range(2):
        words = _word_count(s)
        if words >= fmt["lo"] - 8:
            break
        log(f"[script:{label}] {words} words is too short, expanding")
        s = _validate(llm.generate(EXPAND_PROMPT.format(words=words, script=json.dumps(s, ensure_ascii=False),
                                                        **fmt), temperature=0.6, task="expand", strong=True), label)
    return s


ANGLE_PROMPT = """You plan a fact-based business Short about {company}.
Proposed angle: "{angle}"

SOURCE MATERIAL (the only allowed facts):
<<<
{source}
>>>

Is the proposed angle's CORE claim explicitly supported by the source? Be strict: a claim that
"sounds plausible" or is common knowledge but is not written in the source is NOT supported.
If it is not supported, propose the most surprising money/business angle that IS supported by
the source (a contradiction, an unexpected revenue source, a weird origin, a big number).

Return JSON: {{"supported": true/false, "angle": "the angle to use (one sentence)",
"evidence": "the exact source sentence(s) that support it"}}"""

AUDIT_PROMPT = """Audit this YouTube Short script against its source, claim by claim.

SOURCE MATERIAL:
<<<
{source}
>>>

SCRIPT BEATS:
{beats}

List every factual claim in the script (who/what/when/how much/causes/effects) that is NOT
supported by the source. Opinions, rhetorical questions and the call-to-action are fine.
A cause-and-effect story the source does not state ("so people use it as money") is unsupported.

Return JSON: {{"unsupported": [{{"beat": 1, "claim": "...", "why": "..."}}]}}"""

FIX_PROMPT = """Rewrite this Short script so that EVERY claim is supported by the source.
Unsupported claims found by the fact-checker:
{problems}

SOURCE MATERIAL:
<<<
{source}
>>>

SCRIPT (JSON):
{script}

Replace each unsupported claim with a true, surprising fact from the source (keep the story
gripping: hook -> reveal -> payoff). If the hook itself was unsupported, write a new hook from a
supported surprising fact. Keep {lo}-{hi} words, {b_lo}-{b_hi} beats, 3 visual_queries per beat,
numbers as digits, and the final CTA sentence exactly: "{cta}".
Return the full script JSON in the same shape."""


def ground_angle(topic: dict, source_text: str) -> dict:
    """Make sure the story's core claim is in the source before writing anything."""
    try:
        r = llm.generate(ANGLE_PROMPT.format(company=topic["company"], angle=topic.get("angle", ""),
                                             source=source_text[:12000]),
                         temperature=0.3, task="angle-check", strong=True)
    except llm.LLMError as e:
        log(f"[angle] check skipped: {e}")
        return topic
    if isinstance(r, dict) and r.get("angle"):
        if not r.get("supported"):
            log(f"[angle] unsupported angle replaced -> {r['angle']}")
        topic = {**topic, "angle": r["angle"], "evidence": r.get("evidence", "")}
    return topic


def audit_claims(script: dict, source_text: str) -> list:
    beats = "\n".join(f"{i + 1}. {b['text']}" for i, b in enumerate(script["beats"]))
    r = llm.generate(AUDIT_PROMPT.format(source=source_text, beats=beats),
                     temperature=0.0, task="claim-audit", strong=True)
    items = r.get("unsupported", []) if isinstance(r, dict) else []
    return [x for x in items if isinstance(x, dict) and x.get("claim")]


def enforce_facts(script: dict, fmt: dict) -> dict:
    """Audit every claim; rewrite until clean. Refuse to continue with an unsupported story."""
    import json
    for attempt in range(2):
        problems = audit_claims(script, fmt["source"])
        if not problems:
            log("[audit] all claims supported by the source")
            return script
        log(f"[audit] {len(problems)} unsupported claim(s): " + "; ".join(p["claim"][:60] for p in problems[:3]))
        fixed = llm.generate(FIX_PROMPT.format(problems=json.dumps(problems, ensure_ascii=False, indent=1),
                                               script=json.dumps(script, ensure_ascii=False), **fmt),
                             temperature=0.4, task="fact-fix", strong=True)
        script = _ensure_length(_validate(fixed, "en"), fmt, "en")
    problems = audit_claims(script, fmt["source"])
    if problems:
        raise llm.LLMError("script still has unsupported claims after 2 fixes: "
                           + "; ".join(p["claim"][:80] for p in problems[:3]))
    log("[audit] all claims supported by the source")
    return script


def write_english(topic: dict, source_text: str) -> dict:
    fmt = dict(company=topic["company"], angle=topic.get("angle", ""), source=source_text,
               lo=config.TARGET_WORDS[0], hi=config.TARGET_WORDS[1],
               b_lo=config.BEATS[0], b_hi=config.BEATS[1],
               cta=config.LANGUAGES["en"]["cta"], schema=SCRIPT_SCHEMA)
    draft = _validate(llm.generate(WRITE_PROMPT.format(**fmt), temperature=0.85, task="script", strong=True), "en-draft")
    import json
    draft = _ensure_length(draft, fmt, "en-draft")
    polished = llm.generate(POLISH_PROMPT.format(script=json.dumps(draft, ensure_ascii=False), **fmt),
                            temperature=0.4, task="factcheck", strong=True)
    final = _ensure_length(_validate(polished, "en"), fmt, "en")
    final = enforce_facts(final, fmt)
    # Lighter models sometimes drop or "improve" fields while editing: keep the draft's footage plan
    for key in ("setting_queries", "hook_title", "thumb_text", "thumb_badge", "banner"):
        if not final.get(key) and draft.get(key):
            final[key] = draft[key]
    return design_screens(clean_queries(package(final, "en"), topic["company"]), "en")


PACKAGING_FIELDS = ("title", "hook_title", "banner", "thumb_text", "thumb_badge", "emoji",
                    "thumb_template", "split_top", "split_bottom", "thumb_focus")

PACKAGING_STYLE = {
    "en": """Language: English. Audience: US/global viewers 18-35 scrolling Shorts.
Proven title formulas (adapt, don't copy):
- Contradiction: "Ryanair Sells €70 Seats... But Makes Its Money Elsewhere"
- Hidden villain/trick: "The Sneaky Trick Behind Costco's $1.50 Hot Dog"
- Number shock: "€70 Ticket, Only €8 Profit?!"
- You-angle: "You're Not Ryanair's Customer. You're the Product"
- Ternyata/realization: "McDonald's Isn't a Burger Company"
Hook/thumbnail words that work: SECRET, TRICK, TRAP, SCAM?, BAIT, LIE, REAL, HIDDEN, NOBODY, ONLY.""",
    "id": """Bahasa: Indonesia (gaya channel explainer Indonesia seperti "Ngomongin Uang": santai,
pakai "kamu", informatif tapi bikin penasaran).
Formula judul yang terbukti di channel itu (adaptasi, jangan disalin):
- "Wah, Bos AI Malah Minta Pengembangan AI Direm, Ada Apa?"
- "Orang Aneh Asuransikan Gedung WTC Sebelum Gedungnya Hancur"
- "Dari Pengangguran sampai Wisatawan, Malaysia Kok Bisa Kelihatan Lebih Unggul?"
- "Ternyata Skema Perampasan Aset Koruptor Sudah Ada di Regulasi Kita"
- "Ada Apa Di Balik ... Yang Tidak Kunjung ...?"
Pola: pembuka emosional (Wah, / Ternyata / Kok Bisa / Ada Apa Di Balik / Pantesan) + fakta spesifik
+ pertanyaan atau kontras. Semua teks layar dalam Bahasa Indonesia yang natural.""",
}

PACKAGING_PROMPT = """You are a top YouTube Shorts packaging expert (titles + thumbnails),
known for very high click-through rates. Clickbait style is wanted, but it must be TRUE to the
video (a title the video doesn't pay off gets punished by YouTube).

{style}

Video narration:
{narration}

What makes people click: a CONTRADICTION or SURPRISE ("cheap but rich", "loses money but wins",
"not what you think"), a SPECIFIC detail (number, price, name), and an open QUESTION the video
answers. Descriptive titles ("How X Built Y", "Cara X Kuasai Dunia", "The History of X") are boring.

Write candidates:
- title: 10 candidates, max 65 chars, each with a contradiction/surprise + specific detail,
  may end with "?!" or "...". Capitalize Like A Title.
- hook_title: 5 candidates, 4-9 words, shown big in the first seconds: setup words then the
  payoff in *stars* AT THE END, e.g. "GYM INI UNTUNG KALAU *KAMU BOLOS*", "€70 TICKET, *€8 PROFIT?*".
- thumb_text: 6 candidates, an informative news-style headline of 6-12 words: setup words
  first (shown white), then the payoff of 2-5 words in *stars* AT THE END (shown BIG yellow).
  e.g. "6 HAL INI BIKIN MALAYSIA KELIHATAN *LEBIH MAJU DARI INDONESIA*",
  "TIKET RYANAIR CUMA €70 TAPI *UNTUNGNYA DARI SINI*", "PLANET FITNESS UNTUNG BESAR *KARENA KAMU MALAS*".
  It must make the topic instantly clear AND open a curiosity gap. Not identical to the title.
- thumb_badge: 4 candidates, max 14 chars, a striking number, e.g. "€8 PROFIT", "SINCE 1985".
- banner: 3 candidates, max 22 chars, short topic label.
- emoji: 3 candidates, ONE emoji each that fits the emotion (😱 🤯 💸 🔥 🤑 😳 🚨 💰 ...).
- thumb_focus: the one physical object the thumbnail picture should show (e.g. "airplane",
  "instant noodles", "tire"), 1-2 words, English.
Use only numbers that appear in the narration.

Return JSON: {{"candidates": {{"title": [...], "hook_title": [...], "thumb_text": [...],
"thumb_badge": [...], "banner": [...], "emoji": [...]}}, "thumb_focus": "..."}}"""

JUDGE_PROMPT = """You are a strict judge of YouTube Shorts packaging by predicted click-through rate.
{style}

Video narration (the packaging must be true to it):
{narration}

Candidates:
{candidates}

Pick the single best candidate per field (you may sharpen it: shorter, punchier, fix grammar,
keep it true). Rubric for ctr_score of the chosen title + thumb_text together:
 9-10: clear contradiction/surprise + specific number/name + emotion, instantly understood
 7-8 : intriguing and specific but missing one of those
 4-6 : descriptive/informative only ("How Indomie Built a Global Noodle Empire",
       "Cara Indomie Kuasai Dunia", "19 Billion Packs") - no reason to click NOW
 1-3 : vague, misleading or ungrammatical
Be honest: most candidates are 5-7. Never give 8+ to a descriptive title.
No claim stronger than the narration: no invented "all/every/always/never", no exaggerated
scope (e.g. "conquered ALL of Africa" when the narration says "largest factory in Africa").
Check the spelling of every word (e.g. Indonesian "miliar", not "milar").
thumb_badge must contain a number; otherwise leave it empty.
The title and thumb_text must work together without repeating each other.
hook_title and thumb_text: setup words first, then exactly one *starred* payoff (2-5 words)
AT THE END. thumb_text must have 6-12 words.

Return JSON: {{"title": "...", "hook_title": "...", "thumb_text": "...", "thumb_badge": "...",
"banner": "...", "emoji": "...", "ctr_score": 1-10, "why": "one sentence"}}"""


def _numbers_in(text: str) -> set:
    return {re.sub(r"[^\d.]", "", n).rstrip(".") for n in _NUM.findall(text or "")} - {""}


_BORING = re.compile(r"^(how|the history|cara|sejarah|inilah|this is)\b", re.I)
_HOOKY = re.compile(r"[?!]|\b(but|yet|secret|trick|trap|actually|really|why|tapi|ternyata|"
                    r"pantesan|kok|wah|rahasia|trik|jebakan|licik|cuma|malah|padahal|ada apa)\b", re.I)


def _packaging_sanity(b: dict) -> float:
    """Cap the judge's score when the text breaks the rules it is supposed to enforce."""
    cap = 10.0
    title, thumb = str(b.get("title", "")), str(b.get("thumb_text", ""))
    if _BORING.search(title) and not _HOOKY.search(title):
        cap = min(cap, 5)
    if not _HOOKY.search(title):
        cap = min(cap, 7)
    words = thumb.replace("*", " ").split()
    if len(words) < 5 or "*" not in thumb or not thumb.rstrip(" ?!.").endswith("*"):
        cap = min(cap, 6)  # thumbnail headline too short or payoff not at the end
    return cap


def package(script: dict, lang: str = "en") -> dict:
    """Clickbait-but-true packaging: generate many candidates, then a judge picks the best."""
    import json
    narration = " ".join(b["text"] for b in script["beats"])
    style = PACKAGING_STYLE[lang]
    try:
        best, gen = None, {}
        for round_ in range(2):  # a second round only if the judge isn't convinced (score < 8)
            g = llm.generate(PACKAGING_PROMPT.format(style=style, narration=narration),
                             temperature=1.0, task=f"packaging-{lang}", strong=True)
            cands = g.get("candidates", {}) if isinstance(g, dict) else {}
            b = llm.generate(JUDGE_PROMPT.format(style=style, narration=narration,
                                                 candidates=json.dumps(cands, ensure_ascii=False, indent=1)),
                             temperature=0.2, task=f"ctr-judge-{lang}", strong=True)
            score = float(b.get("ctr_score", 0) or 0) if isinstance(b, dict) else 0
            score = min(score, _packaging_sanity(b) if isinstance(b, dict) else 0)
            log(f"[packaging:{lang}] round {round_ + 1}: CTR score {score:g}")
            if best is None or score > float(best.get("ctr_score", 0) or 0):
                best, gen = b, g
            if score >= 8:
                break
        allowed = _numbers_in(narration)
        for key in ("title", "hook_title", "thumb_text", "thumb_badge", "banner", "emoji",
                    "thumb_template", "split_top", "split_bottom"):
            value = best.get(key) if isinstance(best, dict) else None
            if not (isinstance(value, str) and value.strip()):
                continue
            if _numbers_in(value) - allowed:  # invented number: keep the previous text
                log(f"[packaging] rejected {key} {value!r}: number not in the narration")
                continue
            script[key] = value.strip()
        for key in ("thumb_focus",):
            value = gen.get(key) if isinstance(gen, dict) else None
            if isinstance(value, str) and value.strip() and not (_numbers_in(value) - allowed):
                script[key] = value.strip()
        thumb = script.get("thumb_text", "")
        if len(thumb.replace("*", " ").split()) < 5 and len(script.get("hook_title", "").split()) >= 5:
            script["thumb_text"] = script["hook_title"]  # a fuller headline reads better
        log(f"[packaging:{lang}] {script.get('title')} | hook: {script.get('hook_title')} | "
            f"thumb[{script.get('thumb_template', 'claim')}]: {script.get('thumb_text')} "
            f"+ {script.get('thumb_badge')} {script.get('emoji', '')}")
    except llm.LLMError as e:
        log(f"[packaging:{lang}] skipped: {e}")
    return _validate(script, lang)


SCREENS_PROMPT = """You are the motion designer of a {lang_name} YouTube Shorts explainer channel
(style: Indonesian news explainers like "Ngomongin Uang": short kinetic text that builds up word by
word at the top of the screen, key phrase big in yellow, plus number tags, name lower-thirds,
count-up stats and speech bubbles).

Narration beats:
{beats}

Design ONE on-screen graphic per beat (same order, exactly {n} items). Types:
- "headline": 1-3 short lines summarising the beat. The LAST line is the emphasis (shown big,
  yellow): mark it with *stars*. Use the narrator's own words so the text syncs with the voice.
  Max 9 words total, emphasis 1-4 words. e.g. ["DIBIAYAI PINJAMAN", "*BANK BUMN*"]
- "stat": a number from this beat counting up: value (number), prefix ("$", "€", "Rp"),
  suffix (" MILIAR", "B", "%"), caption (2-5 words). Use ONLY when the beat states that number.
- "number": a list step: number ("1", "2"...) and label (1-3 words). Use for list-like beats.
- "name": lower-third introducing a person or company: name and role (2-5 words each).
- "bubble": a witty/surprised aside comment (4-9 words) said by a cartoon emoji character,
  with emoji (one of 😱 🤯 😳 🤔 🧐 😤 🤑 😏 🙄 😬). Great for twists and "wait, what?" moments.
- "quote": a short quote (max 14 words) with speaker, only if the narration quotes someone.
Rules: the first beat is the hook: type "headline", 2-3 lines, strong. Use variety: include at
least one "stat" if the narration has numbers, one "bubble" for the twist, and not more than 3
"headline" in a row. All text in {lang_name}, ALL CAPS except bubble/quote text.
Numbers must match the narration exactly.

Return JSON: {{"screens": [{{"type": "headline", "lines": ["...", "*...*"]}},
{{"type": "stat", "value": 4.5, "prefix": "$", "suffix": "B", "caption": "..."}},
{{"type": "number", "number": "1", "label": "..."}}, {{"type": "name", "name": "...", "role": "..."}},
{{"type": "bubble", "text": "...", "emoji": "😱"}}, {{"type": "quote", "text": "...", "speaker": "..."}}]}}"""


def _fallback_screen(text: str) -> dict:
    words = text.upper().replace("*", "").split()
    head, tail = words[:-3][:5], words[-3:]
    return {"type": "headline", "lines": [" ".join(head)] + ["*" + " ".join(tail) + "*"] if head
            else ["*" + " ".join(tail) + "*"]}


def design_screens(script: dict, lang: str) -> dict:
    """One kinetic graphic spec per beat (motion.py renders them)."""
    beats = script["beats"]
    listing = "\n".join(f"{i + 1}. {b['text']}" for i, b in enumerate(beats))
    lang_name = config.LANGUAGES[lang]["name"]
    screens = []
    try:
        r = llm.generate(SCREENS_PROMPT.format(lang_name=lang_name, beats=listing, n=len(beats)),
                         temperature=0.7, task=f"screens-{lang}", strong=True)
        screens = r.get("screens", []) if isinstance(r, dict) else r
    except llm.LLMError as e:
        log(f"[screens:{lang}] failed, using simple headlines: {e}")
    allowed = _numbers_in(" ".join(b["text"] for b in beats))
    for i, b in enumerate(beats):
        sc = screens[i] if i < len(screens) and isinstance(screens[i], dict) else {}
        kind = sc.get("type")
        ok = {
            "headline": bool(sc.get("lines")),
            "stat": isinstance(sc.get("value"), (int, float)),
            "number": bool(sc.get("number")) and bool(sc.get("label")),
            "name": bool(sc.get("name")),
            "bubble": bool(sc.get("text")),
            "quote": bool(sc.get("text")),
        }.get(kind, False)
        if kind == "stat" and ok:
            v = sc["value"]
            shown = f"{v:g}"
            if not any(shown.replace(".", "") in n.replace(".", "") or n.replace(".", "") in shown.replace(".", "")
                       for n in allowed):
                ok = False  # a number the narrator never says
        if i == 0 and kind != "headline":
            ok = False
        b["screen"] = sc if ok else _fallback_screen(b["text"])
    kinds = [b["screen"]["type"] for b in beats]
    log(f"[screens:{lang}] {kinds}")
    return script


_NUM = re.compile(r"[$€£]?\d[\d.,]*%?")


def tidy_screen_text(text: str) -> str:
    """Fix common on-screen text slips: "€8 euro" -> "€8", "208juta" -> "208 juta"."""
    text = re.sub(r"([$€£]\s?\d[\d.,]*(?:[kKmMbB]\b)?)\s+(?:euros?|dollars?|dolar|pounds?)\b(\*?)",
                  r"\1\2", text, flags=re.I)
    text = re.sub(r"(\d)(juta|miliar|ribu|triliun|jt)\b", r"\1 \2", text, flags=re.I)
    for wrong, right in (("milar", "miliar"), ("milyar", "miliar"), ("miliyar", "miliar"),
                         ("trilyun", "triliun"), ("trilliun", "triliun")):
        text = re.sub(rf"\b{wrong}\b", lambda m: right.upper() if m.group(0).isupper() else right,
                      text, flags=re.I)
    return re.sub(r"\s{2,}", " ", text).strip()


def sync_numbers(source: str, target: str) -> str:
    """Make the numbers/currencies in an adapted on-screen text identical to the original."""
    src = _NUM.findall(source or "")
    if not src or not target:
        return target
    it = iter(src)
    return _NUM.sub(lambda m: next(it, m.group(0)), target)


_BAD_QUERY_WORDS = {"logo", "icon", "metaphor", "concept", "illustration", "symbol", "brand",
                    "infographic", "animation", "cartoon", "vector"}


def clean_queries(script: dict, company: str) -> dict:
    """Strip brand names and abstract words that stock sites can't match."""
    brand = {w.lower().strip(".,'\"") for w in company.replace("'s", "").split()}

    def clean(q: str) -> str:
        words = [w for w in q.split()
                 if w.lower().strip(".,'\"").replace("'s", "") not in brand | _BAD_QUERY_WORDS]
        return " ".join(words)

    for b in script["beats"]:
        qs = [clean(q) for q in b["visual_queries"]]
        b["visual_queries"] = [q for q in qs if len(q.split()) >= 1][:3] or ["business people office"]
    script["setting_queries"] = [q for q in (clean(q) for q in script.get("setting_queries", [])) if q][:5]
    return script


def adapt_indonesian(script_en: dict) -> dict:
    import json
    slim = {k: script_en[k] for k in ("title", "banner", "hook_title", "thumb_text", "thumb_badge", "hook", "beats", "description", "hashtags",
                                      "music_mood", "facts_used") if k in script_en}
    slim["beats"] = [{"text": b["text"], "visual_queries": b["visual_queries"]} for b in script_en["beats"]]
    result = llm.generate(ADAPT_PROMPT.format(script=json.dumps(slim, ensure_ascii=False),
                                              cta=config.LANGUAGES["id"]["cta"]),
                          temperature=0.6, task="adapt-id", strong=True)
    result = _validate(result, "id")
    try:
        proofread = _validate(llm.generate(
            PROOFREAD_ID_PROMPT.format(script=json.dumps(result, ensure_ascii=False),
                                       cta=config.LANGUAGES["id"]["cta"]),
            temperature=0.3, task="proofread-id", strong=True), "id")
        if len(proofread["beats"]) == len(result["beats"]):
            result = proofread
    except llm.LLMError as e:
        log(f"[script:id] proofread skipped: {e}")
    # Footage is chosen once from the English beats; keep beat counts aligned
    if len(result["beats"]) != len(script_en["beats"]):
        raise llm.LLMError(f"adapt-id: {len(result['beats'])} beats vs {len(script_en['beats'])} in English")
    for b_id, b_en in zip(result["beats"], script_en["beats"]):
        b_id["visual_queries"] = b_en["visual_queries"]
    result["music_mood"] = script_en.get("music_mood", "documentary")
    result["setting_queries"] = script_en.get("setting_queries", [])
    for key in ("thumb_text", "thumb_badge", "hook_title", "banner"):
        result[key] = tidy_screen_text(sync_numbers(script_en.get(key, ""), result.get(key, "")))
    for key in ("emoji", "thumb_template", "split_top", "split_bottom"):
        result.setdefault(key, script_en.get(key, ""))
    # Native Indonesian clickbait packaging (not a translation of the English one)
    result = package(result, "id")
    result["thumb_focus"] = script_en.get("thumb_focus", "")
    return design_screens(result, "id")
