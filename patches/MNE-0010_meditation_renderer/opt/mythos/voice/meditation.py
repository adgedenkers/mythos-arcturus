"""
Iris Meditation Renderer
========================
Parses a meditation script with pause markup, synthesizes each text segment
using Kokoro TTS, stitches together with silence, and exports OGG Vorbis.

Markup format (plain text, one element per line):
    Spoken text goes here as normal sentences.
    [pause:5]          <- 5 seconds of silence
    [pause:10]         <- 10 seconds of silence
    More spoken text.

File naming:
    meditation_YYYYMMDD_HHMMSS_{slug}.ogg
"""

import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger("iris.voice.meditation")

OUTPUT_DIR = Path("/opt/mythos/public/meditations")
SAMPLE_RATE = 24000  # Kokoro native sample rate
BREATH_GAP = 0.4     # seconds of silence added between speech segments


def slugify(title: str, max_words: int = 4) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    words = title.split()[:max_words]
    return "_".join(words) if words else "meditation"


def parse_script(script: str) -> list:
    """
    Parse meditation script into a list of segment dicts.
    {"type": "speech", "text": "..."} or {"type": "pause", "seconds": N}
    """
    segments = []
    for line in script.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\[pause:(\d+(?:\.\d+)?)\]$", line, re.IGNORECASE)
        if m:
            segments.append({"type": "pause", "seconds": float(m.group(1))})
        else:
            segments.append({"type": "speech", "text": line})
    return segments


def make_silence(seconds: float) -> np.ndarray:
    return np.zeros(int(seconds * SAMPLE_RATE), dtype=np.float32)


def render_meditation(
    script: str,
    title: str = "meditation",
    voice: str = "af_heart",
    output_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """
    Render a meditation script to an OGG file.
    Returns the Path of the output file, or None on failure.
    """
    from voice.tts import synthesize

    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    segments = parse_script(script)
    if not segments:
        logger.error("No segments found in script")
        return None

    n_speech = sum(1 for s in segments if s["type"] == "speech")
    n_pause  = sum(1 for s in segments if s["type"] == "pause")
    t_pause  = sum(s["seconds"] for s in segments if s["type"] == "pause")
    logger.info(f"Rendering: {n_speech} speech, {n_pause} pauses ({t_pause:.0f}s), voice={voice}")

    tts_config = {"voice": voice}
    parts: list = []

    for i, seg in enumerate(segments):
        if seg["type"] == "pause":
            parts.append(make_silence(seg["seconds"]))
            logger.debug(f"  [{i+1}] pause {seg['seconds']}s")
        else:
            text = seg["text"]
            logger.debug(f"  [{i+1}] synth: {text[:60]}")
            audio = synthesize(text, tts_config)
            if audio is None:
                logger.warning(f"  [{i+1}] TTS returned None — using 1s silence")
                parts.append(make_silence(1.0))
            else:
                if hasattr(audio, "numpy"):
                    audio = audio.numpy()
                parts.append(np.asarray(audio, dtype=np.float32))
                parts.append(make_silence(BREATH_GAP))

    if not parts:
        logger.error("No audio parts generated")
        return None

    full_audio = np.concatenate(parts)
    duration = len(full_audio) / SAMPLE_RATE
    logger.info(f"Total duration: {duration:.1f}s ({duration/60:.1f} min)")

    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = slugify(title)
        output_path = output_dir / f"meditation_{ts}_{slug}.ogg"
    else:
        output_path = Path(output_path)

    try:
        import soundfile as sf
        sf.write(str(output_path), full_audio, SAMPLE_RATE, format="OGG", subtype="VORBIS")
        size_kb = output_path.stat().st_size / 1024
        logger.info(f"Written: {output_path} ({size_kb:.0f} KB)")
        return output_path
    except Exception as e:
        logger.error(f"OGG write failed: {e}")
        # WAV fallback
        try:
            wav = output_path.with_suffix(".wav")
            import soundfile as sf
            sf.write(str(wav), full_audio, SAMPLE_RATE)
            logger.warning(f"Fell back to WAV: {wav}")
            return wav
        except Exception as e2:
            logger.error(f"WAV fallback failed: {e2}")
            return None


def estimate_duration(script: str) -> float:
    """Rough duration estimate (seconds) without rendering."""
    segments = parse_script(script)
    total = 0.0
    wps = 130 / 60 * 0.75  # words/sec at slow meditation pace
    for s in segments:
        if s["type"] == "pause":
            total += s["seconds"]
        else:
            total += len(s["text"].split()) / wps + BREATH_GAP
    return total


def list_meditations(output_dir: Optional[Path] = None) -> list:
    """Return metadata dicts for all rendered meditations, newest first."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir = Path(output_dir)
    if not output_dir.exists():
        return []
    results = []
    for f in sorted(output_dir.glob("meditation_*.ogg"), reverse=True):
        stat = f.stat()
        parts = f.stem.split("_", 3)
        title = parts[3].replace("_", " ").title() if len(parts) > 3 else f.stem
        results.append({
            "filename": f.name,
            "path": str(f),
            "title": title,
            "size_kb": round(stat.st_size / 1024),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        })
    return results
