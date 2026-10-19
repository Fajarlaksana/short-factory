"""Beat timing + word-by-word ASS captions (active word highlighted, pop-in per chunk)."""
import difflib
import re
from pathlib import Path
from typing import List

from . import config

CAPTION_Y = 1240          # baseline of captions (Shorts UI covers the bottom ~350px)
WORDS_PER_CHUNK = 3
MAX_CHUNK_CHARS = 14
HIGHLIGHT = "&H0000E6FF&"  # ASS colours are &HBBGGRR -> warm yellow
WHITE = "&H00FFFFFF&"


def _norm(w: str) -> str:
    return re.sub(r"[^\w]", "", w.lower())


def beat_times(beats: List[dict], words: List[dict]) -> List[tuple]:
    """Map each beat to (start, end) seconds in the narration."""
    script_tokens, token_beat = [], []
    for i, b in enumerate(beats):
        for t in b["text"].split():
            script_tokens.append(_norm(t))
            token_beat.append(i)
    heard = [_norm(w["word"]) for w in words]
    mapping = {}
    for block in difflib.SequenceMatcher(None, script_tokens, heard, autojunk=False).get_matching_blocks():
        for k in range(block.size):
            mapping[block.a + k] = block.b + k

    starts = []
    for i in range(len(beats)):
        idxs = [s for s, b in enumerate(token_beat) if b == i]
        w_idx = next((mapping[s] for s in idxs if s in mapping), None)
        if w_idx is None:  # no exact match: interpolate by position in the script
            w_idx = min(len(words) - 1, round(idxs[0] / max(1, len(script_tokens)) * len(words)))
        starts.append(words[w_idx]["start"])
    starts[0] = 0.0
    for i in range(1, len(starts)):  # keep monotonic with a sane minimum length
        starts[i] = max(starts[i], starts[i - 1] + 0.8)
    end = words[-1]["end"] + 0.6
    return [(starts[i], starts[i + 1] if i + 1 < len(starts) else end) for i in range(len(starts))]


def _chunks(words: List[dict]) -> List[List[dict]]:
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        text = " ".join(x["word"] for x in cur)
        if (len(cur) >= WORDS_PER_CHUNK or len(text) >= MAX_CHUNK_CHARS
                or re.search(r"[.!?,:;]$", w["word"])):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def _ts(t: float) -> str:
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")")


MONEY = "&H0055E000&"       # green for numbers / money words
YELLOW_BOX = "&H0000D7FF&"  # #FFD700
HOOK_SECONDS = 2.8
_MONEY_WORDS = {"billion", "million", "trillion", "percent", "miliar", "juta", "triliun", "persen",
                "dollar", "dollars", "dolar", "euro", "euros", "rupiah"}


def _is_money(word: str) -> bool:
    w = word.lower().strip(".,!?;:")
    return bool(re.search(r"[\d$€£%]", w)) or w in _MONEY_WORDS


def split_marked(text: str):
    """'They LOSE money on *hot dogs*' -> [(word, is_key), ...] (stars mark the key word/phrase)."""
    out, key = [], False
    for token in text.split():
        stars = token.count("*")
        opens = token.lstrip("\"'(").startswith("*")
        if opens:
            key = True
        clean = token.replace("*", "")
        if clean:
            out.append((clean, key))
        # closes when a star follows the start ("*dinner*?", "dogs*", "*word*")
        if (opens and stars >= 2) or (not opens and stars >= 1):
            key = False
    if not any(k for _, k in out) and out:  # no marker: highlight the longest word
        i = max(range(len(out)), key=lambda j: len(out[j][0]))
        out[i] = (out[i][0], True)
    return out


