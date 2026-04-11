# Mumble Voice Transport (Deprecated)

**Deployed:** Patch 0194 (Voice Foundation)  
**Replaced by:** Patch 0198 (Web Voice Interface)  
**Reason:** iOS Mumble client unmaintained (last update 2017), poor audio quality, 
whisper hallucination from ambient noise, no good push-to-talk on mobile.

## What It Was

Mumble server (mumble-server/murmur) running on Arcturus port 64738.
Iris connected as a pymumble bot, received audio from users in the channel,
ran STT -> LLM -> TTS pipeline, and sent audio back through Mumble.

## Components (Removed)

- `mumble-server` (apt package) - VoIP server
- `pymumble_py3` (pip package) - Python Mumble client library  
- `voice/mumble_client.py` - Iris Mumble bot (join channel, send/receive audio)
- `iris-tts.service` - Separate TTS server (XTTS v2, later removed in 0196)
- `voice/tts_server.py` - XTTS v2 microservice (removed in 0196)

## Architecture

```
User (Mumble client) -> Mumble Server -> pymumble -> VAD -> faster-whisper -> 
Ollama iris-thinking-v2 -> Kokoro TTS -> pymumble -> Mumble Server -> User
```

## Issues Encountered

1. **iOS client unmaintained** - Official Mumble iOS app last updated 2017, 
   breaks on iOS 16+, no good alternatives
2. **pymumble SSL incompatibility** - Python 3.12 removed ssl.wrap_socket, 
   required monkey-patch
3. **Whisper hallucination** - faster-whisper invents plausible sentences from 
   ambient noise/silence ("Thank you for watching!", "I came back to set you up 
   for a new video"). Mitigation: raise VAD threshold, require wake word.
4. **XTTS v2 GPU incompatibility** - RTX 5090 (sm_120/Blackwell) not supported 
   by PyTorch 2.5.1 required by Coqui TTS. Fell back to CPU (~10s latency).
   Resolved by switching to Kokoro TTS (patch 0196).
5. **Echo loop potential** - Bot could hear its own output through Mumble and 
   transcribe it.

## Lessons Learned

- Voice Activity Detection needs aggressive tuning in noisy environments
- Push-to-talk (explicit send) is more reliable than continuous VAD for home use
- Browser-based WebSocket approach avoids all client compatibility issues
- Kokoro TTS >> XTTS v2 for this hardware (RTX 5090 + Python 3.12)

## Mumble Server Config (for reference)

```
Host: 127.0.0.1
Port: 64738
User: Iris
Channel: Root (Iris channel was planned but not created)
```

## How to fully remove Mumble

```bash
sudo systemctl stop mumble-server
sudo systemctl disable mumble-server
sudo apt remove --purge mumble-server
/opt/mythos/.venv/bin/pip uninstall pymumble
rm /opt/mythos/voice/mumble_client.py
```
