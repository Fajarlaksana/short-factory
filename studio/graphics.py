"""Thumbnail + on-screen title graphics (PIL): clickbait-style but clean.

Visual language shared by the thumbnail and the video's opening headline:
white words with a heavy black stroke, ONE key word on a tilted yellow box, a big emoji,
a red number sticker, and (thumbnail) a red circle + arrow on the key object.
"""
import math
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config, llm
from .log import log

W, H = config.WIDTH, config.HEIGHT
YELLOW = (255, 214, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (232, 30, 40)
EMOJI_DIR = config.ROOT / "assets" / "studio" / "emoji"
EMOJI_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------
def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(config.FONTS_DIR / config.FONTS["title"][1]), size)


def split_marked(text: str):
    from .captions import split_marked as _split
    return _split(text)


def emoji_image(emoji: str, size: int) -> Optional[Image.Image]:
    """Noto emoji PNG (Google, Apache-2.0), cached locally."""
    if not emoji:
        return None
    cps = [f"{ord(c):x}" for c in emoji if ord(c) not in (0xFE0F, 0x200D)]
    if not cps:
        return None
    name = "_".join(cps)
    path = EMOJI_DIR / f"{name}.png"
    if not path.exists():
        for url in (f"https://fonts.gstatic.com/s/e/notoemoji/latest/{name}/512.png",
                    f"https://cdn.jsdelivr.net/gh/googlefonts/noto-emoji@v2.042/png/512/emoji_u{name}.png"):
            try:
                r = requests.get(url, timeout=20)
                if r.ok and r.content[:4] == b"\x89PNG":
                    path.write_bytes(r.content)
                    break
            except requests.RequestException:
                continue
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    return img.resize((size, size), Image.LANCZOS)


