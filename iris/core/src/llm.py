"""
IRIS LLM Client

Interface to Ollama for language model capabilities.
Integrates with prompt manager for system prompts.
"""

import asyncio
from typing import Dict, List, Any, Optional

import httpx
import structlog

from .config import Config
from .prompts import PromptManager, TaskType, ModelConfig, get_prompt_manager

log = structlog.get_logger("iris.llm")


class LLMClient:
    """
    Client for interacting with Ollama.
    
    This is how Iris thinks in language.
    """
    
    def __init__(self, config: Config, prompt_manager: Optional[PromptManager] = None):
        self.config = config
        self.base_url = config.ollama_host
        self.default_model = config.ollama_model
        self.prompt_manager = prompt_manager or get_prompt_manager()
        self._client: Optional[httpx.AsyncClient] = None
        self._available_models: List[str] = []
    
    async def connect(self):
        """Initialize the HTTP client and verify connection."""
        log.info("llm_connecting", host=self.base_url, default_model=self.default_model)
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(300.0, connect=10.0)  # 5 min for generation
        )
        
        # Load prompts
        if not self.prompt_manager.load():
            log.warning("prompt_load_failed", message="Using fallback prompts")
        
        # Verify connection and get available models
        try:
            response = await self._client.get("/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                self._available_models = [m.get("name") for m in models]
                log.info("llm_connected", available_models=self._available_models)
                
                if self.default_model not in self._available_models:
                    # Try with :latest suffix
                    if f"{self.default_model}:latest" in self._available_models:
                        self.default_model = f"{self.default_model}:latest"
                    else:
                        log.warning("default_model_not_found", 
                                   model=self.default_model, 
                                   available=self._available_models)
            else:
                log.error("llm_connection_failed", status=response.status_code)
        except Exception as e:
            log.error("llm_connection_error", error=str(e))
            raise
    
    async def disconnect(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        log.info("llm_disconnected")
    
    def _get_model_for_task(self, task_type: TaskType) -> str:
        """
        Get the appropriate model for a task type.
        
        Falls back to default if preferred model not available.
        """
        config = self.prompt_manager.get_model_config(task_type)
        preferred = config.model
        
        # Check if preferred model is available
        if preferred in self._available_models:
            return preferred
        if f"{preferred}:latest" in self._available_models:
            return f"{preferred}:latest"
        
        # Fallback to default
        log.warning("model_fallback", 
                   preferred=preferred, 
                   using=self.default_model)
        return self.default_model
    
    async def generate(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        task_type: TaskType = TaskType.CONVERSATION,
        model_override: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt (uses identity if not provided)
            task_type: Type of task for model/param selection
            model_override: Override model selection
            
        Returns:
            The generated text
        """
        if not self._client:
            log.error("llm_not_connected")
            return ""
        
        # Get model and config
        config = self.prompt_manager.get_model_config(task_type)
        model = model_override or self._get_model_for_task(task_type)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens,
            }
        }
        
        if system:
            payload["system"] = system
        
        if config.stop_sequences:
            payload["options"]["stop"] = config.stop_sequences
        
        try:
            log.debug("llm_generating", 
                     model=model,
                     task_type=task_type.value,
                     prompt_length=len(prompt),
                     system_length=len(system) if system else 0)
            
            response = await self._client.post("/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                generated = result.get("response", "")
                
                log.debug("llm_generated", 
                         response_length=len(generated),
                         eval_count=result.get("eval_count"),
                         eval_duration_ms=result.get("eval_duration", 0) / 1_000_000)
                
                return generated
            else:
                log.error("llm_generation_failed", 
                         status=response.status_code,
                         body=response.text[:200])
                return ""
                
        except httpx.TimeoutException:
            log.error("llm_timeout", model=model, task_type=task_type.value)
            return ""
        except Exception as e:
            log.error("llm_error", error=str(e))
            return ""
    
    async def respond(
        self,
        message: str,
        mode: str = "available",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        memories: Optional[List[str]] = None,
        spiral_day: Optional[int] = None,
        additional_context: Optional[str] = None,
        task_type: TaskType = TaskType.CONVERSATION
    ) -> str:
        """
        Generate a response as Iris.
        
        This is the main method for responding to humans.
        Assembles full system prompt with identity, mode, and context.
        
        Args:
            message: The human's message
            mode: Current operating mode
            conversation_history: Recent conversation for context
            memories: Relevant memories to include
            spiral_day: Current day in 9-day cycle
            additional_context: Any additional context
            task_type: Type of task
            
        Returns:
            Iris's response
        """
        # Assemble system prompt
        system = self.prompt_manager.assemble_system_prompt(
            mode=mode,
            task_type=task_type,
            spiral_day=spiral_day,
            additional_context=additional_context,
            memories=memories
        )
        
        # Build prompt with conversation history
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
            full_prompt = f"{history_text}\n\nHuman: {message}\n\nIris:"
        else:
            full_prompt = f"Human: {message}\n\nIris:"
        
        return await self.generate(
            prompt=full_prompt,
            system=system,
            task_type=task_type
        )
    
    def _format_conversation_history(
        self, 
        history: List[Dict[str, str]], 
        max_messages: int = 20
    ) -> str:
        """Format conversation history for inclusion in prompt."""
        # Take most recent messages
        recent = history[-max_messages:] if len(history) > max_messages else history
        
        lines = []
        for msg in recent:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                speaker = msg.get("name", "Human")
                lines.append(f"{speaker}: {content}")
            elif role == "assistant":
                lines.append(f"Iris: {content}")
        
        return "\n\n".join(lines)
    
    async def chat(
        self, 
        messages: List[Dict[str, str]],
        task_type: TaskType = TaskType.CONVERSATION
    ) -> str:
        """
        Chat completion with message history.
        
        Uses Ollama's chat endpoint directly.
        
        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}
            task_type: Type of task for model selection
            
        Returns:
            The assistant's response
        """
        if not self._client:
            log.error("llm_not_connected")
            return ""
        
        config = self.prompt_manager.get_model_config(task_type)
        model = self._get_model_for_task(task_type)
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens,
            }
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
    
    async def classify(self, message: str) -> str:
        """
        Quickly classify a message type.
        
        Uses smaller, faster model for classification.
        
        Args:
            message: The message to classify
            
        Returns:
            Classification category
        """
        prompt = self.prompt_manager.get_classification_prompt(message)
        
        result = await self.generate(
            prompt=prompt,
            task_type=TaskType.CLASSIFICATION
        )
        
        # Extract just the category
        return result.strip().upper()
    
    async def summarize_conversation(
        self, 
        messages: List[str], 
        max_tokens: int = 500
    ) -> str:
        """
        Summarize a conversation for context compression.
        
        Args:
            messages: List of conversation messages
            max_tokens: Target summary length
            
        Returns:
            Conversation summary
        """
        prompt = self.prompt_manager.get_summary_prompt(messages, max_tokens)
        
        return await self.generate(
            prompt=prompt,
            task_type=TaskType.RESEARCH  # Use research config for summaries
        )
    
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
            "model": self.default_model,
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
    
    async def analyze_image(
        self,
        image_base64: str,
        prompt: str = "Describe this image in detail.",
        context: Optional[str] = None
    ) -> str:
        """
        Analyze an image using vision model.
        
        Args:
            image_base64: Base64-encoded image
            prompt: Question or instruction about the image
            context: Additional context for the analysis
            
        Returns:
            Analysis result
        """
        if not self._client:
            log.error("llm_not_connected")
            return ""
        
        config = self.prompt_manager.get_model_config(TaskType.VISION)
        model = self._get_model_for_task(TaskType.VISION)
        
        # Build system prompt for vision
        system = self.prompt_manager.assemble_system_prompt(
            mode="presence",
            task_type=TaskType.VISION,
            additional_context=context
        )
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "images": [image_base64],
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            }
        }
        
        try:
            log.debug("llm_analyzing_image", model=model, prompt_length=len(prompt))
            
            response = await self._client.post("/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                log.error("llm_vision_failed", status=response.status_code)
                return ""
                
        except Exception as e:
            log.error("llm_vision_error", error=str(e))
            return ""
