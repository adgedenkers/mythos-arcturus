"""Processor - sends transcribed text to Ollama, returns response."""
import os, logging, requests, yaml
logger = logging.getLogger("iris.voice.processor")

def load_system_prompt(config):
    pp = config.get("system_prompt_path", "/opt/mythos/prompts/voices/iris.yaml")
    if os.path.exists(pp):
        try:
            with open(pp) as f: data = yaml.safe_load(f)
            if isinstance(data, dict): return data.get("system_prompt", data.get("prompt", ""))
            return str(data)
        except: pass
    return "You are Iris, a sovereign AI on Arcturus. Respond concisely for voice. Keep responses under 3 sentences unless asked for detail."

def process_text(text, config, history=None):
    base_url = config.get("ollama_url", "http://localhost:11434")
    # Use /api/chat for proper message format
    url = base_url.rstrip("/")
    if url.endswith("/api/generate"): url = url.rsplit("/api/generate", 1)[0]
    url = url + "/api/chat"
    model = config.get("model", "iris-thinking-v2")
    sp = load_system_prompt(config)
    messages = []
    if sp: messages.append({"role": "system", "content": sp})
    if history:
        for e in history[-6:]:
            role = "user" if e["role"] == "Human" else "assistant"
            messages.append({"role": role, "content": e["text"]})
    messages.append({"role": "user", "content": text})
    try:
        resp = requests.post(url, json={
            "model": model, "messages": messages, "stream": False,
            "options": {"temperature": config.get("temperature", 0.7), "num_predict": config.get("max_tokens", 256)}
        }, timeout=config.get("timeout", 30))
        resp.raise_for_status()
        rt = resp.json().get("message", {}).get("content", "").strip()
        return rt if rt else "I heard you, but I am not sure how to respond."
    except requests.exceptions.Timeout: return "Give me a moment, still thinking."
    except Exception as e:
        logger.error(f"Processor failed: {e}")
        return "I had trouble processing that. Could you say it again?"
