"""End-to-end: one topic -> one finished Short per language, in a tidy output folder."""
import json
import re
import shutil
import time
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from . import captions, config, fonts, graphics, motion, music, research, script, topics, visuals, voice
from .log import log
from .render import render


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "video"


def _hook_lines(hook_title: str) -> list:
    """'GYM INI UNTUNG KALAU *KAMU BOLOS*' -> ['GYM INI UNTUNG KALAU', '*KAMU BOLOS*']"""
    if "*" in hook_title:
        head, _, rest = hook_title.partition("*")
        key = rest.split("*")[0]
        lines = [head.strip()] if head.strip() else []
        return lines + [f"*{key.strip()}*"]
    words = hook_title.split()
    return [" ".join(words[:-2]), "*" + " ".join(words[-2:]) + "*"] if len(words) > 2 else [f"*{hook_title}*"]


def _narration(s: dict) -> str:
    return " ".join(b["text"].strip() for b in s["beats"])


def make_video(topic_hint: Optional[str] = None, langs: Iterable[str] = ("en", "id"),
               keep_work: bool = False) -> Path:
    t0 = time.time()
    fonts.ensure_fonts()
    langs = [l for l in langs if l in config.LANGUAGES]

    topic = topics.pick_topic(topic_hint)
    src = research.research(topic["company"], topic.get("wikipedia_title"))
    if len(src["text"]) < 1500:
        raise RuntimeError(f"Not enough source material for {topic['company']} - try another topic")

    topic = script.ground_angle(topic, src["text"])
    script_en = script.write_english(topic, src["text"])
    scripts = {"en": script_en}
    if "id" in langs:
        scripts["id"] = script.adapt_indonesian(script_en)

    folder = config.OUTPUT_DIR / f"{date.today().isoformat()}_{_slug(topic['company'] + ' ' + script_en['title'])}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "topic.json").write_text(json.dumps({"topic": topic, "sources": src["sources"]},
                                                  indent=2, ensure_ascii=False), encoding="utf-8")

    # Footage is chosen once (from the English beats) and reused for every language
    candidates = visuals.gather_candidates(script_en["beats"], script_en.get("setting_queries", []))
    ranked = visuals.rank_with_vision(script_en["beats"], candidates, topic["company"])
    ranked = visuals.rescue_empty_beats(script_en["beats"], ranked, script_en.get("setting_queries", []),
                                        topic["company"])
    track = music.pick(script_en.get("music_mood", "documentary"))

    for lang in langs:
        s = scripts[lang]
        out_dir = folder / lang
        work = out_dir / "work"
        work.mkdir(parents=True, exist_ok=True)
        log(f"===== {lang.upper()}: {s['title']}")

        voice_wav, words = voice.make_voice(_narration(s), lang, work)
        timings = captions.beat_times(s["beats"], words)
        ass = None
        if config.KARAOKE_CAPTIONS:
            ass = work / "captions.ass"
            captions.build_ass(words, "", ass, timings[-1][1])
        # Kinetic graphics (headlines, stats, number tags, bubbles...) as one overlay track
        if s["beats"] and s.get("hook_title"):
            s["beats"][0]["screen"] = {"type": "headline", "lines": _hook_lines(s["hook_title"])}
        overlay = motion.build_overlay(s["beats"], timings, words, work / "motion")

        plan = visuals.assign_shots(s["beats"], ranked, timings)
        visuals.download_plan(plan)

        video = out_dir / "video.mp4"
        tmp_video = work / "video.mp4"
        render(plan, timings, voice_wav, ass, track, tmp_video, work,
               overlay=overlay, sfx_events=motion.element_entries(s["beats"], timings))
        shutil.move(str(tmp_video), video)
        # Thumbnail frames only from clips the vision model rated on-topic
        good = lambda sh: sh["clip"].get("score", 6) >= 6
        top_clips = [sh["path"] for sh in plan[0] if good(sh)] or [plan[0][0]["path"]]
        half = len(plan) // 2
        bottom_clips = [sh["path"] for beat in plan[half:] for sh in beat if good(sh)]
        bottom_clips += [sh["path"] for beat in plan[1:half] for sh in beat if good(sh)]
        graphics.make_thumbnail(top_clips, bottom_clips, s, out_dir / "thumbnail.jpg", work)

        meta = {
            "language": lang, "title": s["title"], "description": s.get("description", ""),
            "on_screen": {k: s.get(k, "") for k in ("hook_title", "banner", "thumb_text", "thumb_badge",
                                                     "emoji", "thumb_template", "split_top", "split_bottom",
                                                     "thumb_focus")},
            "hashtags": s.get("hashtags", []), "duration": round(timings[-1][1], 2),
            "narration": _narration(s), "beats": s["beats"], "facts_used": s.get("facts_used", []),
            "sources": src["sources"], "music": track,
            "footage": [{"pixabay_id": sh["clip"]["id"], "query": sh["clip"].get("query")}
                        for beat in plan for sh in beat],
        }
        visuals.remember_used([sh["clip"]["id"] for beat in plan for sh in beat])
        (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        if not keep_work:
            shutil.rmtree(work, ignore_errors=True)

    topics.save_history({"company": topic["company"], "angle": topic.get("angle", ""),
                         "title": script_en["title"], "folder": folder.name})
    log(f"DONE in {(time.time() - t0) / 60:.1f} min -> {folder}")
    return folder
