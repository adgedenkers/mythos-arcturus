"""STT engine - faster-whisper with Silero VAD."""
import logging, time
import numpy as np
logger = logging.getLogger("iris.voice.stt")
_whisper_model = None
_vad_model = None

def get_whisper_model(config):
    global _whisper_model
    if _whisper_model is not None: return _whisper_model
    from faster_whisper import WhisperModel
    ms = config.get("model_size", "medium.en")
    dev = config.get("device", "cuda")
    ct = config.get("compute_type", "float16")
    logger.info(f"Loading faster-whisper: {ms} on {dev}")
    _whisper_model = WhisperModel(ms, device=dev, compute_type=ct)
    return _whisper_model

def get_vad_model():
    global _vad_model
    if _vad_model is not None: return _vad_model
    import torch
    logger.info("Loading Silero VAD...")
    model, _ = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad", force_reload=False)
    _vad_model = model
    return _vad_model

def transcribe(audio_data, config):
    model = get_whisper_model(config)
    try:
        segments, info = model.transcribe(audio_data, beam_size=5, language="en")
        parts = []
        for s in segments:
            parts.append(s.text.strip())
        if not parts: return None, 0.0
        return " ".join(parts), 0.9
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None, 0.0

class VoiceActivityDetector:
    def __init__(self, config):
        vc = config.get("vad", {})
        self.threshold = vc.get("threshold", 0.5)
        self.min_speech_ms = vc.get("min_speech_ms", 250)
        self.post_speech_pause_ms = vc.get("post_speech_pause_ms", 800)
        self._buffer, self._is_speaking = [], False
        self._silence_start, self._speech_start, self._vad = None, None, None

    def process_chunk(self, audio_chunk):
        import torch
        if self._vad is None: self._vad = get_vad_model()
        for i in range(0, len(audio_chunk), 512):
            frame = audio_chunk[i:i+512]
            if len(frame) < 512: frame = np.pad(frame, (0, 512-len(frame)))
            sp = self._vad(torch.from_numpy(frame).float(), 16000).item()
            if sp >= self.threshold:
                if not self._is_speaking:
                    self._is_speaking, self._speech_start = True, time.time()
                self._silence_start = None
                self._buffer.append(frame)
            elif self._is_speaking:
                self._buffer.append(frame)
                if self._silence_start is None: self._silence_start = time.time()
                if (time.time()-self._silence_start)*1000 >= self.post_speech_pause_ms:
                    if (time.time()-self._speech_start)*1000 >= self.min_speech_ms:
                        u = np.concatenate(self._buffer); self._reset(); return u
                    self._reset()
        return None

    def _reset(self):
        self._buffer, self._is_speaking = [], False
        self._silence_start, self._speech_start = None, None
