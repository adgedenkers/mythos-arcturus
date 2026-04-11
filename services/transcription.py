#!/usr/bin/env python3
"""
Transcription Service for Mythos

Uses faster-whisper (CTranslate2) with GPU acceleration for speech-to-text.
Handles Telegram voice messages (.ogg/opus) → WAV conversion → transcription.

Usage:
    from services.transcription import TranscriptionService
    
    ts = TranscriptionService()
    result = ts.transcribe("/path/to/audio.ogg")
    # result = {"text": "...", "segments": [...], "language": "en", "duration": 12.3}
"""

import os
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Model config
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "large-v3")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "float16")


class TranscriptionService:
    """
    GPU-accelerated speech-to-text using faster-whisper.
    
    Lazy-loads the model on first use to avoid startup delay.
    """
    
    def __init__(self):
        self._model = None
        self._model_name = WHISPER_MODEL
        self._device = WHISPER_DEVICE
        self._compute_type = WHISPER_COMPUTE
        logger.info(f"TranscriptionService initialized (model={self._model_name}, device={self._device})")
    
    def _load_model(self):
        """Lazy-load the whisper model on first transcription"""
        if self._model is not None:
            return
        
        from faster_whisper import WhisperModel
        
        logger.info(f"Loading whisper model: {self._model_name} on {self._device}...")
        self._model = WhisperModel(
            self._model_name,
            device=self._device,
            compute_type=self._compute_type
        )
        logger.info("Whisper model loaded")
    
    def convert_ogg_to_wav(self, ogg_path: str, wav_path: str = None) -> str:
        """
        Convert Telegram voice message (.ogg/opus) to WAV for whisper.
        Returns path to WAV file.
        """
        if wav_path is None:
            wav_path = ogg_path.rsplit('.', 1)[0] + '.wav'
        
        try:
            result = subprocess.run(
                [
                    'ffmpeg', '-y', '-i', ogg_path,
                    '-ar', '16000',     # 16kHz sample rate (whisper optimal)
                    '-ac', '1',          # mono
                    '-c:a', 'pcm_s16le', # 16-bit PCM
                    wav_path
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg conversion failed: {result.stderr}")
                return None
            
            logger.debug(f"Converted {ogg_path} → {wav_path}")
            return wav_path
            
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg conversion timed out")
            return None
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return None
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            result = subprocess.run(
                [
                    'ffprobe', '-v', 'quiet',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    audio_path
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            return float(result.stdout.strip())
        except Exception:
            return 0.0
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to audio file (WAV, OGG, MP3, etc.)
            language: Optional language hint (e.g., 'en')
        
        Returns:
            {
                "text": "full transcription text",
                "segments": [{"start": 0.0, "end": 2.5, "text": "..."}],
                "language": "en",
                "duration": 12.3
            }
        """
        self._load_model()
        
        # Convert OGG to WAV if needed
        needs_cleanup = False
        process_path = audio_path
        
        if audio_path.endswith(('.ogg', '.opus', '.oga')):
            wav_path = self.convert_ogg_to_wav(audio_path)
            if wav_path is None:
                return {"text": "", "segments": [], "language": "", "duration": 0, "error": "conversion_failed"}
            process_path = wav_path
            needs_cleanup = True
        
        try:
            # Get duration
            duration = self.get_audio_duration(process_path)
            
            # Transcribe
            kwargs = {"beam_size": 5, "vad_filter": True}
            if language:
                kwargs["language"] = language
            
            segments_gen, info = self._model.transcribe(process_path, **kwargs)
            
            # Collect segments
            segments = []
            full_text_parts = []
            
            for segment in segments_gen:
                seg_data = {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                }
                segments.append(seg_data)
                full_text_parts.append(segment.text.strip())
            
            full_text = " ".join(full_text_parts)
            
            result = {
                "text": full_text,
                "segments": segments,
                "language": info.language,
                "language_probability": round(info.language_probability, 3),
                "duration": round(duration, 1),
            }
            
            logger.info(f"Transcribed {duration:.1f}s audio → {len(full_text)} chars, lang={info.language}")
            return result
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {"text": "", "segments": [], "language": "", "duration": 0, "error": str(e)}
        
        finally:
            # Clean up temp WAV if we created one
            if needs_cleanup and process_path != audio_path:
                try:
                    os.remove(process_path)
                except OSError:
                    pass
