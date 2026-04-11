#!/usr/bin/env python3
"""
Diarized Transcription Service for Mythos

Extends the base TranscriptionService with speaker diarization via pyannote.audio.
Produces transcripts with speaker labels and timestamps.

Falls back to transcription-only if pyannote is not available or no HuggingFace token.

Usage:
    from services.diarized_transcription import DiarizedTranscriptionService

    dts = DiarizedTranscriptionService()
    result = dts.transcribe_with_diarization("/path/to/audio.m4a")
    # result = {
    #     "text": "full transcript",
    #     "segments": [...],
    #     "speakers": {"SPEAKER_00": {...}, "SPEAKER_01": {...}},
    #     "diarized_segments": [
    #         {"speaker": "SPEAKER_00", "start": 0.0, "end": 2.5, "text": "..."},
    #         ...
    #     ],
    #     "diarized": True,
    #     "language": "en",
    #     "duration": 1234.5
    # }
"""

import os
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Model config
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "large-v3")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "float16")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")


class DiarizedTranscriptionService:
    """
    GPU-accelerated speech-to-text with speaker diarization.

    Lazy-loads both whisper and pyannote models on first use.
    Falls back to transcription-only if diarization unavailable.
    """

    def __init__(self):
        self._whisper_model = None
        self._diarization_pipeline = None
        self._diarization_available = None  # None = not yet checked
        self._model_name = WHISPER_MODEL
        self._device = WHISPER_DEVICE
        self._compute_type = WHISPER_COMPUTE
        logger.info(
            f"DiarizedTranscriptionService initialized "
            f"(model={self._model_name}, device={self._device})"
        )

    def _load_whisper(self):
        """Lazy-load the whisper model"""
        if self._whisper_model is not None:
            return

        from faster_whisper import WhisperModel

        logger.info(f"Loading whisper model: {self._model_name} on {self._device}...")
        start = time.time()
        self._whisper_model = WhisperModel(
            self._model_name,
            device=self._device,
            compute_type=self._compute_type,
        )
        logger.info(f"Whisper model loaded in {time.time() - start:.1f}s")

    def _load_diarization(self) -> bool:
        """
        Lazy-load the pyannote diarization pipeline.
        Returns True if available, False otherwise.
        """
        if self._diarization_available is not None:
            return self._diarization_available

        # Check for HF token
        token = HF_TOKEN
        if not token:
            # Try file-based token
            token_path = Path.home() / ".cache" / "huggingface" / "token"
            if token_path.exists():
                token = token_path.read_text().strip()

        if not token:
            logger.warning(
                "No HuggingFace token found. Diarization disabled. "
                "Set HUGGINGFACE_TOKEN in .env or run `huggingface-cli login`"
            )
            self._diarization_available = False
            return False

        try:
            from pyannote.audio import Pipeline

            logger.info("Loading pyannote diarization pipeline...")
            start = time.time()
            self._diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=token,
            )

            # Move to GPU if available
            import torch
            if torch.cuda.is_available():
                self._diarization_pipeline.to(torch.device("cuda"))
                logger.info("Diarization pipeline moved to GPU")

            logger.info(f"Diarization pipeline loaded in {time.time() - start:.1f}s")
            self._diarization_available = True
            return True

        except Exception as e:
            logger.warning(f"Diarization unavailable: {e}")
            self._diarization_available = False
            return False

    def convert_to_wav(self, input_path: str, wav_path: str = None) -> Optional[str]:
        """
        Convert any audio format to 16kHz mono WAV for processing.
        Handles .m4a, .ogg, .opus, .mp3, .mp4, .wav, etc.
        """
        if wav_path is None:
            wav_path = str(Path(input_path).with_suffix(".wav"))

        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", input_path,
                    "-ar", "16000",       # 16kHz (whisper optimal)
                    "-ac", "1",           # mono
                    "-c:a", "pcm_s16le",  # 16-bit PCM
                    wav_path,
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout for long files
            )

            if result.returncode != 0:
                logger.error(f"ffmpeg conversion failed: {result.stderr[:500]}")
                return None

            logger.debug(f"Converted {input_path} → {wav_path}")
            return wav_path

        except subprocess.TimeoutExpired:
            logger.error(f"ffmpeg conversion timed out for {input_path}")
            return None
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return None

    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "quiet",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    audio_path,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def _transcribe_whisper(
        self, wav_path: str, language: str = None
    ) -> Dict[str, Any]:
        """Run whisper transcription, return segments with word-level timestamps."""
        self._load_whisper()

        kwargs = {
            "beam_size": 5,
            "vad_filter": True,
            "word_timestamps": True,  # Need word timestamps for diarization alignment
        }
        if language:
            kwargs["language"] = language

        segments_gen, info = self._whisper_model.transcribe(wav_path, **kwargs)

        segments = []
        full_text_parts = []

        for segment in segments_gen:
            seg_data = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
                "words": [],
            }

            # Collect word-level timestamps if available
            if segment.words:
                for word in segment.words:
                    seg_data["words"].append({
                        "word": word.word.strip(),
                        "start": round(word.start, 2),
                        "end": round(word.end, 2),
                        "probability": round(word.probability, 3),
                    })

            segments.append(seg_data)
            full_text_parts.append(segment.text.strip())

        return {
            "text": " ".join(full_text_parts),
            "segments": segments,
            "language": info.language,
            "language_probability": round(info.language_probability, 3),
        }

    def _run_diarization(self, wav_path: str) -> List[Dict[str, Any]]:
        """
        Run pyannote diarization on audio file.
        Returns list of speaker segments: [{"speaker": "SPEAKER_00", "start": 0.0, "end": 2.5}, ...]
        """
        if not self._load_diarization():
            return []

        logger.info(f"Running diarization on {wav_path}...")
        start = time.time()

        diarization = self._diarization_pipeline(wav_path)

        speaker_segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                "speaker": speaker,
                "start": round(turn.start, 2),
                "end": round(turn.end, 2),
            })

        logger.info(
            f"Diarization complete in {time.time() - start:.1f}s — "
            f"{len(speaker_segments)} segments, "
            f"{len(set(s['speaker'] for s in speaker_segments))} speakers"
        )

        return speaker_segments

    def _merge_transcription_and_diarization(
        self,
        whisper_segments: List[Dict],
        diarization_segments: List[Dict],
    ) -> List[Dict[str, Any]]:
        """
        Merge whisper transcription segments with pyannote diarization.
        Assigns speaker labels to each transcription segment based on
        temporal overlap with diarization segments.
        """
        if not diarization_segments:
            # No diarization — return whisper segments without speaker labels
            return [
                {
                    "speaker": "UNKNOWN",
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                }
                for seg in whisper_segments
            ]

        merged = []

        for wseg in whisper_segments:
            # Find the diarization segment with maximum overlap
            best_speaker = "UNKNOWN"
            best_overlap = 0.0

            for dseg in diarization_segments:
                # Calculate overlap
                overlap_start = max(wseg["start"], dseg["start"])
                overlap_end = min(wseg["end"], dseg["end"])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = dseg["speaker"]

            merged.append({
                "speaker": best_speaker,
                "start": wseg["start"],
                "end": wseg["end"],
                "text": wseg["text"],
            })

        return merged

    def _compute_speaker_stats(
        self, diarized_segments: List[Dict]
    ) -> Dict[str, Dict]:
        """Compute per-speaker statistics."""
        speakers = {}

        for seg in diarized_segments:
            spk = seg["speaker"]
            if spk not in speakers:
                speakers[spk] = {
                    "total_duration": 0.0,
                    "segment_count": 0,
                    "word_count": 0,
                }

            speakers[spk]["total_duration"] += seg["end"] - seg["start"]
            speakers[spk]["segment_count"] += 1
            speakers[spk]["word_count"] += len(seg["text"].split())

        # Round durations
        for spk in speakers:
            speakers[spk]["total_duration"] = round(
                speakers[spk]["total_duration"], 1
            )

        return speakers

    def transcribe_with_diarization(
        self,
        audio_path: str,
        language: str = None,
        wav_cache_dir: str = "/opt/mythos/voice_memos/wav_cache",
    ) -> Dict[str, Any]:
        """
        Full pipeline: convert → transcribe → diarize → merge.

        Args:
            audio_path: Path to audio file (any format ffmpeg supports)
            language: Optional language hint
            wav_cache_dir: Where to store converted WAV files

        Returns:
            Complete result dict with text, segments, speakers, diarized_segments
        """
        total_start = time.time()

        # Get duration of original
        duration = self.get_audio_duration(audio_path)
        logger.info(f"Processing {audio_path} ({duration:.1f}s)")

        # Convert to WAV
        Path(wav_cache_dir).mkdir(parents=True, exist_ok=True)
        wav_filename = Path(audio_path).stem + ".wav"
        wav_path = str(Path(wav_cache_dir) / wav_filename)

        convert_start = time.time()
        converted = self.convert_to_wav(audio_path, wav_path)
        if not converted:
            return {
                "text": "",
                "segments": [],
                "diarized_segments": [],
                "speakers": {},
                "diarized": False,
                "language": "",
                "duration": duration,
                "error": "conversion_failed",
            }
        convert_time = time.time() - convert_start

        # Transcribe
        transcribe_start = time.time()
        whisper_result = self._transcribe_whisper(wav_path, language)
        transcribe_time = time.time() - transcribe_start

        # Diarize
        diarize_start = time.time()
        diarization_segments = self._run_diarization(wav_path)
        diarize_time = time.time() - diarize_start

        # Merge
        diarized_segments = self._merge_transcription_and_diarization(
            whisper_result["segments"], diarization_segments
        )

        # Speaker stats
        speakers = self._compute_speaker_stats(diarized_segments)

        # Build formatted transcript
        formatted_lines = []
        current_speaker = None
        for seg in diarized_segments:
            if seg["speaker"] != current_speaker:
                current_speaker = seg["speaker"]
                formatted_lines.append(f"\n[{current_speaker}]")
            formatted_lines.append(seg["text"])

        formatted_transcript = "\n".join(formatted_lines).strip()

        total_time = time.time() - total_start

        result = {
            "text": whisper_result["text"],
            "formatted_transcript": formatted_transcript,
            "segments": whisper_result["segments"],
            "diarized_segments": diarized_segments,
            "speakers": speakers,
            "diarized": bool(diarization_segments),
            "language": whisper_result["language"],
            "language_probability": whisper_result.get("language_probability", 0),
            "duration": round(duration, 1),
            "processing_times": {
                "convert_s": round(convert_time, 1),
                "transcribe_s": round(transcribe_time, 1),
                "diarize_s": round(diarize_time, 1),
                "total_s": round(total_time, 1),
            },
        }

        logger.info(
            f"Pipeline complete: {duration:.0f}s audio → "
            f"{len(whisper_result['text'])} chars, "
            f"{len(speakers)} speakers, "
            f"processed in {total_time:.1f}s "
            f"(convert={convert_time:.1f}s, transcribe={transcribe_time:.1f}s, "
            f"diarize={diarize_time:.1f}s)"
        )

        # Clean up WAV cache file
        try:
            os.remove(wav_path)
        except OSError:
            pass

        return result
