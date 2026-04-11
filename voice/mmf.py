"""
Iris Meditation Markup Format (MMF) Renderer
MNE-0014: Fixed _mix_background to use -stream_loop -1 instead of aloop filter.
"""
import os
import re
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

logger = logging.getLogger("iris.voice.mmf")

SCRIPTS_DIR = Path("/opt/mythos/public/meditations/scripts")
OUTPUT_DIR  = Path("/opt/mythos/public/meditations")
MUSIC_DIR   = Path("/opt/mythos/public/meditations/music")
CONFIG_PATH = Path("/opt/mythos/voice/meditation_config.yaml")
SAMPLE_RATE = 24000


def load_global_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_background(spec_defaults: dict, global_cfg: dict) -> Optional[dict]:
    global_bg = global_cfg.get("background", {}) or {}
    spec_bg   = spec_defaults.get("background", {}) or {}
    merged    = {**global_bg, **spec_bg}
    track_name = merged.get("track")
    if not track_name:
        return None
    music_dir  = Path(global_cfg.get("music_dir", str(MUSIC_DIR)))
    track_path = music_dir / track_name
    if not track_path.exists():
        logger.warning(f"Background track not found: {track_path} -- skipping music")
        return None
    return {
        "track_path": track_path,
        "volume":     float(merged.get("volume", 0.22)),
        "fade_in":    float(merged.get("fade_in", 3.0)),
        "fade_out":   float(merged.get("fade_out", 5.0)),
    }


