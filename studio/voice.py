"""Narration: Gemini TTS (natural voice) -> cleanup -> word timestamps via Groq Whisper."""
import asyncio
import base64
import os
import re
import shutil
import subprocess
import time
import wave
from pathlib import Path
from typing import List, Tuple

import requests

from . import config
from .log import log

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# Slightly faster than natural read speed suits Shorts pacing
TEMPO = 1.07
# Above this, a take sounds choppy ("putus-putus") and the next TTS model is tried
MAX_DROPOUTS_PER_MIN = 6


def dropouts_per_minute(wav: Path) -> float:
    """Count abrupt loud->silent->loud cuts shorter than 150 ms (clipped words), per minute."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    if len(a) < 16000:
        return 0.0
    win = 160  # 10 ms
    rms = np.sqrt(np.mean(a[: len(a) // win * win].reshape(-1, win) ** 2, axis=1))
    db = 20 * np.log10(rms + 1e-6)
    voiced = db[db > -60]
    if not len(voiced):
        return 0.0
    loud = db > (np.percentile(voiced, 60) - 8)
    n, i = 0, 0
    while i < len(db) - 20:
        if loud[i] and db[i + 2] < -45:
            j = i + 2
            while j < len(db) and db[j] < -45:
                j += 1
            if j - i <= 15 and j < len(db) - 1 and loud[j + 1]:
                n += 1
            i = j
        i += 1
    return n / (len(a) / 16000 / 60)


def _tts_prompt(model: str, text: str) -> str:
    if model.startswith("gemini-2.5"):
        return f"Say in a {config.TTS_STYLE} voice: {text}"
    return f"[{config.TTS_STYLE}] {text}"


def _gemini_tts(model: str, text: str, voice: str, out_wav: Path):
    key = os.environ.get("GEMINI_API_KEY")
    r = requests.post(GEMINI_URL.format(model), params={"key": key}, timeout=300, json={
        "contents": [{"parts": [{"text": _tts_prompt(model, text)}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}})
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code} {r.text[:120]}")
    part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    data = base64.b64decode(part["data"])
    if data[:4] == b"RIFF":
        out_wav.write_bytes(data)
    else:
        rate = int((re.search(r"rate=(\d+)", part.get("mimeType", "")) or [None, 24000])[1])
        with wave.open(str(out_wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(data)


def _edge_tts(text: str, voice: str, out_wav: Path):
    import edge_tts
    mp3 = out_wav.with_suffix(".edge.mp3")
    asyncio.run(edge_tts.Communicate(text, voice, rate="+5%").save(str(mp3)))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), str(out_wav)], check=True)


def transcribe(wav: Path, lang: str) -> List[dict]:
    """Word-level timestamps [{word, start, end}] from Groq Whisper."""
    key = os.environ.get("GROQ_API_KEY")
    for attempt in range(3):
        with open(wav, "rb") as f:
            r = requests.post(WHISPER_URL, headers={"Authorization": f"Bearer {key}"},
                              files={"file": (wav.name, f, "audio/wav")},
                              data={"model": "whisper-large-v3-turbo", "language": lang,
                                    "response_format": "verbose_json",
                                    "timestamp_granularities[]": "word"}, timeout=180)
        if r.ok:
            words = [{"word": w["word"].strip(), "start": float(w["start"]), "end": float(w["end"])}
                     for w in r.json().get("words", []) if w.get("word", "").strip()]
            return words
        log(f"[voice] whisper HTTP {r.status_code}, retrying")
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Whisper failed: {r.status_code} {r.text[:150]}")


def _norm(w: str) -> str:
    return re.sub(r"[^\w]", "", w.lower())


def _leaked_prefix_end(words: List[dict], script_text: str) -> float:
    """If the TTS read the style tag aloud, return where the real script starts (else 0)."""
    first = [_norm(w) for w in script_text.split()[:3]]
    heard = [_norm(w["word"]) for w in words]
    for i in range(min(len(heard), 25)):
        if heard[i:i + 2] == first[:2]:
            return words[i]["start"] - 0.05 if i > 0 else 0.0
    return 0.0


def make_voice(text: str, lang: str, workdir: Path) -> Tuple[Path, List[dict]]:
    """Synthesize narration. Returns (clean 48k wav, word timestamps)."""
    settings = config.LANGUAGES[lang]
    raw = workdir / "voice_raw.wav"
    # Gemini TTS sometimes glitches (words cut off mid-sound), the 3.x models much more than 2.5.
    # Measure dropouts and move on to the next model when a take is choppy; keep the cleanest.
    used, best_rate = None, None
    # TTS is random: a second take of the best model usually beats switching to a worse one
    attempts = [config.TTS_MODELS[0]] + list(config.TTS_MODELS)
    for n, model in enumerate(attempts):
        take = workdir / f"take_{n}_{model}.wav"
        try:
            _gemini_tts(model, text, settings["voice"], take)
        except Exception as e:
            log(f"[voice] {model} failed: {str(e)[:100]}")
            continue
        rate = dropouts_per_minute(take)
        log(f"[voice] {model}: {rate:.1f} dropouts/min")
        if best_rate is None or rate < best_rate:
            best_rate, used = rate, model
            shutil.copyfile(take, raw)
        if rate <= MAX_DROPOUTS_PER_MIN:
            break
    if not used or best_rate > MAX_DROPOUTS_PER_MIN * 3:
        log("[voice] no clean Gemini take, using Edge TTS")
        _edge_tts(text, settings["edge_voice"], raw)
        used = "edge-tts"
    log(f"[voice:{lang}] synthesized with {used}")

    # Check the style tag wasn't read aloud
    start = 0.0
    if used != "edge-tts":
        start = _leaked_prefix_end(transcribe(raw, lang), text)
        if start > 0:
            log(f"[voice] trimming {start:.2f}s of leaked style instructions")

    # Trim, tempo, trailing silence cleanup, 48 kHz
    clean = workdir / "voice.wav"
    af = (f"atrim=start={start:.3f},asetpts=PTS-STARTPTS,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
          f"atempo={TEMPO},"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse,"
          "highpass=f=70,aresample=48000")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", af, "-ac", "1", str(clean)],
                   check=True)
    words = transcribe(clean, lang)
    if not words:
        raise RuntimeError("Whisper returned no words")
    log(f"[voice:{lang}] {words[-1]['end']:.1f}s, {len(words)} words timed")
    return clean, words
