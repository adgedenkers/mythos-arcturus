"""Web Voice Server - FastAPI + WebSocket for browser-based voice interaction."""
import asyncio, logging, struct, io, time
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

logger = logging.getLogger("iris.voice.web")

# Lazy-loaded pipeline components
_stt_model = None
_tts_pipeline = None
_processor_config = None
_config = None

def load_config():
    global _config
    if _config: return _config
    import yaml
    with open("/opt/mythos/voice/config.yaml") as f:
        _config = yaml.safe_load(f)
    return _config

def get_stt():
    global _stt_model
    if _stt_model: return _stt_model
    from faster_whisper import WhisperModel
    config = load_config().get("stt", {})
    ms = config.get("model_size", "medium.en")
    dev = config.get("device", "cuda")
    ct = config.get("compute_type", "float16")
    logger.info(f"Loading faster-whisper: {ms} on {dev}")
    _stt_model = WhisperModel(ms, device=dev, compute_type=ct)
    return _stt_model

def get_tts():
    global _tts_pipeline
    if _tts_pipeline: return _tts_pipeline
    from kokoro import KPipeline
    logger.info("Loading Kokoro TTS...")
    _tts_pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    logger.info("Kokoro TTS loaded")
    return _tts_pipeline

def transcribe(audio_f32):
    model = get_stt()
    try:
        segments, info = model.transcribe(audio_f32, beam_size=5, language="en")
        parts = [s.text.strip() for s in segments]
        if not parts: return None
        return " ".join(parts)
    except Exception as e:
        logger.error(f"STT failed: {e}")
        return None

def synthesize(text):
    from voice.pronunciations import apply
    text = apply(text)
    config = load_config().get("tts", {})
    voice = config.get("voice", "af_heart")
    pipe = get_tts()
    try:
        segments = []
        for gs, ps, audio in pipe(text, voice=voice):
            segments.append(audio)
        if not segments: return None
        audio = np.concatenate(segments) if len(segments) > 1 else segments[0]
        if hasattr(audio, 'numpy'): audio = audio.numpy()
        return np.asarray(audio, dtype=np.float32)
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return None

def think(text, history):
    from voice.processor import process_text
    config = load_config().get("processor", {})
    return process_text(text, config, history)

def audio_to_wav_bytes(audio_f32, sr=24000):
    """Convert float32 numpy array to WAV bytes."""
    pcm = (audio_f32 * 32767).astype(np.int16)
    buf = io.BytesIO()
    # WAV header
    data_size = len(pcm) * 2
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    buf.write(pcm.tobytes())
    return buf.getvalue()

# --- FastAPI app ---
app = FastAPI(title="Iris Voice")
app.mount("/static", StaticFiles(directory="/opt/mythos/voice/static"), name="static")

@app.get("/")
async def index():
    return FileResponse("/opt/mythos/voice/static/index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "iris-voice-web"}

@app.websocket("/ws/voice")
async def voice_ws(websocket: WebSocket):
    await websocket.accept()
    history = []
    logger.info("Client connected")

    # Send greeting
    try:
        config = load_config()
        greeting = config.get("pipeline", {}).get("greeting", "Iris online. I am listening.")
        audio = synthesize(greeting)
        if audio is not None:
            wav = audio_to_wav_bytes(audio)
            await websocket.send_bytes(wav)
            logger.info("Greeting sent")
    except Exception as e:
        logger.error(f"Greeting failed: {e}")

    try:
        while True:
            # Receive audio bytes from browser (16-bit PCM, 16kHz mono)
            data = await websocket.receive_bytes()
            t0 = time.time()

            # Convert to float32
            pcm16 = np.frombuffer(data, dtype=np.int16)
            audio_f32 = pcm16.astype(np.float32) / 32768.0

            # Skip very short audio
            duration = len(audio_f32) / 16000.0
            if duration < 0.5:
                logger.debug(f"Skipped short audio: {duration:.2f}s")
                continue

            # STT
            t1 = time.time()
            text = transcribe(audio_f32)
            t_stt = time.time() - t1

            if not text or len(text.strip()) < 2:
                logger.debug(f"Empty transcription from {duration:.1f}s audio")
                continue

            logger.info(f"[STT {t_stt:.1f}s] '{text}'")

            # Send transcription to client
            await websocket.send_json({"type": "transcript", "text": text})

            # LLM
            t2 = time.time()
            history.append({"role": "Human", "text": text})
            response = await asyncio.to_thread(think, text, history)
            history.append({"role": "Iris", "text": response})
            t_llm = time.time() - t2

            if len(history) > 20:
                history = history[-12:]

            logger.info(f"[LLM {t_llm:.1f}s] '{response[:100]}'")

            # Send response text to client
            await websocket.send_json({"type": "response", "text": response})

            # TTS
            t3 = time.time()
            audio = await asyncio.to_thread(synthesize, response)
            t_tts = time.time() - t3

            if audio is not None:
                wav = audio_to_wav_bytes(audio)
                await websocket.send_bytes(wav)
                t_total = time.time() - t0
                logger.info(f"[DONE {t_total:.1f}s] stt={t_stt:.1f} llm={t_llm:.1f} tts={t_tts:.1f}")
            else:
                logger.warning("TTS returned no audio")

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

def start_server(host="0.0.0.0", port=8777):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    )
    import sys
    sys.path.insert(0, "/opt/mythos")
    logger.info(f"Starting Iris Voice Web on {host}:{port}")
    logger.info("Pre-loading models...")
    get_stt()
    get_tts()
    logger.info("Models loaded. Server starting.")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_server()
