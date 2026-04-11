#!/usr/bin/env python3
"""
Runner — Send prompts to Ollama and capture everything.
"""
import os
import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ollama import Client

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')


def get_client() -> Client:
    return Client(host=OLLAMA_HOST)


def list_models() -> list:
    """Get names of all pulled Ollama models."""
    try:
        client = get_client()
        response = client.list()
        models = response.models if hasattr(response, 'models') else response.get('models', [])
        names = []
        for m in models:
            name = m.model if hasattr(m, 'model') else m.get('model', m.get('name', ''))
            if name:
                names.append(name)
        return sorted(names)
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []


def run_prompt(
    system_prompt: str,
    user_message: str,
    model: str = 'qwen2.5:32b',
    temperature: float = 0.7,
    num_predict: int = 4096,
    conversation_history: list = None,
) -> Dict[str, Any]:
    """
    Send a prompt to Ollama and capture the full result.

    Returns dict with: response, timing, token counts, model info, full prompt.
    """
    client = get_client()

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({'role': 'user', 'content': user_message})

    start = time.time()
    try:
        response = client.chat(
            model=model,
            messages=messages,
            options={
                'temperature': temperature,
                'num_predict': num_predict,
            }
        )
        elapsed = time.time() - start

        text = response['message']['content']
        eval_count = response.get('eval_count', 0)
        prompt_eval_count = response.get('prompt_eval_count', 0)

        return {
            'success': True,
            'response': text,
            'model': model,
            'temperature': temperature,
            'elapsed_seconds': round(elapsed, 2),
            'word_count': len(text.split()),
            'char_count': len(text),
            'eval_tokens': eval_count,
            'prompt_tokens': prompt_eval_count,
            'system_prompt': system_prompt,
            'system_prompt_length': len(system_prompt) if system_prompt else 0,
            'user_message': user_message,
            'timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'success': False,
            'error': str(e),
            'model': model,
            'elapsed_seconds': round(elapsed, 2),
            'system_prompt': system_prompt,
            'user_message': user_message,
            'timestamp': datetime.now().isoformat(),
        }
