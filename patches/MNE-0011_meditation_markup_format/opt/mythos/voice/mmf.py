"""
Iris Meditation Markup Format (MMF) Renderer
=============================================
Parses a .yaml meditation spec and renders it to OGG audio using Kokoro TTS.

Spec structure:
    meditation:
      title, slug, author, description, version, created
      defaults:
        voice, speed, output_format, sample_rate, breath_gap
      phases:
        - id, label, speed (default for all segments), tone (metadata only)
          segments:
            - type: speech | pause
              text: "..."        (speech only)
              seconds: N         (pause only)
              speed: 0.75        (optional segment-level override)

Speed values:
    1.0  = normal conversational pace
    0.85 = gentle, slightly slowed
    0.80 = meditation default
    0.72 = suspended, superposition quality
    0.65 = very slow, deep work
    0.60 = anchor moments only

Tone field (metadata — stored, not yet acted on by Kokoro):
    warm_grounding, suspended, direct, gentle, anchoring, returning
    These are logged and included in the render manifest for future SSML export.

Output:
    /opt/mythos/public/meditations/{slug}.ogg
    /opt/mythos/public/meditations/scripts/{slug}.render.json  (manifest)
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

logger = logging.getLogger("iris.voice.mmf")

SCRIPTS_DIR  = Path("/opt/mythos/public/meditations/scripts")
OUTPUT_DIR   = Path("/opt/mythos/public/meditations")
SAMPLE_RATE  = 24000


# ---------------------------------------------------------------------------
# Schema / parsing
# ---------------------------------------------------------------------------

def load_spec(path: str | Path) -> dict:
    """Load and validate a .yaml meditation spec. Returns the meditation dict."""
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
    required = ["title", "phases"]
    for k in required:
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
                raise ValueError(f"Phase {i}, segment {j} is speech but missing 'text'")
            if seg["type"] == "pause" and "seconds" not in seg:
                raise ValueError(f"Phase {i}, segment {j} is pause but missing 'seconds'")


def flatten_segments(spec: dict) -> list[dict]:
    """
    Flatten phases → segments into a single list, resolving speed inheritance.
    Each segment gets:
        type, text/seconds, speed (resolved), phase_id, phase_label, tone
    """
    defaults = spec.get("defaults", {})
    default_speed     = float(defaults.get("speed", 0.82))
    default_breath    = float(defaults.get("breath_gap", 0.4))
    default_voice     = defaults.get("voice", "af_heart")

    flat = []
    for phase in spec["phases"]:
        phase_speed = float(phase.get("speed", default_speed))
        phase_tone  = phase.get("tone", "neutral")
        phase_id    = phase.get("id", "unknown")
        phase_label = phase.get("label", phase_id)

        for seg in phase["segments"]:
            seg_speed = float(seg.get("speed", phase_speed))
            entry = {
                "type":        seg["type"],
                "phase_id":    phase_id,
                "phase_label": phase_label,
                "tone":        phase_tone,
                "speed":       seg_speed,
                "breath_gap":  default_breath,
                "voice":       seg.get("voice", default_voice),
            }
            if seg["type"] == "speech":
                entry["text"] = seg["text"]
            elif seg["type"] == "pause":
                entry["seconds"] = float(seg["seconds"])
            flat.append(entry)

    return flat


# ---------------------------------------------------------------------------
# Synthesis helpers
# ---------------------------------------------------------------------------

def make_silence(seconds: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


def synth_segment(text: str, voice: str, speed: float) -> Optional[np.ndarray]:
    """
    Synthesize one speech segment. Speed is passed to Kokoro via the pipeline
    speed parameter (supported in kokoro >= 0.8).
    Falls back to default speed if speed param unsupported.
    """
    from voice.pronunciations import apply
    from voice.tts import get_pipeline

    text = apply(text)
    if not text.strip():
        return None

    pipe = get_pipeline()
    try:
        segments = []
        # Kokoro KPipeline accepts speed= kwarg
        for _gs, _ps, audio in pipe(text, voice=voice, speed=speed):
            segments.append(audio)
        if not segments:
            return None
        audio = np.concatenate(segments) if len(segments) > 1 else segments[0]
        if hasattr(audio, "numpy"):
            audio = audio.numpy()
        return np.asarray(audio, dtype=np.float32)
    except TypeError:
        # Older kokoro that doesn't accept speed=
        logger.warning("Kokoro doesn't support speed= kwarg, using default rate")
        try:
            segments = []
            for _gs, _ps, audio in pipe(text, voice=voice):
                segments.append(audio)
            if not segments:
                return None
            audio = np.concatenate(segments) if len(segments) > 1 else segments[0]
            if hasattr(audio, "numpy"):
                audio = audio.numpy()
            return np.asarray(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render_spec(
    spec_path: str | Path,
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """
    Full render pipeline for a .yaml MMF spec.
    Returns path to rendered OGG file, or None on failure.
    """
    spec_path = Path(spec_path)
    spec = load_spec(spec_path)

    defaults    = spec.get("defaults", {})
    title       = spec.get("title", "Untitled Meditation")
    slug        = spec.get("slug") or _slugify(title)
    voice       = defaults.get("voice", "af_heart")
    sample_rate = int(defaults.get("sample_rate", SAMPLE_RATE))

    segments = flatten_segments(spec)

    n_speech = sum(1 for s in segments if s["type"] == "speech")
    n_pause  = sum(1 for s in segments if s["type"] == "pause")
    t_pause  = sum(s["seconds"] for s in segments if s["type"] == "pause")
    logger.info(f"MMF render: '{title}' | {n_speech} speech, {n_pause} pauses ({t_pause:.0f}s silence)")

    # Log unique speeds in use
    speeds = sorted(set(s["speed"] for s in segments if s["type"] == "speech"))
    logger.info(f"Speed range: {speeds}")

    parts: list[np.ndarray] = []
    manifest_segments = []

    for i, seg in enumerate(segments):
        if seg["type"] == "pause":
            silence = make_silence(seg["seconds"], sample_rate)
            parts.append(silence)
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
                logger.warning(f"  [{i+1:03d}] TTS None — inserting 0.8s silence")
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
    logger.info(f"Total rendered duration: {total_dur:.1f}s ({total_dur/60:.1f} min)")

    # Output path
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"meditation_{ts}_{slug}.ogg"
    output_path = Path(output_path)

    # Write OGG
    try:
        import soundfile as sf
        sf.write(str(output_path), full_audio, sample_rate, format="OGG", subtype="VORBIS")
        size_kb = output_path.stat().st_size / 1024
        logger.info(f"Written: {output_path} ({size_kb:.0f} KB)")
    except Exception as e:
        logger.error(f"OGG write failed: {e}")
        return None

    # Write render manifest
    _write_manifest(spec, slug, output_path, total_dur, manifest_segments, spec_path)

    return output_path


def _write_manifest(spec, slug, output_path, total_dur, manifest_segments, spec_path):
    """Write a .render.json manifest next to the spec file."""
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "title":        spec.get("title"),
        "slug":         slug,
        "author":       spec.get("author", "unknown"),
        "rendered_at":  datetime.now().isoformat(),
        "source_spec":  str(spec_path),
        "output_file":  str(output_path),
        "total_duration_s": round(total_dur, 1),
        "total_duration_min": round(total_dur / 60, 1),
        "phases": [
            {
                "id":    p.get("id"),
                "label": p.get("label"),
                "tone":  p.get("tone"),
                "speed": p.get("speed"),
            }
            for p in spec.get("phases", [])
        ],
        "segments": manifest_segments,
    }
    manifest_path = SCRIPTS_DIR / f"{slug}.render.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Manifest: {manifest_path}")


# ---------------------------------------------------------------------------
# Estimation (no synthesis)
# ---------------------------------------------------------------------------

def estimate_spec(spec_path: str | Path) -> dict:
    """Estimate duration from a spec without rendering."""
    spec = load_spec(spec_path)
    segments = flatten_segments(spec)

    t_pause  = sum(s["seconds"] for s in segments if s["type"] == "pause")
    n_speech = sum(1 for s in segments if s["type"] == "speech")
    n_pause  = sum(1 for s in segments if s["type"] == "pause")

    # Speech timing: words / (130wpm * speed) + breath_gap
    t_speech = 0.0
    for s in segments:
        if s["type"] == "speech":
            wps = (130 / 60) * s["speed"]
            t_speech += len(s["text"].split()) / wps + s["breath_gap"]

    total = t_pause + t_speech
    return {
        "title":          spec.get("title"),
        "n_speech":       n_speech,
        "n_pause":        n_pause,
        "t_pause_s":      round(t_pause),
        "t_speech_s":     round(t_speech),
        "total_s":        round(total),
        "total_min":      round(total / 60, 1),
        "phases":         [p.get("label", p.get("id")) for p in spec.get("phases", [])],
        "speed_range":    sorted(set(s["speed"] for s in segments if s["type"] == "speech")),
    }


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _slugify(title: str, max_words: int = 5) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    return "_".join(title.split()[:max_words])


def spec_to_txt(spec_path: str | Path) -> str:
    """Export a .yaml spec back to the flat .txt format (for debugging)."""
    spec = load_spec(spec_path)
    segments = flatten_segments(spec)
    lines = []
    for seg in segments:
        if seg["type"] == "speech":
            lines.append(seg["text"])
        elif seg["type"] == "pause":
            lines.append(f"[pause:{int(seg['seconds'])}]")
    return "\n".join(lines)
