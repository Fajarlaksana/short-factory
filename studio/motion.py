"""Kinetic on-screen graphics for the whole video, rendered as one transparent overlay track.

Per beat (spec from script.design_screens):
  headline - words build up one by one, synced to the narrator; last line big & yellow (slams in)
  stat     - big number counting up + caption
  number   - yellow "1." tile + label strip wiping in
  name     - lower-third: yellow name box + blue role box sliding in
  bubble   - big emoji "character" bouncing in + yellow speech bubble popping
  quote    - dark quote card sliding up
The first beat is the hook: a bigger, centred headline.

Frames are only rendered while something moves; still periods become one image with a long
duration in an ffconcat list, so a 50 s video needs a few hundred PNGs, not 1500.
"""
import math
import re
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config
from .graphics import emoji_image
from .log import log

W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS
YELLOW = (255, 212, 0)
WHITE = (255, 255, 255)
INK = (18, 18, 18)
BLUE = (30, 91, 216)
TOP = 250          # below the Shorts top bar
LEFT = 70
MAX_W = W - 2 * LEFT


def _font(size: int, italic: bool = False) -> ImageFont.FreeTypeFont:
    key = "kinetic_italic" if italic else "kinetic"
    return ImageFont.truetype(str(config.FONTS_DIR / config.FONTS[key][1]), size)