def load_spec(path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Spec not found: {path}")
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if "meditation" not in raw:
        raise ValueError("YAML must have a top-level 'meditation' key")
    spec = raw["meditation"]
    _validate(spec)
    return spec


def _validate(spec: dict):
    for k in ["title", "phases"]:
        if k not in spec:
            raise ValueError(f"Meditation spec missing required key: '{k}'")
    if not isinstance(spec["phases"], list) or len(spec["phases"]) == 0:
        raise ValueError("'phases' must be a non-empty list")
    for i, phase in enumerate(spec["phases"]):
        if "segments" not in phase:
            raise ValueError(f"Phase {i} missing 'segments'")
        for j, seg in enumerate(phase["segments"]):
            if "type" not in seg:
                raise ValueError(f"Phase {i}, segment {j} missing 'type'")
            if seg["type"] == "speech" and "text" not in seg:
                raise ValueError(f"Phase {i}, segment {j} speech missing 'text'")
            if seg["type"] == "pause" and "seconds" not in seg:
                raise ValueError(f"Phase {i}, segment {j} pause missing 'seconds'")


def flatten_segments(spec: dict) -> list:
    defaults       = spec.get("defaults", {})
    default_speed  = float(defaults.get("speed", 0.82))
    default_breath = float(defaults.get("breath_gap", 0.4))
    default_voice  = defaults.get("voice", "af_heart")
    flat = []
    for phase in spec["phases"]:
        phase_speed = float(phase.get("speed", default_speed))
        phase_tone  = phase.get("tone", "neutral")
        phase_id    = phase.get("id", "unknown")
        phase_label = phase.get("label", phase_id)
        for seg in phase["segments"]:
            entry = {
                "type":        seg["type"],
                "phase_id":    phase_id,
                "phase_label": phase_label,
                "tone":        phase_tone,
                "speed":       float(seg.get("speed", phase_speed)),
                "breath_gap":  default_breath,
                "voice":       seg.get("voice", default_voice),
            }
            if seg["type"] == "speech":
                entry["text"] = seg["text"]
            elif seg["type"] == "pause":
                entry["seconds"] = float(seg["seconds"])
            flat.append(entry)
    return flat


def make_silence(seconds: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


def synth_segment(text: str, voice: str, speed: float) -> Optional[np.ndarray]:
    from voice.pronunciations import apply
    from voice.tts import get_pipeline
    text = apply(text)
    if not text.strip():
        return None
    pipe = get_pipeline()
    try:
        parts = []
        for _gs, _ps, audio in pipe(text, voice=voice, speed=speed):
            parts.append(audio)
        if not parts:
            return None
        audio = np.concatenate(parts) if len(parts) > 1 else parts[0]
        if hasattr(audio, "numpy"):
            audio = audio.numpy()
        return np.asarray(audio, dtype=np.float32)
    except TypeError:
        logger.warning("Kokoro speed= kwarg unsupported, using default rate")
        try:
            parts = []
            for _gs, _ps, audio in pipe(text, voice=voice):
                parts.append(audio)
            if not parts:
                return None
            audio = np.concatenate(parts) if len(parts) > 1 else parts[0]
            if hasattr(audio, "numpy"):
                audio = audio.numpy()
            return np.asarray(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return None


def _wav_to_ogg(wav_path: str, ogg_path: str) -> bool:
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path,
         "-c:a", "libvorbis", "-q:a", "4", ogg_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logger.error(f"ffmpeg WAV->OGG failed:\n{result.stderr[-800:]}")
        return False
    return True


def _mix_background(voice_wav: str, bg: dict, ogg_path: str) -> bool:
    """
    Mix voice WAV with background track using ffmpeg.
    Uses -stream_loop -1 to loop at container level -- avoids timestamp
    issues with high-sample-rate OGG files (e.g. 96000 Hz stereo).
    Resamples background to mono 24000 Hz to match voice track.
    """
    track    = str(bg["track_path"])
    volume   = bg["volume"]
    fade_in  = bg["fade_in"]
    fade_out = bg["fade_out"]

    result = subprocess.run(
        ["ffmpeg", "-y",
         "-i", voice_wav,
         "-stream_loop", "-1", "-i", track,
         "-filter_complex",
         f"[1:a]aresample=24000,aformat=channel_layouts=mono,volume={volume},"
         f"afade=t=in:st=0:d={fade_in}[bg];"
         f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition={fade_out}[out]",
         "-map", "[out]",
         "-c:a", "libvorbis", "-q:a", "4",
         ogg_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logger.error(f"ffmpeg mix failed:\n{result.stderr[-800:]}")
        return False
    return True


def render_spec(spec_path, output_path: Optional[Path] = None) -> Optional[Path]:
    spec_path  = Path(spec_path)
    spec       = load_spec(spec_path)
    global_cfg = load_global_config()
    defaults    = spec.get("defaults", {})
    title       = spec.get("title", "Untitled Meditation")
    slug        = spec.get("slug") or _slugify(title)
    sample_rate = int(defaults.get("sample_rate", SAMPLE_RATE))
    segments = flatten_segments(spec)
    n_speech = sum(1 for s in segments if s["type"] == "speech")
    n_pause  = sum(1 for s in segments if s["type"] == "pause")
    t_pause  = sum(s["seconds"] for s in segments if s["type"] == "pause")
    speeds   = sorted(set(s["speed"] for s in segments if s["type"] == "speech"))
    logger.info(f"MMF render: '{title}' | {n_speech} speech, {n_pause} pauses ({t_pause:.0f}s)")
    logger.info(f"Speed range: {speeds}")
    bg = resolve_background(defaults, global_cfg)
    if bg:
        logger.info(f"Background: {bg['track_path'].name} vol={bg['volume']} "
                    f"fade_in={bg['fade_in']}s fade_out={bg['fade_out']}s")
    else:
        logger.info("Background: none")
    parts: list = []
    manifest_segments = []
    for i, seg in enumerate(segments):
        if seg["type"] == "pause":
            parts.append(make_silence(seg["seconds"], sample_rate))
            manifest_segments.append({
                "index": i, "type": "pause",
                "seconds": seg["seconds"],
                "phase": seg["phase_id"], "tone": seg["tone"],
            })
            logger.debug(f"  [{i+1:03d}] pause {seg['seconds']}s [{seg['phase_id']}]")
        elif seg["type"] == "speech":
            text = seg["text"]
            spd  = seg["speed"]
            v    = seg["voice"]
            logger.debug(f"  [{i+1:03d}] synth speed={spd} [{seg['phase_id']}] '{text[:50]}'")
            audio = synth_segment(text, v, spd)
            if audio is None:
                logger.warning(f"  [{i+1:03d}] TTS None -- inserting silence")
                parts.append(make_silence(0.8, sample_rate))
                manifest_segments.append({
                    "index": i, "type": "speech_failed",
                    "text": text, "phase": seg["phase_id"],
                })
            else:
                dur = len(audio) / sample_rate
                parts.append(audio)
                parts.append(make_silence(seg["breath_gap"], sample_rate))
                manifest_segments.append({
                    "index": i, "type": "speech",
                    "text": text, "speed": spd,
                    "phase": seg["phase_id"], "tone": seg["tone"],
                    "duration_s": round(dur, 2),
                })
    if not parts:
        logger.error("No audio parts generated")
        return None
    full_audio = np.concatenate(parts)
    total_dur  = len(full_audio) / sample_rate
    logger.info(f"Total synthesized: {total_dur:.1f}s ({total_dur/60:.1f} min)")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"meditation_{ts}_{slug}.ogg"
    output_path = Path(output_path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    try:
        import soundfile as sf
        sf.write(wav_path, full_audio, sample_rate)
        wav_size = Path(wav_path).stat().st_size // 1024
        logger.info(f"WAV written: {wav_size} KB -> converting to OGG via ffmpeg")
    except Exception as e:
        logger.error(f"WAV write failed: {e}")
        _safe_unlink(wav_path)
        return None
    try:
        if bg:
            success = _mix_background(wav_path, bg, str(output_path))
        else:
            success = _wav_to_ogg(wav_path, str(output_path))
        if not success:
            return None
        size_kb = output_path.stat().st_size / 1024
        logger.info(f"Written: {output_path} ({size_kb:.0f} KB)")
    finally:
        _safe_unlink(wav_path)
    _write_manifest(spec, slug, output_path, total_dur, manifest_segments, spec_path, bg)
    return output_path


def _safe_unlink(path: str):
    try:
        os.unlink(path)
    except Exception:
        pass


def _write_manifest(spec, slug, output_path, total_dur, manifest_segments, spec_path, bg):
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "title":              spec.get("title"),
        "slug":               slug,
        "author":             spec.get("author", "unknown"),
        "rendered_at":        datetime.now().isoformat(),
        "source_spec":        str(spec_path),
        "output_file":        str(output_path),
        "total_duration_s":   round(total_dur, 1),
        "total_duration_min": round(total_dur / 60, 1),
        "background": {
            "track":    str(bg["track_path"].name) if bg else None,
            "volume":   bg["volume"] if bg else None,
            "fade_in":  bg["fade_in"] if bg else None,
            "fade_out": bg["fade_out"] if bg else None,
        },
        "phases": [
            {"id": p.get("id"), "label": p.get("label"),
             "tone": p.get("tone"), "speed": p.get("speed")}
            for p in spec.get("phases", [])
        ],
        "segments": manifest_segments,
    }
    manifest_path = SCRIPTS_DIR / f"{slug}.render.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Manifest: {manifest_path}")


def estimate_spec(spec_path) -> dict:
    spec     = load_spec(spec_path)
    segments = flatten_segments(spec)
    t_pause  = sum(s["seconds"] for s in segments if s["type"] == "pause")
    n_speech = sum(1 for s in segments if s["type"] == "speech")
    n_pause  = sum(1 for s in segments if s["type"] == "pause")
    t_speech = 0.0
    for s in segments:
        if s["type"] == "speech":
            wps = (130 / 60) * s["speed"]
            t_speech += len(s["text"].split()) / wps + s["breath_gap"]
    total = t_pause + t_speech
    global_cfg = load_global_config()
    bg = resolve_background(spec.get("defaults", {}), global_cfg)
    return {
        "title":       spec.get("title"),
        "n_speech":    n_speech,
        "n_pause":     n_pause,
        "t_pause_s":   round(t_pause),
        "t_speech_s":  round(t_speech),
        "total_s":     round(total),
        "total_min":   round(total / 60, 1),
        "phases":      [p.get("label", p.get("id")) for p in spec.get("phases", [])],
        "speed_range": sorted(set(s["speed"] for s in segments if s["type"] == "speech")),
        "background":  bg["track_path"].name if bg else None,
    }


def _slugify(title: str, max_words: int = 5) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    return "_".join(title.split()[:max_words])


def spec_to_txt(spec_path) -> str:
    spec     = load_spec(spec_path)
    segments = flatten_segments(spec)
    lines    = []
    for seg in segments:
        if seg["type"] == "speech":
            lines.append(seg["text"])
        elif seg["type"] == "pause":
            lines.append(f"[pause:{int(seg['seconds'])}]")
    return "\n".join(lines)