def _shadowed(img: Image.Image, offset=(8, 14), blur=12, alpha=170) -> Image.Image:
    """Add a soft drop shadow under an RGBA image (canvas grows to fit)."""
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1]))
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = img.split()[3].point(lambda a: a * alpha // 255)
    shadow.paste((0, 0, 0, 255), (pad + offset[0], pad + offset[1]), mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def word_image(word: str, size: int, key: bool) -> Image.Image:
    """One word: white with black stroke, or (key) black on a tilted yellow box."""
    f = font(size)
    stroke = max(6, size // 13)
    l, t, r, b = f.getbbox(word, stroke_width=0 if key else stroke)
    w, h = r - l, b - t
    if key:
        px, py = int(size * 0.16), int(size * 0.10)
        img = Image.new("RGBA", (w + px * 2, h + py * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=size // 9, fill=YELLOW)
        d.text((px - l, py - t), word, font=f, fill=(18, 18, 18))
        return img.rotate(-4, expand=True, resample=Image.BICUBIC)
    img = Image.new("RGBA", (w + stroke * 2, h + stroke * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((stroke - l, stroke - t), word, font=f, fill=WHITE,
                             stroke_width=stroke, stroke_fill=BLACK)
    return img


def text_block(text: str, size: int, max_width: int) -> Image.Image:
    """Marked text -> centred multi-line block (key word on yellow), with drop shadow."""
    words = [(w.upper(), k) for w, k in split_marked(text)]
    imgs = [word_image(w, size, k) for w, k in words]
    gap = int(size * 0.07)
    lines, cur, cur_w = [], [], 0
    for im in imgs:
        add = im.width + (gap if cur else 0)
        if cur and cur_w + add > max_width:
            lines.append(cur)
            cur, cur_w = [], 0
            add = im.width
        cur.append(im)
        cur_w += add
    if cur:
        lines.append(cur)
    line_h = [max(im.height for im in line) for line in lines]
    line_w = [sum(im.width for im in line) + gap * (len(line) - 1) for line in lines]
    spacing = int(size * 0.06)
    block = Image.new("RGBA", (max(line_w), sum(line_h) + spacing * (len(lines) - 1)), (0, 0, 0, 0))
    y = 0
    for line, lw, lh in zip(lines, line_w, line_h):
        x = (block.width - lw) // 2
        for im in line:
            block.alpha_composite(im, (x, y + (lh - im.height) // 2))
            x += im.width + gap
        y += lh + spacing
    return _shadowed(block)


def fit_text_block(text: str, max_width: int, max_height: int, start: int = 300, minimum: int = 120):
    size = start
    while True:
        block = text_block(text, size, max_width)
        if (block.width <= max_width + 80 and block.height <= max_height) or size <= minimum:
            return block
        size -= 15


def badge(text: str, size: int = 96, fill=RED, fg=WHITE, angle: float = 5) -> Image.Image:
    f = font(size)
    l, t, r, b = f.getbbox(text)
    px, py = int(size * 0.42), int(size * 0.24)
    img = Image.new("RGBA", (r - l + px * 2, b - t + py * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=size // 4, fill=fill,
                        outline=WHITE, width=max(5, size // 16))
    d.text((px - l, py - t), text, font=f, fill=fg)
    return _shadowed(img.rotate(angle, expand=True, resample=Image.BICUBIC), blur=10)


def arrow(start: Tuple[float, float], end: Tuple[float, float], width: int = 34,
          color=RED) -> Image.Image:
    """Thick slightly curved arrow with a white rim, as a full-frame RGBA layer."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    (x0, y0), (x1, y1) = start, end
    ang = math.atan2(y1 - y0, x1 - x0)
    head = width * 2.4
    # shaft stops where the head starts
    sx1, sy1 = x1 - math.cos(ang) * head * 0.8, y1 - math.sin(ang) * head * 0.8
    # gentle curve via a mid control point
    mx, my = (x0 + sx1) / 2 - math.sin(ang) * 60, (y0 + sy1) / 2 + math.cos(ang) * 60
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t ** 2 * sx1,
            (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t ** 2 * sy1) for t in np.linspace(0, 1, 30)]
    left = (x1 + math.cos(ang + 2.6) * head, y1 + math.sin(ang + 2.6) * head)
    right = (x1 + math.cos(ang - 2.6) * head, y1 + math.sin(ang - 2.6) * head)
    for col, extra in ((WHITE, 14), (color, 0)):
        d.line(pts, fill=col, width=width + extra, joint="curve")
        d.ellipse([x0 - (width + extra) / 2, y0 - (width + extra) / 2,
                   x0 + (width + extra) / 2, y0 + (width + extra) / 2], fill=col)
        grow = extra * 0.9
        d.polygon([(x1 + math.cos(ang) * grow, y1 + math.sin(ang) * grow),
                   (left[0] + math.cos(ang + 2.6) * grow, left[1] + math.sin(ang + 2.6) * grow),
                   (right[0] + math.cos(ang - 2.6) * grow, right[1] + math.sin(ang - 2.6) * grow)],
                  fill=col)
    return layer


def circle(box: Tuple[int, int, int, int], width: int = 16) -> Image.Image:
    """Hand-drawn-looking red ellipse around a box, as a full-frame layer."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    px, py = (x1 - x0) * 0.18 + 20, (y1 - y0) * 0.18 + 20
    rect = [x0 - px, y0 - py, x1 + px, y1 + py]
    d.ellipse([rect[0] - 6, rect[1] - 6, rect[2] + 6, rect[3] + 6], outline=WHITE, width=width + 12)
    d.ellipse(rect, outline=RED, width=width)
    return layer.filter(ImageFilter.GaussianBlur(0.6))


# ---------------------------------------------------------------------------
# Frames for the thumbnail background
# ---------------------------------------------------------------------------
def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-400:])


def clean_frame(clip: str, at: float, out: Path, w: int = W, h: int = H):
    seek = [] if clip.lower().endswith((".jpg", ".jpeg", ".png")) else ["-ss", f"{at:.2f}"]
    _run(["ffmpeg", "-y", "-v", "error", *seek, "-i", clip, "-frames:v", "1", "-vf",
          f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          "eq=saturation=1.10:contrast=1.04", str(out)])


def colorfulness(img: Image.Image) -> float:
    a = np.asarray(img.convert("RGB").resize((180, 320)), dtype=np.float32)
    rg = a[..., 0] - a[..., 1]
    yb = 0.5 * (a[..., 0] + a[..., 1]) - a[..., 2]
    return float(np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean())
                 + 0.25 * a.mean(axis=2).std())


def best_frames(clips: List[str], workdir: Path, n: int = 3) -> List[Image.Image]:
    """Most lively clean frames from the first clips (the hook clip gets a head start)."""
    scored = []
    for ci, clip in enumerate(clips[:5]):
        for at in (0.8, 2.4):
            path = workdir / f"cand_{ci}_{at}.png"
            try:
                clean_frame(clip, at, path)
                img = Image.open(path).convert("RGB")
                img.load()
                scored.append((colorfulness(img) * (1.25 if ci == 0 else 1.0), ci, img))
            except Exception:
                pass
            finally:
                path.unlink(missing_ok=True)
    scored.sort(key=lambda x: x[0], reverse=True)
    out, used = [], set()
    for _, ci, img in scored:  # prefer frames from different clips
        if ci not in used:
            out.append(img)
            used.add(ci)
        if len(out) >= n:
            break
    return out or [Image.new("RGB", (W, H), (20, 20, 30))]


def find_object(img: Image.Image, focus: str) -> Optional[Tuple[int, int, int, int]]:
    """Ask a vision model where the focus object is. Returns a pixel box or None."""
    if not focus:
        return None
    import io
    buf = io.BytesIO()
    img.convert("RGB").resize((540, 960)).save(buf, "JPEG", quality=85)
    prompt = (f'Find the most prominent "{focus}" (or the main subject if there is no {focus}) in this '
              "image. Return JSON {\"found\": true/false, \"box_2d\": [ymin, xmin, ymax, xmax]} with "
              "coordinates normalized to 0-1000. found=false if nothing clearly visible.")
    try:
        r = llm.generate(prompt, images=[buf.getvalue()], temperature=0.0, task="thumb-focus")
        if not r.get("found") or len(r.get("box_2d", [])) != 4:
            return None
        y0, x0, y1, x1 = [float(v) for v in r["box_2d"]]
        box = (int(x0 / 1000 * W), int(y0 / 1000 * H), int(x1 / 1000 * W), int(y1 / 1000 * H))
        bw, bh = box[2] - box[0], box[3] - box[1]
        if bw < 80 or bh < 80 or bw * bh > 0.22 * W * H:  # too tiny, or too big to circle nicely
            return None
        return box
    except Exception as e:
        log(f"[thumb] focus detection skipped: {str(e)[:80]}")
        return None


PHOTO_CACHE = config.CACHE_DIR / "photos"
PHOTO_CACHE.mkdir(parents=True, exist_ok=True)


def photo_candidates(queries: List[str], n: int = 4) -> List[Image.Image]:
    """Vertical stock photos (Pixabay) for the thumbnail background: sharper and more on-topic
    than video frames. Pixabay content is free to use without attribution."""
    import os
    out, seen = [], set()
    for q in [q for q in queries if q][:3]:
        try:
            r = requests.get("https://pixabay.com/api/", timeout=20, params={
                "key": os.environ.get("PIXABAY_API_KEY"), "q": q[:100], "image_type": "photo",
                "orientation": "vertical", "safesearch": "true", "per_page": 5, "order": "popular"})
            hits = r.json().get("hits", []) if r.ok else []
        except Exception:
            hits = []
        for h in hits[:2]:
            if h["id"] in seen:
                continue
            seen.add(h["id"])
            path = PHOTO_CACHE / f"{h['id']}.jpg"
            try:
                if not path.exists():
                    path.write_bytes(requests.get(h["largeImageURL"], timeout=30).content)
                img = Image.open(path).convert("RGB")
                scale = max(W / img.width, H / img.height)
                img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1), Image.LANCZOS)
                img = img.crop(((img.width - W) // 2, (img.height - H) // 2,
                                (img.width - W) // 2 + W, (img.height - H) // 2 + H))
                from PIL import ImageEnhance
                img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.08)).enhance(1.04)
                out.append(img)
            except Exception:
                continue
        if len(out) >= n:
            break
    return out[:n]


def choose_frame(frames: List[Image.Image], s: dict) -> Tuple[int, Optional[Tuple[int, int, int, int]]]:
    """Let a vision model pick the best thumbnail background and locate the focus object."""
    import io
    if len(frames) == 1 and not s.get("thumb_focus"):
        return 0, None
    images = []
    for fr in frames:
        buf = io.BytesIO()
        fr.convert("RGB").resize((360, 640)).save(buf, "JPEG", quality=82)
        images.append(buf.getvalue())
    focus = s.get("thumb_focus") or "the main subject"
    prompt = f"""You pick the background picture for a YouTube Shorts thumbnail.
Video title: "{s.get('title', '')}". Thumbnail text: "{s.get('thumb_text', '')}".
Key object: "{focus}". There are {len(frames)} images, numbered 1..{len(frames)} in the attached order.

Choose the image that will get the most clicks: it must show the video's TOPIC / the company's
world (e.g. a gym for a gym chain, an airplane for an airline) so a viewer instantly gets it.
Prefer a human face with strong emotion or the key object big and sharp, bright, uncluttered.
Reject images that only match a single word of the text but not the topic (e.g. birthday
candles for "2020"), and images unrelated to the title even if they are pretty.
Never pick suggestive or revealing images (towels, swimwear, lingerie) - they break YouTube's
thumbnail policy. Never pick graphics with big text, logos, green screens or "like/subscribe"
templates - only real photos/footage.
Then give the bounding box of the key object (or the person's face) in the chosen image,
normalized 0-1000 as [ymin, xmin, ymax, xmax], or null if there is no clear object.

Return JSON: {{"best": 1, "box_2d": [ymin, xmin, ymax, xmax] or null}}"""
    try:
        r = llm.generate(prompt, images=images, temperature=0.0, task="thumb-pick")
        idx = int(r.get("best", 1)) - 1
        idx = idx if 0 <= idx < len(frames) else 0
        box = None
        if isinstance(r.get("box_2d"), list) and len(r["box_2d"]) == 4:
            y0, x0, y1, x1 = [float(v) for v in r["box_2d"]]
            box = (int(x0 / 1000 * W), int(y0 / 1000 * H), int(x1 / 1000 * W), int(y1 / 1000 * H))
            bw, bh = box[2] - box[0], box[3] - box[1]
            if bw < 80 or bh < 80 or bw * bh > 0.22 * W * H:
                box = None
        return idx, box
    except Exception as e:
        log(f"[thumb] vision pick skipped: {str(e)[:80]}")
        return 0, None


# ---------------------------------------------------------------------------
# Thumbnail templates
# ---------------------------------------------------------------------------
def _grade(img: Image.Image, text_at_bottom: bool = True) -> Image.Image:
    """Vignette + dark gradient where the text goes."""
    base = img.convert("RGBA")
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W * 0.75), (yy - H / 2) / (H * 0.62))
    vign = np.clip((r - 0.55) * 1.4, 0, 1) * 170
    if text_at_bottom:
        grad = np.clip((yy - H * 0.45) / (H * 0.40), 0, 1) * 225
    else:
        grad = np.clip((H * 0.55 - yy) / (H * 0.45), 0, 1) * 235
    alpha = np.maximum(vign, grad).astype(np.uint8)
    overlay = Image.fromarray(np.dstack([np.zeros_like(alpha)] * 3 + [alpha]), "RGBA")
    return Image.alpha_composite(base, overlay)


def _paste_center(canvas: Image.Image, im: Image.Image, cx: float, cy: float):
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def kfont(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(config.FONTS_DIR / config.FONTS["kinetic"][1]), size)


def news_headline(text: str, max_width: int) -> Image.Image:
    """News-explainer headline (like Indonesian explainer channels): setup line(s) in white, the
    *starred* payoff big in yellow, left-aligned, soft shadow, no hard outline.
    Rendered at 2x and downsampled so the edges stay smooth."""
    ss = 2
    if "*" in text:  # keep reading order: setup (white) -> payoff (yellow) -> tail (white)
        head, _, rest = text.partition("*")
        payoff = rest.split("*")[0]
        tail = rest.split("*", 1)[1].strip() if "*" in rest else ""
        setup = head.strip()
    else:
        words = text.split()
        setup, payoff, tail = " ".join(words[:-3]), " ".join(words[-3:]), ""

    def wrap(t, size, max_rows):
        while True:
            f, out, cur = kfont(size * ss), [], ""
            for w in t.upper().split():
                test = f"{cur} {w}".strip()
                if cur and f.getlength(test) > max_width * ss:
                    out.append(cur)
                    cur = w
                else:
                    cur = test
            if cur:
                out.append(cur)
            if len(out) <= max_rows or size <= 56:
                return out, size
            size -= 6

    rows = []
    if setup:
        lines, size = wrap(setup, 78, 3)
        rows += [(ln, size, WHITE) for ln in lines]
    lines, size = wrap(payoff, 132, 3)
    rows += [(ln, size, YELLOW) for ln in lines]
    if tail.strip(" ?!."):
        lines, size = wrap(tail, 78, 2)
        rows += [(ln, size, WHITE) for ln in lines]
    elif tail:  # trailing "?!" sticks to the payoff
        rows[-1] = (rows[-1][0] + tail.strip(), rows[-1][1], rows[-1][2])
    heights = [int(sz * ss * (1.04 if col == YELLOW else 1.10)) for _, sz, col in rows]
    block = Image.new("RGBA", ((max_width + 20) * ss, sum(heights) + 20 * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(block)
    y = 6 * ss
    for (ln, sz, col), h in zip(rows, heights):
        f = kfont(sz * ss)
        l, t, r, b = f.getbbox(ln)
        d.text((-l, y - t + (h - (b - t)) // 2), ln, font=f, fill=col)
        y += h
    block = block.crop(block.getbbox() or (0, 0, 1, 1))
    block = block.resize((block.width // ss, block.height // ss), Image.LANCZOS)
    return _shadowed(block, offset=(0, 6), blur=18, alpha=230)


def thumbnail_claim(frame: Image.Image, s: dict, focus_box=None) -> Image.Image:
    """Clean news-style thumbnail: photo + headline at the top. Nothing else."""
    text = s.get("thumb_text") or s.get("title", "")
    block = news_headline(text, W - 140)
    base = frame.convert("RGBA")
    # smooth dark gradient behind the headline + light vignette (no hard bands)
    yy, xx = np.mgrid[0:H, 0:W]
    cover = (block.height + 260) / H
    grad = np.clip(1 - yy / (H * cover), 0, 1) ** 1.3 * 215
    r = np.hypot((xx - W / 2) / (W * 0.8), (yy - H / 2) / (H * 0.7))
    vign = np.clip((r - 0.6) * 1.2, 0, 1) * 120
    alpha = np.maximum(grad, vign).astype(np.uint8)
    img = Image.alpha_composite(base, Image.fromarray(np.dstack([np.zeros_like(alpha)] * 3 + [alpha]), "RGBA"))
    img.alpha_composite(block, (52, 190))
    return img


def _label(text: str, size: int, color) -> Image.Image:
    f = kfont(size)
    l, t, r, b = f.getbbox(text)
    im = Image.new("RGBA", (r - l + 20, b - t + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=f, fill=color,
                            stroke_width=max(3, size // 26), stroke_fill=(12, 12, 12))
    return _shadowed(im, offset=(4, 10), blur=14, alpha=210)


def thumbnail_split(top_frame: Image.Image, bottom_frame: Image.Image, s: dict) -> Image.Image:
    """Two halves (e.g. what you see vs what really happens) with news-style labels."""
    half = H // 2
    img = Image.new("RGBA", (W, H), BLACK + (255,))
    for frame, y in ((top_frame, 0), (bottom_frame, half)):
        f = frame.convert("RGB")
        scale = max(W / f.width, half / f.height)
        f = f.resize((int(f.width * scale) + 1, int(f.height * scale) + 1), Image.LANCZOS)
        f = f.crop(((f.width - W) // 2, (f.height - half) // 2, (f.width - W) // 2 + W,
                    (f.height - half) // 2 + half))
        img.paste(f, (0, y))
    # darken the lower part of each half where its label sits
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for y0 in (0, half):
        for y in range(half):
            a = int(200 * max(0.0, (y - half * 0.45) / (half * 0.55)) ** 1.4)
            d.line([(0, y0 + y), (W, y0 + y)], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, shade)
    ImageDraw.Draw(img).rectangle([0, half - 6, W, half + 6], fill=YELLOW)

    def fit(text, size, color):
        while size > 60 and kfont(size).getlength(text) > W - 120:
            size -= 6
        return _label(text, size, color)

    top_label = fit(s["split_top"].upper(), 120, WHITE)
    bottom_label = fit(s["split_bottom"].upper(), 140, YELLOW)
    img.alpha_composite(top_label, (50, half - top_label.height - 40))
    img.alpha_composite(bottom_label, (50, H - bottom_label.height - 230))

    med = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    md = ImageDraw.Draw(med)
    md.ellipse([0, 0, 199, 199], fill=YELLOW, outline=BLACK, width=8)
    md.polygon([(100, 165), (45, 90), (80, 90), (80, 35), (120, 35), (120, 90), (155, 90)], fill=BLACK)
    _paste_center(img, _shadowed(med), W - 170, half)
    if s.get("thumb_text"):
        head = news_headline(s["thumb_text"], W - 160)
        head = head.resize((int(head.width * 0.62), int(head.height * 0.62)), Image.LANCZOS)
        img.alpha_composite(head, (40, 150))
    return img


def make_thumbnail(top_clips: List[str], bottom_clips: List[str], s: dict, out_jpg: Path, workdir: Path):
    """top_clips: the hook's clips (most on-topic); bottom_clips: good clips from the reveal."""
    photos = photo_candidates([s.get("thumb_focus", "")] + list(s.get("setting_queries", []))[:2], n=4)
    if (config.THUMB_SPLIT and s.get("thumb_template") == "split" and s.get("split_top") and s.get("split_bottom")
            and top_clips and bottom_clips):
        tops = photos[:2] + best_frames(top_clips, workdir, n=2)
        ti, _ = choose_frame(tops, {**s, "thumb_text": s["split_top"]})
        bottoms = photos[2:] + best_frames(bottom_clips, workdir, n=3)
        bi, _ = choose_frame(bottoms, {**s, "thumb_text": s["split_bottom"]})
        img = thumbnail_split(tops[ti], bottoms[bi], s)
    else:
        frames = photos + best_frames(top_clips + bottom_clips, workdir, n=3)
        idx, box = choose_frame(frames, s)
        img = thumbnail_claim(frames[idx], s, box)
    # 4:4:4 chroma keeps yellow text edges clean (default 4:2:0 makes them look rough)
    img.convert("RGB").save(out_jpg, quality=95, subsampling=0)


# ---------------------------------------------------------------------------
# Animated opening headline + banner for the video
# ---------------------------------------------------------------------------
HOOK_SECONDS = 2.8
HOOK_TOP = 150  # y of the overlay canvas in the video


def _ease_out_back(x: float) -> float:
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def hook_frames(s: dict, out_dir: Path, fps: int = 30) -> Path:
    """PNG sequence (1080x900) of the headline slamming in, shaking, emoji popping, flicking out."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cw, ch = W, 900
    block = fit_text_block(s.get("hook_title") or s.get("banner", ""), W - 120, 560, start=175, minimum=110)
    emo = emoji_image(s.get("emoji", ""), 250)
    n = int(HOOK_SECONDS * fps)
    for i in range(n):
        t = i / fps
        frame = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        # headline scale / alpha
        if t < 0.22:
            scale = 0.25 + 0.75 * _ease_out_back(t / 0.22)
            alpha = min(1.0, t / 0.08)
        elif t > HOOK_SECONDS - 0.22:
            k = (t - (HOOK_SECONDS - 0.22)) / 0.22
            scale, alpha = 1.0 + 0.25 * k, 1.0 - k
        else:
            scale, alpha = 1.0 + 0.018 * math.sin((t - 0.22) * 7), 1.0
        shake = 9 * math.exp(-(t - 0.22) * 9) * math.sin(t * 90) if t >= 0.22 else 0
        bw, bh = max(1, int(block.width * scale)), max(1, int(block.height * scale))
        b = block.resize((bw, bh), Image.BILINEAR).rotate(-2, expand=True, resample=Image.BILINEAR)
        if alpha < 1:
            b.putalpha(b.split()[3].point(lambda a: int(a * alpha)))
        cx, cy = cw / 2 + shake, ch * 0.56
        frame.alpha_composite(b, (int(cx - b.width / 2), int(cy - b.height / 2)))
        # emoji pops in a beat later and wobbles
        if emo and t >= 0.30:
            te = t - 0.30
            es = _ease_out_back(min(1.0, te / 0.25)) * (1.0 - (0.0 if t < HOOK_SECONDS - 0.22 else
                                                               (t - (HOOK_SECONDS - 0.22)) / 0.22))
            if es > 0.02:
                e = emo.resize((max(1, int(emo.width * es)), max(1, int(emo.height * es))), Image.BILINEAR)
                e = e.rotate(10 * math.sin(te * 6), expand=True, resample=Image.BILINEAR)
                ex = min(cw - e.width / 2 + 20, cw / 2 + block.width * 0.46)
                ey = cy - block.height * 0.50 - 20
                frame.alpha_composite(e, (int(ex - e.width / 2), int(max(4, ey - e.height / 2))))
        frame.save(out_dir / f"hook_{i:03d}.png")
    return out_dir


def banner_image(s: dict, out: Path) -> Path:
    """Persistent top label: black text on a bright yellow pill, emoji on the left."""
    text = (s.get("banner") or "").upper()
    f = font(74)
    l, t, r, b = f.getbbox(text)
    emo = emoji_image(s.get("emoji", ""), 84)
    ew = (emo.width + 16) if emo else 0
    px, py = 34, 18
    img = Image.new("RGBA", (r - l + px * 2 + ew, max(b - t, 84) + py * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=26, fill=YELLOW,
                        outline=BLACK, width=5)
    if emo:
        img.alpha_composite(emo, (px - 6, (img.height - emo.height) // 2))
    d.text((px + ew - l, (img.height - (b - t)) // 2 - t), text, font=f, fill=(18, 18, 18))
    _shadowed(img, offset=(4, 8), blur=8).save(out)
    return out
