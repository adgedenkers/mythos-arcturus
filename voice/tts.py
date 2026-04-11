"""TTS engine - Kokoro TTS with af_heart voice."""
import os, logging
import numpy as np
logger = logging.getLogger("iris.voice.tts")
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is not None: return _pipeline
    logger.info("Loading Kokoro TTS...")
    from kokoro import KPipeline
    _pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    logger.info("Kokoro TTS loaded")
    return _pipeline

def synthesize(text, config, output_path=None):
    if not text or not text.strip(): return None
    from voice.pronunciations import apply
    text = apply(text)
    pipe = get_pipeline()
    voice = config.get("voice", "af_heart")
    try:
        segments = []
        for gs, ps, audio in pipe(text, voice=voice):
            segments.append(audio)
        if not segments: return None
        audio = np.concatenate(segments) if len(segments) > 1 else segments[0]
        if hasattr(audio, 'numpy'): audio = audio.numpy()
        audio = np.asarray(audio, dtype=np.float32)
        if output_path:
            try:
                import soundfile as sf
                sf.write(output_path, audio, 24000)
            except ImportError: pass
        return audio
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return None

def ping():
    try:
        get_pipeline()
        return True
    except: return False