def _wrap(words, max_chars: int):
    lines, cur = [], []
    for w in words:
        if cur and len(" ".join(x for x, _ in cur + [w])) > max_chars:
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def _hook_title_event(hook_title: str) -> str:
    words = [(w.upper(), k) for w, k in split_marked(hook_title)]
    total = len(" ".join(w for w, _ in words))
    size, max_chars = (215, 10) if total <= 22 else (180, 12) if total <= 32 else (150, 15)
    lines = _wrap(words, max_chars)[:3]
    body = "\\N".join(" ".join(f"{{\\c{HIGHLIGHT}}}{_esc(w)}{{\\c{WHITE}}}" if k else _esc(w)
                               for w, k in line) for line in lines)
    # Slams in (overshoot), tilts slightly, then flicks away when the story starts
    anim = ("{\\an8\\pos(540,300)\\fs%d\\frz-3\\fscx30\\fscy30\\alpha&HFF&"
            "\\t(0,140,\\fscx116\\fscy116\\alpha&H00&)\\t(140,260,\\fscx100\\fscy100)"
            "\\t(%d,%d,\\fscx40\\fscy40\\alpha&HFF&)}" % (size, int(HOOK_SECONDS * 1000) - 180,
                                                         int(HOOK_SECONDS * 1000)))
    return f"Dialogue: 2,{_ts(0)},{_ts(HOOK_SECONDS)},Hook,,0,0,0,,{anim}{body}"


def build_ass(words: List[dict], banner: str, out_path: Path, duration: float, hook_title: str = ""):
    cap_font = config.FONTS["caption"][0]
    title_font = config.FONTS["title"][0]
    margin_v = config.HEIGHT - CAPTION_Y
    lines = [
        "[Script Info]", "ScriptType: v4.00+",
        f"PlayResX: {config.WIDTH}", f"PlayResY: {config.HEIGHT}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Caption,{cap_font},128,{WHITE},{WHITE},&H00000000,&H64000000,"
        f"0,0,0,0,100,100,0,0,1,8,4,2,90,90,{margin_v},1",
        # Big opening headline: white + yellow key word, heavy outline and drop shadow
        f"Style: Hook,{title_font},150,{WHITE},{WHITE},&H00000000,&H96000000,"
        "0,0,0,0,100,100,1,0,1,10,9,8,70,70,300,1",
        # Persistent top label: black text on a bright yellow box
        f"Style: Banner,{title_font},80,&H00141414&,&H00141414&,{YELLOW_BOX},&H00000000,"
        "0,0,0,0,100,100,1,0,3,22,0,8,80,80,200,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    banner_start = 0.0
    if hook_title:
        lines.append(_hook_title_event(hook_title))
        banner_start = HOOK_SECONDS - 0.1
    if banner:
        lines.append(f"Dialogue: 1,{_ts(banner_start)},{_ts(duration)},Banner,,0,0,0,,"
                     f"{{\\an8\\move(540,140,540,200,0,260)\\fad(260,0)}}{_esc(banner.upper())}")

    chunks = _chunks(words)
    for ci, chunk in enumerate(chunks):
        next_start = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else chunk[-1]["end"] + 0.5
        chunk_end = min(next_start, chunk[-1]["end"] + 0.5)
        tokens = [_esc(w["word"].upper()) for w in chunk]
        for wi, w in enumerate(chunk):
            start = chunk[0]["start"] if wi == 0 else w["start"]
            end = chunk[wi + 1]["start"] if wi + 1 < len(chunk) else chunk_end
            if end <= start:
                continue
            parts = []
            for k, t in enumerate(tokens):
                if k == wi:  # spoken word: yellow (green for money) and slightly bigger
                    color = MONEY if _is_money(t) else HIGHLIGHT
                    parts.append(f"{{\\c{color}\\fscx112\\fscy112}}{t}{{\\c{WHITE}\\fscx100\\fscy100}}")
                elif _is_money(t):
                    parts.append(f"{{\\c{MONEY}}}{t}{{\\c{WHITE}}}")
                else:
                    parts.append(t)
            pop = "{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
            lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Caption,,0,0,0,,{pop}{' '.join(parts)}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