def _ease_out(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def _ease_back(x: float) -> float:
    x = min(1.0, max(0.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def _shadow(img: Image.Image, blur: int = 8, offset=(3, 6), alpha: int = 170) -> Image.Image:
    pad = blur * 2 + 8
    out = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (pad + offset[0], pad + offset[1]), img.split()[3].point(lambda a: a * alpha // 255))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(img, (pad, pad))
    return out


def text_sprite(text: str, size: int, color=WHITE, italic: bool = False, stroke: int = 3) -> Image.Image:
    f = _font(size, italic)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    img = Image.new("RGBA", (r - l, b - t), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((-l, -t), text, font=f, fill=color, stroke_width=stroke, stroke_fill=(10, 10, 10))
    return _shadow(img)


def _paste(canvas: Image.Image, sprite: Image.Image, x: float, y: float, alpha: float = 1.0,
           scale: float = 1.0, anchor: str = "lt"):
    """Paste with optional alpha/scale. anchor 'lt' (left-top) or 'cc' (centre)."""
    if alpha <= 0.01 or scale <= 0.01:
        return
    sp = sprite
    if abs(scale - 1.0) > 0.01:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.BILINEAR)
    if alpha < 0.99:
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda a: int(a * alpha)))
    if anchor == "cc":
        x, y = x - sp.width / 2, y - sp.height / 2
    elif scale != 1.0:  # keep the scaled sprite centred on its unscaled box
        x -= (sp.width - sprite.width) / 2
        y -= (sp.height - sprite.height) / 2
    canvas.alpha_composite(sp, (int(x), int(y)))


# ---------------------------------------------------------------------------
# Elements. Each has .windows (local times that need per-frame rendering) and .draw(canvas, t)
# ---------------------------------------------------------------------------
class Headline:
    """Lines of words revealed one by one; the *starred* last line is big and yellow."""

    def __init__(self, lines: List[str], word_times: List[float], hook: bool = False):
        self.hook = hook
        small, big = (80, 138) if hook else (62, 106)
        self.items = []  # (sprite, x, y, t_in, is_key)
        parsed = []
        for line in lines:
            key = "*" in line
            parsed.append((line.replace("*", "").strip().upper(), key))
        pad = 24  # text_sprite() adds this much shadow padding on every side
        y = 0
        layout = []
        for text, key in parsed:
            size = big if key else small
            if key:  # shrink the emphasis line until it wraps into at most 2 rows
                while size > 60 and _font(size).getlength(text) > (MAX_W - 20) * 1.9:
                    size = int(size * 0.9)
            gap = int(size * 0.26)
            cur, rows = [], []
            for w in text.split():  # wrap inside MAX_W
                if cur and _font(size).getlength(" ".join(cur + [w])) > MAX_W - 20:
                    rows.append(cur)
                    cur = []
                cur.append(w)
            if cur:
                rows.append(cur)
            for row in rows:
                sprites = [text_sprite(w, size, YELLOW if key else WHITE, stroke=4 if key else 3) for w in row]
                widths = [sp.width - 2 * pad for sp in sprites]
                row_w = sum(widths) + gap * (len(sprites) - 1)
                layout.append((sprites, widths, row_w, gap, y))
                y += int(size * (1.10 if key else 1.20))
        self.height = y
        top = (H * 0.30 - y / 2) if hook else TOP
        k = 0
        for sprites, widths, row_w, gap, ry in layout:
            x = (W - row_w) / 2 if hook else LEFT
            for sp, w in zip(sprites, widths):
                t_in = word_times[k] if k < len(word_times) else (word_times[-1] if word_times else 0)
                self.items.append([sp, x - pad, top + ry - pad, t_in, False])
                x += w + gap
                k += 1
        # mark which items belong to *starred* lines (same order as the layout)
        flags = []
        for text, key in parsed:
            flags += [key] * len(text.split())
        for item, flag in zip(self.items, flags):
            item[4] = flag
        self.windows = [(t, t + 0.22) for *_, t, _ in self.items]

    def draw(self, canvas: Image.Image, t: float):
        for sp, x, y, t_in, key in self.items:
            if t < t_in:
                continue
            p = (t - t_in) / 0.18
            if key:  # slams in: big -> normal with overshoot
                scale = 1.0 + 0.45 * (1 - _ease_back(p)) if p < 1 else 1.0
                _paste(canvas, sp, x, y, alpha=min(1.0, p * 3), scale=scale)
            else:     # rises and fades in
                _paste(canvas, sp, x, y + 18 * (1 - _ease_out(p)), alpha=min(1.0, p * 1.6))


class Stat:
    def __init__(self, value: float, prefix: str, suffix: str, caption: str):
        self.value, self.prefix, self.suffix = float(value), prefix or "", (suffix or "").upper()
        self.decimals = 0 if float(value).is_integer() else min(2, len(f"{value}".split(".")[1]))
        self.caption = text_sprite((caption or "").upper(), 58) if caption else None
        self.windows = [(0.0, 1.0)]

    def _label(self, v: float) -> str:
        num = f"{v:,.{self.decimals}f}"
        return f"{self.prefix}{num}{self.suffix}"

    def draw(self, canvas: Image.Image, t: float):
        p = _ease_out(t / 0.9)
        size = 168
        while size > 80 and _font(size).getlength(self._label(self.value)) > MAX_W - 40:
            size -= 8
        sp = text_sprite(self._label(self.value * p), size, YELLOW, stroke=5)
        scale = 1.0 + 0.25 * (1 - _ease_back(min(1, t / 0.25)))
        _paste(canvas, sp, W / 2, H * 0.30, alpha=min(1, t * 6), scale=scale, anchor="cc")
        if self.caption:
            _paste(canvas, self.caption, W / 2, H * 0.30 + 130 + 20 * (1 - _ease_out(t / 0.4)),
                   alpha=min(1, max(0, (t - 0.15) * 4)), anchor="cc")


class NumberTag:
    def __init__(self, number: str, label: str):
        f = _font(128)
        n = f"{number}".strip().rstrip(".") + "."
        l, t_, r, b = f.getbbox(n)
        box = Image.new("RGBA", (max(200, r - l + 60), 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rounded_rectangle([0, 0, box.width - 1, 199], radius=22, fill=YELLOW)
        d.text(((box.width - (r - l)) / 2 - l, (200 - (b - t_)) / 2 - t_), n, font=f, fill=INK)
        self.tile = _shadow(box)
        text = label.upper()
        size = 84
        while size > 50 and _font(size).getlength(text) > MAX_W - 80:
            size -= 6
        fl = _font(size)
        l, t_, r, b = fl.getbbox(text)
        sh = int(size * 1.6)
        strip = Image.new("RGBA", (r - l + 70, sh), (0, 0, 0, 0))
        d = ImageDraw.Draw(strip)
        d.rounded_rectangle([0, 0, strip.width - 1, sh - 1], radius=16, fill=(40, 40, 40, 220))
        d.text((35 - l, (sh - (b - t_)) / 2 - t_), text, font=fl, fill=WHITE)
        self.strip = _shadow(strip)
        self.windows = [(0.0, 0.55)]

    def draw(self, canvas: Image.Image, t: float):
        cy = H * 0.30
        _paste(canvas, self.tile, W / 2, cy - 95, scale=0.3 + 0.7 * _ease_back(t / 0.22), anchor="cc",
               alpha=min(1, t * 8))
        if t > 0.15:  # label wipes open from the centre
            p = _ease_out((t - 0.15) / 0.3)
            w = max(1, int(self.strip.width * p))
            crop = self.strip.crop(((self.strip.width - w) // 2, 0, (self.strip.width + w) // 2, self.strip.height))
            _paste(canvas, crop, W / 2, cy + 100, anchor="cc")


class NameCard:
    def __init__(self, name: str, role: str):
        def box(text, size, fill, fg):
            f = _font(size)
            l, t_, r, b = f.getbbox(text)
            im = Image.new("RGBA", (r - l + 44, int(size * 1.45)), (0, 0, 0, 0))
            ImageDraw.Draw(im).rectangle([0, 0, im.width, im.height], fill=fill)
            ImageDraw.Draw(im).text((22 - l, (im.height - (b - t_)) / 2 - t_), text, font=f, fill=fg)
            return im
        self.name = _shadow(box(name.upper(), 76, YELLOW, INK))
        self.role = _shadow(box(role.upper(), 54, BLUE, WHITE)) if role else None
        self.windows = [(0.0, 0.5)]

    def draw(self, canvas: Image.Image, t: float):
        y = H * 0.60
        _paste(canvas, self.name, LEFT - 30 - 500 * (1 - _ease_out(t / 0.28)), y)
        if self.role:
            p = _ease_out((t - 0.1) / 0.28)
            _paste(canvas, self.role, LEFT - 30 - 500 * (1 - p), y + self.name.height - 30, alpha=min(1, p * 2))


class Bubble:
    def __init__(self, text: str, emoji: str):
        self.char = emoji_image(emoji or "😱", 340)
        f = _font(64, italic=True)
        words, rows, cur = text.split(), [], ""
        for w in words:
            test = f"{cur} {w}".strip()
            if cur and f.getlength(test) > 620:
                rows.append(cur)
                cur = w
            else:
                cur = test
        rows.append(cur)
        line_h = 84
        bw = int(max(f.getlength(r) for r in rows)) + 70
        bh = line_h * len(rows) + 50
        im = Image.new("RGBA", (bw, bh + 50), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, bw - 1, bh], radius=34, fill=YELLOW)
        d.polygon([(60, bh - 4), (130, bh - 4), (40, bh + 46)], fill=YELLOW)  # tail to the character
        for i, r in enumerate(rows):
            d.text((35, 25 + i * line_h), r, font=f, fill=INK)
        self.bubble = _shadow(im)
        self.windows = [(0.0, 0.7)]

    def draw(self, canvas: Image.Image, t: float):
        cx, cy = W * 0.20, H * 0.70
        if self.char:
            s = _ease_back(t / 0.3)
            wobble = self.char.rotate(8 * math.sin(t * 9) * math.exp(-t * 3), resample=Image.BILINEAR)
            _paste(canvas, _shadow(wobble), cx, cy + 40 * (1 - s), scale=max(0.05, s), anchor="cc")
        if t > 0.18:
            s = _ease_back((t - 0.18) / 0.25)
            _paste(canvas, self.bubble, cx + 70 + self.bubble.width / 2, cy - 170 - self.bubble.height / 2 + 60,
                   scale=max(0.05, s), anchor="cc")


class Quote:
    def __init__(self, text: str, speaker: str):
        f, fs = _font(60, italic=True), _font(46)
        words, rows, cur = f"“{text}”".split(), [], ""
        for w in words:
            test = f"{cur} {w}".strip()
            if cur and f.getlength(test) > MAX_W - 80:
                rows.append(cur)
                cur = w
            else:
                cur = test
        rows.append(cur)
        h = 78 * len(rows) + (100 if speaker else 44)
        im = Image.new("RGBA", (MAX_W, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, MAX_W - 1, h - 1], radius=24, fill=(15, 15, 15, 200))
        d.rectangle([0, 18, 10, h - 18], fill=YELLOW)
        for i, r in enumerate(rows):
            d.text((44, 24 + i * 78), r, font=f, fill=WHITE)
        if speaker:
            d.text((44, h - 72), f"— {speaker.upper()}", font=fs, fill=YELLOW)
        self.card = _shadow(im)
        self.windows = [(0.0, 0.4)]

    def draw(self, canvas: Image.Image, t: float):
        p = _ease_out(t / 0.3)
        _paste(canvas, self.card, LEFT - 20, H * 0.58 + 60 * (1 - p), alpha=p)


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------
def _norm(w: str) -> str:
    return re.sub(r"[^\w]", "", w.lower())


def _word_times(text_words: List[str], words: List[dict], start: float, end: float) -> List[float]:
    """Time each on-screen word appears: when the narrator says it (or evenly, if not spoken)."""
    spoken = [(w["start"], _norm(w["word"])) for w in words if start - 0.05 <= w["start"] < end]
    times, pos, last = [], 0, start + 0.05
    for tw in text_words:
        n = _norm(tw)
        hit = next((k for k in range(pos, len(spoken)) if spoken[k][1] == n and n), None)
        if hit is not None:
            last = max(last, spoken[hit][0] - start)
            pos = hit + 1
        else:
            last = last + 0.14
        times.append(min(last, max(0.05, end - start - 0.3)))
    return times


def _element(screen: dict, words, start, end, hook: bool):
    kind = screen.get("type")
    try:
        if kind == "stat":
            return Stat(screen["value"], screen.get("prefix", ""), screen.get("suffix", ""), screen.get("caption", ""))
        if kind == "number":
            return NumberTag(screen["number"], screen["label"])
        if kind == "name":
            return NameCard(screen["name"], screen.get("role", ""))
        if kind == "bubble":
            return Bubble(screen["text"], screen.get("emoji", ""))
        if kind == "quote":
            return Quote(screen["text"], screen.get("speaker", ""))
    except Exception as e:
        log(f"[motion] {kind} element failed ({e}), using a headline")
    lines = screen.get("lines") or ["*" + " ".join(screen.get("text", "").split()[:4]) + "*"]
    text_words = [w for line in lines for w in line.replace("*", "").split()]
    return Headline(lines, _word_times(text_words, words, start, end), hook=hook)


def _top_gradient() -> Image.Image:
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(0, 900):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(150 * (1 - y / 900) ** 1.6)))
    return g


def build_overlay(beats: List[dict], timings: List[tuple], words: List[dict], out_dir: Path) -> Path:
    """Render the overlay track; returns an ffconcat file usable as an ffmpeg input."""
    out_dir.mkdir(parents=True, exist_ok=True)
    base = _top_gradient()
    entries = []  # (png name, duration)
    n_png = 0
    for bi, ((start, end), beat) in enumerate(zip(timings, beats)):
        el = _element(beat.get("screen") or {}, words, start, end, hook=(bi == 0))
        dur = end - start
        # sample times: every frame inside animation windows, one frame for still stretches
        ts, t = [], 0.0
        windows = sorted((max(0, a), min(dur, b)) for a, b in el.windows if a < dur)
        while t < dur - 1e-6:
            active = any(a - 1e-6 <= t < b for a, b in windows)
            ts.append(t)
            if active:
                t += 1 / FPS
            else:
                nxt = min([a for a, _ in windows if a > t + 1e-6] + [dur])
                t = max(nxt, t + 1 / FPS)
        for k, t in enumerate(ts):
            frame = base.copy()
            el.draw(frame, t)
            name = f"m_{n_png:04d}.png"
            frame.save(out_dir / name, compress_level=1)
            n_png += 1
            t_next = ts[k + 1] if k + 1 < len(ts) else dur
            entries.append((name, t_next - t))
    lines = ["ffconcat version 1.0"]
    for name, d in entries:
        lines += [f"file '{name}'", f"duration {d:.4f}"]
    lines.append(f"file '{entries[-1][0]}'")  # the concat demuxer needs the last file twice
    concat = out_dir / "overlay.ffconcat"
    concat.write_text("\n".join(lines), encoding="utf-8")
    log(f"[motion] {n_png} overlay frames for {len(beats)} beats")
    return concat


def element_entries(beats: List[dict], timings: List[tuple]) -> List[float]:
    """Times when a new graphic appears (for whoosh/pop sound effects)."""
    return [start for (start, _), b in zip(timings, beats)]
