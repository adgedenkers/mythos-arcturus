"""
Ollama API Client

Async wrapper for Ollama API operations.
Provides methods for model management and inference.

Example:
    async with OllamaClient() as client:
        models = await client.list_models()
        response = await client.generate("llama3.1:70b", "Hello!")
"""

import aiohttp
import asyncio
from typing import Optional, List, Dict, Any, AsyncIterator
import logging
from datetime import datetime

import sys
sys.path.insert(0, '/opt/mythos/orchestrator/src')
from config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Async client for Ollama API.
    
    Supports model listing, pulling, generation, and management.
    Uses connection pooling and automatic retries.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (default: from settings)
            timeout: Request timeout in seconds (default: from settings)
            max_retries: Maximum number of retry attempts
        """
        self.base_url = (base_url or settings.OLLAMA_HOST).rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout or settings.OLLAMA_TIMEOUT)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self):
        """Create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.info(f"Connected to Ollama at {self.base_url}")
    
    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Ollama client closed")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        stream: bool = False
    ) -> Any:
        """
        Make HTTP request to Ollama API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            json: JSON payload
            stream: Whether to stream response
            
        Returns:
            Response data
            
        Raises:
            Exception: If request fails after retries
        """
        if self.session is None:
            await self.connect()
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(method, url, json=json) as resp:
                    if resp.status == 200:
                        if stream:
                            return resp
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        logger.warning(
                            f"Ollama request failed (attempt {attempt + 1}): "
                            f"{resp.status} - {error_text}"
                        )
                        
                        if attempt == self.max_retries - 1:
                            raise Exception(
                                f"Ollama API error: {resp.status} - {error_text}"
                            )
                        
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except aiohttp.ClientError as e:
                logger.warning(
                    f"Ollama connection error (attempt {attempt + 1}): {e}"
                )
                
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to connect to Ollama: {e}")
                
                await asyncio.sleep(2 ** attempt)
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List all installed models.
        
        Returns:
            List of model dictionaries with name, size, modified time
            
        Example:
            models = await client.list_models()
            for model in models:
                print(model['name'], model['size'])
        """
        response = await self._request("GET", "/api/tags")
        return response.get("models", [])
    
    async def show_model(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            name: Model name (e.g., "llama3.1:70b")
            
        Returns:
            Model details including parameters, template, system prompt
        """
        response = await self._request("POST", "/api/show", json={"name": name})
        return response
    
    async def pull_model(self, name: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Pull a model from Ollama registry (streaming).
        
        Args:
            name: Model name to pull
            
        Yields:
            Progress updates
            
        Example:
            async for progress in client.pull_model("llama3.1:70b"):
                print(progress.get('status'))
        """
        async with await self._request(
            "POST",
            "/api/pull",
            json={"name": name},
            stream=True
        ) as resp:
            async for line in resp.content:
                if line:
                    import json
                    yield json.loads(line.decode())
    
    async def delete_model(self, name: str) -> bool:
        """
        Delete a model.
        
        Args:
            name: Model name to delete
            
        Returns:
            True if successful
        """
        try:
            await self._request("DELETE", "/api/delete", json={"name": name})
            return True
        except Exception as e:
            logger.error(f"Failed to delete model {name}: {e}")
            return False
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate completion from model.
        
        Args:
            model: Model name
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature (default: from settings)
            stream: Whether to stream response
            **kwargs: Additional model parameters
            
        Returns:
            Response dict or async iterator if streaming
            
        Example:
            # Non-streaming
            response = await client.generate("llama3.1:70b", "Hello!")
            print(response['response'])
            
            # Streaming
            async for chunk in await client.generate(
                "llama3.1:70b", "Hello!", stream=True
            ):
                print(chunk.get('response', ''), end='')
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature or settings.DEFAULT_TEMPERATURE,
                **kwargs
            }
        }
        
        if system:
            payload["system"] = system
        
        if stream:
            return self._generate_stream(payload)
        else:
            return await self._request("POST", "/api/generate", json=payload)
    
    async def _generate_stream(self, payload: Dict) -> AsyncIterator[Dict]:
        """Stream generation responses."""
        async with await self._request(
            "POST",
            "/api/generate",
            json=payload,
            stream=True
        ) as resp:
            async for line in resp.content:
                if line:
                    import json
                    yield json.loads(line.decode())
    
    async def embeddings(self, model: str, prompt: str) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            model: Model name (must support embeddings)
            prompt: Text to embed
            
        Returns:
            List of embedding values
        """
        response = await self._request(
            "POST",
            "/api/embeddings",
            json={"model": model, "prompt": prompt}
        )
        return response.get("embedding", [])
    
    async def health_check(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if service is responsive
        """
        try:
            await self.list_models()
            return True
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def parse_model_name(self, name: str) -> Dict[str, str]:
        """
        Parse model name into components.
        
        Args:
            name: Model name (e.g., "llama3.1:70b")
            
        Returns:
            Dict with 'base', 'tag', 'size'
            
        Example:
            >>> client.parse_model_name("llama3.1:70b")
            {'base': 'llama3.1', 'tag': '70b', 'size': '70B'}
        """
        parts = name.split(":")
        base = parts[0]
        tag = parts[1] if len(parts) > 1 else "latest"
        
        # Extract size if present
        size = None
        import re
        match = re.search(r'(\d+)[bB]', tag)
        if match:
            size = f"{match.group(1)}B"
        
        return {
            "base": base,
            "tag": tag,
            "size": size
        }
