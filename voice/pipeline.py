"""Pipeline - wires STT -> Processor -> TTS -> Mumble."""
import logging, threading, queue, time
import numpy as np
import yaml, os
from voice.stt import transcribe, VoiceActivityDetector
from voice.processor import process_text
from voice.tts import synthesize
from voice.mumble_client import IrisMumbleClient
logger = logging.getLogger("iris.voice.pipeline")

def load_config(path="/opt/mythos/voice/config.yaml"):
    with open(path) as f: return yaml.safe_load(f)

class VoicePipeline:
    def __init__(self, config=None, config_path="/opt/mythos/voice/config.yaml"):
        if config is None: config = load_config(config_path)
        self.config = config
        self.mumble = None
        self.vad = VoiceActivityDetector(config.get("stt", {}))
        self.conversation_history = []
        self._audio_queue = queue.Queue()
        self._running = False
        self._lock = threading.Lock()

    def start(self):
        logger.info("Starting voice pipeline...")

        # Pre-load models to avoid first-response delay
        logger.info("Pre-loading STT model...")
        from voice.stt import get_whisper_model
        get_whisper_model(self.config.get("stt", {}))

        logger.info("Pre-loading TTS model...")
        from voice.tts import get_pipeline
        get_pipeline()

        logger.info("Pre-loading VAD model...")
        from voice.stt import get_vad_model
        get_vad_model()

        # Connect to Mumble
        self.mumble = IrisMumbleClient(
            self.config.get("mumble", {}),
            on_audio_received=self._on_audio
        )
        self.mumble.connect()

        # Start processing thread
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

        # Greeting
        greeting = self.config.get("pipeline", {}).get("greeting", "")
        if greeting:
            logger.info("Speaking greeting...")
            self.say(greeting)

        logger.info("Voice pipeline running - Iris is listening")

    def stop(self):
        self._running = False
        if self.mumble: self.mumble.disconnect()
        logger.info("Voice pipeline stopped")

    def _on_audio(self, user, audio_float, sr):
        if sr != 16000:
            idx = np.arange(0, len(audio_float), sr / 16000).astype(int)
            audio_float = audio_float[idx[idx < len(audio_float)]]
        utterance = self.vad.process_chunk(audio_float)
        if utterance is not None:
            logger.debug(f"Utterance captured: {len(utterance)} samples ({len(utterance)/16000:.1f}s)")
            self._audio_queue.put(utterance)

    def _loop(self):
        while self._running:
            try:
                utterance = self._audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            with self._lock:
                self._handle(utterance)

    def _handle(self, audio):
        t0 = time.time()

        # 1. Transcribe
        text, conf = transcribe(audio, self.config.get("stt", {}))
        t_stt = time.time() - t0

        mc = self.config.get("pipeline", {}).get("min_confidence", 0.4)
        if not text or conf < mc:
            logger.debug(f"Ignored: '{text}' (conf={conf:.2f})")
            return

        logger.info(f"[STT {t_stt:.1f}s] '{text}' (conf={conf:.2f})")

        # 2. Wake word check
        pc = self.config.get("pipeline", {})
        if pc.get("wake_word_required", False):
            ww = pc.get("wake_words", ["iris"])
            tl = text.lower()
            if not any(w in tl for w in ww):
                return
            for w in ww:
                tl = tl.replace(w, "").strip()
            if tl:
                text = tl

        # 3. Process through LLM
        t1 = time.time()
        self.conversation_history.append({"role": "Human", "text": text})
        response = process_text(
            text, self.config.get("processor", {}), self.conversation_history
        )
        self.conversation_history.append({"role": "Iris", "text": response})
        t_llm = time.time() - t1

        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-12:]

        logger.info(f"[LLM {t_llm:.1f}s] '{response[:100]}'")

        # 4. Synthesize
        t2 = time.time()
        audio_out = synthesize(response, self.config.get("tts", {}))
        t_tts = time.time() - t2

        if audio_out is None:
            logger.warning("TTS returned no audio")
            return

        # 5. Send to Mumble
        t3 = time.time()
        self.mumble.send_audio(audio_out, sample_rate=24000)
        t_send = time.time() - t3
        t_total = time.time() - t0

        logger.info(f"[DONE {t_total:.1f}s] stt={t_stt:.1f} llm={t_llm:.1f} tts={t_tts:.1f} send={t_send:.1f}")

    def say(self, text):
        """Manually make Iris say something."""
        audio = synthesize(text, self.config.get("tts", {}))
        if audio is not None and self.mumble and self.mumble.is_connected:
            self.mumble.send_audio(audio, sample_rate=24000)
            return True
        return False
