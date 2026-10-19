"""ffmpeg renderer: shots -> concat -> captions + voice + ducked music -> loudness-normalised MP4."""
import os
import subprocess
from pathlib import Path
from typing import List, Optional



from . import config
from .log import log

W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS


def _run(cmd: list, cwd: Optional[Path] = None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr[-800:]}")


def probe_duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def _prep_shot(src: str, out: Path, frames: int, index: int, punch: bool = False):
    """Scale/crop to 1080x1920 with a slow push-in or pull-out, light grade + grain, exact frames.

    punch: the shot starts a new beat -> a quick zoom "punch" in its first frames.
    """
    dur = frames / FPS
    is_photo = src.lower().endswith((".jpg", ".jpeg", ".png"))
    clip_dur = dur + 1 if is_photo else probe_duration(src)
    loop = clip_dur < dur + 0.2
    # Skip the first moments (often fades) and vary the start between reused clips
    offset = 0.0 if loop else min(max(0.0, clip_dur - dur - 0.1), 0.6 + (index % 3) * 1.7)
    # zoompan on a 2x supersampled frame: smooth (no 1px jitter). Per-frame `scale eval=frame`
    # segfaults in ffmpeg 9 when followed by eq/vignette, so don't use that.
    amount = 0.12 if is_photo else 0.07  # stills need a bit more movement
    z = f"1+{amount}*on/{frames}" if index % 2 == 0 else f"{1 + amount}-{amount}*on/{frames}"
    if punch:
        z = f"{z}+if(lt(on,7),0.14*pow(1-on/7,2),0)"
    sw, sh = W * 2, H * 2
    vf = (f"fps={FPS},scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},"
          f"zoompan=z='{z}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s={W}x{H}:fps={FPS},"
          "eq=contrast=1.06:saturation=1.12:brightness=-0.025,vignette=PI/6,"
          "noise=alls=5:allf=t,format=yuv420p")
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if is_photo:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i", src]
    else:
        if loop:
            cmd += ["-stream_loop", "-1"]
        cmd += ["-ss", f"{offset:.2f}", "-i", src]
    cmd += ["-an", "-vf", vf, "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-r", str(FPS), str(out)]
    _run(cmd)


def make_sfx(workdir: Path, events: List[float], length: float) -> Path:
    """Synthetic sound design: low impact + whoosh on the hook, soft whoosh on each new graphic."""
    out = workdir / "sfx.wav"
    whoosh = ("anoisesrc=d=0.5:c=pink:r=48000:a=0.5,highpass=f=300,lowpass=f=4500,"
              "afade=t=in:d=0.28:curve=qsin,afade=t=out:st=0.28:d=0.22")
    boom = "sine=f=52:d=0.6:r=48000,afade=t=in:d=0.005,afade=t=out:st=0.03:d=0.57:curve=exp"
    parts, labels = [], []
    for i, t in enumerate(events):
        ms = max(0, int((t - 0.18) * 1000))  # whoosh peaks just as the graphic lands
        vol = 0.55 if i == 0 else 0.30
        parts.append(f"{whoosh},volume={vol},adelay={ms}|{ms}[w{i}]")
        labels.append(f"[w{i}]")
    parts.append(f"{boom},volume=0.9,adelay=100|100[b]")
    labels.append("[b]")
    graph = ";".join(parts) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest," \
                              "aformat=sample_rates=48000:channel_layouts=stereo"
    _run(["ffmpeg", "-y", "-v", "error", "-filter_complex", graph, "-t", f"{length:.2f}", str(out)])
    return out


def _loudnorm_two_pass(src: Path, dst: Path):
    """Accurate -14 LUFS (YouTube) with linear gain: measure first, then apply."""
    import json
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    stats = json.loads(p.stderr[p.stderr.rindex("{"):p.stderr.rindex("}") + 1])
    af = ("loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
          f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
          f"offset={stats['target_offset']},aresample=48000")
    _run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", af, "-ar", "48000", str(dst)])


