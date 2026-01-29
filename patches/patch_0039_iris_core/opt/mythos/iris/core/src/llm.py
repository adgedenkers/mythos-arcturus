"""
IRIS LLM Client

Interface to Ollama for language model capabilities.
"""

import asyncio
from typing import Dict, List, Any, Optional

import httpx
import structlog

from .config import Config

log = structlog.get_logger("iris.llm")


class LLMClient:
    """
    Client for interacting with Ollama.
    
    This is how Iris thinks in language.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.ollama_host
        self.model = config.ollama_model
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self):
        """Initialize the HTTP client."""
        log.info("llm_connecting", host=self.base_url, model=self.model)
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(300.0, connect=10.0)  # 5 min for generation
        )
        
        # Verify connection
        try:
            response = await self._client.get("/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                log.info("llm_connected", available_models=model_names)
                
                if self.model not in model_names and f"{self.model}:latest" not in model_names:
                    log.warning("llm_model_not_found", model=self.model, available=model_names)
            else:
                log.error("llm_connection_failed", status=response.status_code)
        except Exception as e:
            log.error("llm_connection_error", error=str(e))
    
    async def disconnect(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        log.info("llm_disconnected")
    
    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt
            
        Returns:
            The generated text
        """
        if not self._client:
            log.error("llm_not_connected")
            return ""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        
        if system:
            payload["system"] = system
        
        try:
            log.debug("llm_generating", prompt_length=len(prompt))
            
            response = await self._client.post("/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                generated = result.get("response", "")
                
                log.debug("llm_generated", 
                         response_length=len(generated),
                         eval_count=result.get("eval_count"),
                         eval_duration=result.get("eval_duration"))
                
                return generated
            else:
                log.error("llm_generation_failed", 
                         status=response.status_code,
                         body=response.text[:200])
                return ""
                
        except httpx.TimeoutException:
            log.error("llm_timeout")
            return ""
        except Exception as e:
            log.error("llm_error", error=str(e))
            return ""
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat completion with message history.
        
        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}
            
        Returns:
            The assistant's response
        """
        if not self._client:
            log.error("llm_not_connected")
            return ""
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        
        try:
            response = await self._client.post("/api/chat", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                message = result.get("message", {})
                return message.get("content", "")
            else:
                log.error("llm_chat_failed", status=response.status_code)
                return ""
                
        except Exception as e:
            log.error("llm_chat_error", error=str(e))
            return ""
    
    async def embed(self, text: str) -> List[float]:
        """
        Get embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self._client:
            log.error("llm_not_connected")
            return []
        
        payload = {
            "model": self.model,
            "prompt": text,
        }
        
        try:
            response = await self._client.post("/api/embeddings", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding", [])
            else:
                log.error("llm_embed_failed", status=response.status_code)
                return []
                
        except Exception as e:
            log.error("llm_embed_error", error=str(e))
            return []
