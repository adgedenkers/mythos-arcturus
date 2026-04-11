"""Voice Lab - test TTS, preview output."""
import os, logging, subprocess
from voice.tts import synthesize
from voice.pipeline import load_config
logger = logging.getLogger("iris.voice.voice_lab")

def test_tts(text, config_path="/opt/mythos/voice/config.yaml", output_path=None):
    config = load_config(config_path)
    tc = config.get("tts", {})
    if output_path is None: output_path = "/opt/mythos/voice/cache/test_output.wav"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    audio = synthesize(text, tc, output_path=output_path)
    if audio is not None:
        duration = len(audio) / 24000.0
        print(f"Generated {duration:.1f}s -> {output_path}")
        subprocess.run(["aplay", output_path])
        return output_path
    print("TTS failed"); return None

def set_voice(voice_name, config_path="/opt/mythos/voice/config.yaml"):
    print(f"To change voice, edit {config_path} and set tts.voice to: {voice_name}")
    print("Available: af_heart, af_bella, af_sarah, af_nova, af_sky, af_nicole")
    return voice_name