def mix_audio(voice_wav: Path, music_path: Optional[str], sfx_events: Optional[List[float]],
              total: float, workdir: Path) -> Path:
    """voice (+ sfx) (+ ducked music) -> exactly `total` seconds -> two-pass loudnorm -> WAV."""
    inputs = ["-i", str(voice_wav)]
    graph = ("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,"
             "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2[vo]")
    last, n = "vo", 1
    if config.SFX_ENABLED and sfx_events:
        inputs += ["-i", str(make_sfx(workdir, sfx_events, total))]
        graph += (f";[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={config.SFX_VOLUME}[sx];"
                  f"[{last}][sx]amix=inputs=2:normalize=0:duration=first[vs]")
        last, n = "vs", n + 1
    graph += f";[{last}]apad=whole_dur={total:.3f}[vp]"
    last = "vp"
    if music_path:
        inputs += ["-stream_loop", "-1", "-i", os.path.abspath(music_path)]
        graph += (f";[{last}]asplit=2[v1][sc];"
                  f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.30,"
                  f"atrim=0:{total:.3f},afade=t=in:d=1.0,afade=t=out:st={max(0, total - 1.8):.2f}:d=1.8[m];"
                  "[m][sc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[md];"
                  "[v1][md]amix=inputs=2:normalize=0:duration=first[mx]")
        last = "mx"
    mixed = workdir / "mix.wav"
    _run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", f"[{last}]",
          "-t", f"{total:.3f}", "-ar", "48000", str(mixed)])
    final = workdir / "final_audio.wav"
    _loudnorm_two_pass(mixed, final)
    return final


def check_audio(video: Path, total: float):
    """Fail loudly if the muxed audio has holes or the wrong length (never ship cut-off speech)."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_packets",
                          "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True).stdout.splitlines()
    pts = []
    for line in out:  # lines look like "1.234" or "-0.021,Skip"
        try:
            pts.append(float(line.split(",")[0]))
        except ValueError:
            continue
    gaps = [(a, b) for a, b in zip(pts, pts[1:]) if b - a > 0.08]
    if gaps or not pts or abs(pts[-1] - total) > 0.3:
        raise RuntimeError(f"audio check failed: {len(gaps)} gap(s) {gaps[:3]}, ends at "
                           f"{pts[-1] if pts else 0:.2f}s of {total:.2f}s")


def render(plan: List[List[dict]], timings: List[tuple], voice_wav: Path, ass_path: Optional[Path],
           music_path: Optional[str], out_mp4: Path, workdir: Path,
           overlay: Optional[Path] = None, sfx_events: Optional[List[float]] = None):
    total = timings[-1][1]
    shots_dir = workdir / "shots"
    shots_dir.mkdir(exist_ok=True)

    # Frame-exact shot boundaries so picture cuts stay in sync with the narration
    entries, t = [], 0.0
    for (start, end), shots in zip(timings, plan):
        for k, s in enumerate(shots):
            t_end = min(end, t + s["duration"]) if s is not shots[-1] else end
            entries.append((s["path"], round(t * FPS), round(t_end * FPS), k == 0))
            t = t_end
    concat_lines = []
    for i, (src, f0, f1, beat_start) in enumerate(entries):
        out = shots_dir / f"shot_{i:02d}.mp4"
        _prep_shot(src, out, max(1, f1 - f0), i, punch=beat_start and i > 0)
        concat_lines.append(f"file '{out.name}'")
    (shots_dir / "list.txt").write_text("\n".join(concat_lines), encoding="utf-8")
    log(f"[render] {len(entries)} shots prepared")

    # Audio is built in its own pass into one finished WAV. Doing loudnorm/amix inside the
    # video command made ffmpeg drop ~3 s chunks of narration (gaps in the audio stream).
    final_audio = mix_audio(voice_wav, music_path, sfx_events, total, workdir)

    inputs = ["-f", "concat", "-safe", "0", "-i", "shots/list.txt", "-i", final_audio.name]
    n = 2
    video = "[0:v]null[v0]"
    if ass_path:
        fonts_rel = os.path.relpath(config.FONTS_DIR, workdir).replace("\\", "/")
        video = f"[0:v]ass={ass_path.name}:fontsdir={fonts_rel}[v0]"
    if overlay:
        rel = os.path.relpath(overlay, workdir).replace("\\", "/")
        inputs += ["-f", "concat", "-safe", "0", "-i", rel]
        video += f";[{n}:v]format=rgba[ov];[v0][ov]overlay=eof_action=pass:format=auto[vp]"
        n += 1
    else:
        video += ";[v0]null[vp]"
    # thin yellow progress bar along the top edge
    video += f";[vp]drawbox=x=0:y=0:w='max(6,iw*t/{total:.3f})':h=12:color=0xFFD400@0.95:t=fill[v]"
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", video,
           "-map", "[v]", "-map", "1:a", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out_mp4.name]
    _run(cmd, cwd=workdir)
    check_audio(workdir / out_mp4.name, total)
    log(f"[render] {out_mp4} ({total:.1f}s)")
