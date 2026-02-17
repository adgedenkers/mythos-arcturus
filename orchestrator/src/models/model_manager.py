"""
Model Manager

High-level operations combining Ollama client and model registry.
Handles model discovery, synchronization, and management.

Example:
    manager = ModelManager()
    await manager.sync_models()
    models = await manager.get_available_models()
"""

from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ollama_client import OllamaClient
from models.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class ModelManager:
    """
    High-level model management operations.
    
    Coordinates between Ollama and the model registry.
    """
    
    def __init__(self):
        """Initialize model manager."""
        self.registry = ModelRegistry()
    
    async def sync_models(self) -> Dict[str, int]:
        """
        Synchronize installed Ollama models with registry.
        
        Discovers models from Ollama and registers them in database.
        Updates installation status for existing models.
        
        Returns:
            Dict with counts: {registered, updated, total}
            
        Example:
            result = await manager.sync_models()
            print(f"Registered {result['registered']} new models")
        """
        async with OllamaClient() as client:
            # Get models from Ollama
            ollama_models = await client.list_models()
            
            registered_count = 0
            updated_count = 0
            
            # Register each model
            for model_data in ollama_models:
                name = model_data.get("name", "")
                
                if not name:
                    continue
                
                # Parse model info
                parsed = client.parse_model_name(name)
                size_params = parsed.get("size")
                
                # Extract context window - it should be an integer
                context_window = None
                try:
                    details = model_data.get("details", {})
                    # Look for parameter_count or context_length as integers
                    if "parameter_count" in details:
                        # This might be the actual parameter count
                        param_count = details.get("parameter_count")
                        if isinstance(param_count, (int, float)):
                            context_window = int(param_count)
                    # Fallback: try to get from families or other fields
                    # For now, leave as None if not found
                except Exception as e:
                    logger.warning(f"Could not extract context window for {name}: {e}")
                    context_window = None
                
                # Check if model exists
                existing = await self.registry.get_model_by_name(name)
                
                if existing:
                    # Update existing model
                    await self.registry.mark_installed(existing["model_id"], True)
                    updated_count += 1
                else:
                    # Register new model
                    await self.registry.register_model(
                        name=name,
                        provider="ollama",
                        size_params=size_params,
                        context_window=context_window,
                        metadata={
                            "size": model_data.get("size"),
                            "modified_at": model_data.get("modified_at"),
                            "digest": model_data.get("digest"),
                            "details": model_data.get("details", {})
                        },
                        mark_installed=True
                    )
                    registered_count += 1
            
            logger.info(
                f"Synced models: {registered_count} registered, "
                f"{updated_count} updated, {len(ollama_models)} total"
            )
            
            return {
                "registered": registered_count,
                "updated": updated_count,
                "total": len(ollama_models)
            }
    
    async def get_available_models(
        self,
        installed_only: bool = True,
        with_capabilities: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get list of available models.
        
        Args:
            installed_only: Only return installed models
            with_capabilities: Include capability information
            
        Returns:
            List of model dicts
        """
        models = await self.registry.list_models(
            provider="ollama",
            installed_only=installed_only
        )
        
        if with_capabilities:
            for model in models:
                caps = await self.registry.get_capabilities(model["model_id"])
                model["capabilities"] = caps
        
        return models
    
    async def get_model_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a model.
        
        Combines registry data with live Ollama data.
        
        Args:
            name: Model name
            
        Returns:
            Combined model information
        """
        # Get from registry
        model = await self.registry.get_model_by_name(name)
        
        if not model:
            return None
        
        # Get capabilities
        caps = await self.registry.get_capabilities(model["model_id"])
        model["capabilities"] = caps
        
        # Get live data from Ollama if installed
        if model.get("installed"):
            try:
                async with OllamaClient() as client:
                    ollama_info = await client.show_model(name)
                    model["ollama_details"] = ollama_info
            except Exception as e:
                logger.warning(f"Failed to get Ollama details for {name}: {e}")
        
        return model
    
    async def ensure_model(
        self,
        name: str,
        auto_pull: bool = False
    ) -> Dict[str, Any]:
        """
        Ensure a model is available, optionally pulling if needed.
        
        Args:
            name: Model name
            auto_pull: Whether to pull model if not installed
            
        Returns:
            Model info
            
        Raises:
            Exception: If model not available and auto_pull is False
        """
        model = await self.registry.get_model_by_name(name)
        
        if model and model.get("installed"):
            return model
        
        if not auto_pull:
            raise Exception(f"Model {name} not installed")
        
        # Pull model
        logger.info(f"Pulling model {name}...")
        
        async with OllamaClient() as client:
            async for progress in client.pull_model(name):
                status = progress.get("status", "")
                if "downloading" in status.lower():
                    logger.info(f"Pulling {name}: {status}")
        
        # Register after pulling
        await self.sync_models()
        
        model = await self.registry.get_model_by_name(name)
        return model
    
    async def select_model_for_task(
        self,
        task_type: str,
        fallback: Optional[str] = None
    ) -> Optional[str]:
        """
        Select best model for a task type.
        
        Args:
            task_type: Type of task (math, code, etc.)
            fallback: Fallback model name if none found
            
        Returns:
            Model name or None
            
        Example:
            model = await manager.select_model_for_task("math")
            if model:
                # Use model for math task
        """
        best = await self.registry.get_best_model_for_task(task_type)
        
        if best:
            return best["name"]
        
        if fallback:
            logger.warning(
                f"No model found for task {task_type}, using fallback {fallback}"
            )
            return fallback
        
        return None
    
    async def generate(
        self,
        model_name: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Generate completion using a model.
        
        Updates last_used timestamp in registry.
        
        Args:
            model_name: Model to use
            prompt: User prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        # Update last used
        model = await self.registry.get_model_by_name(model_name)
        if model:
            await self.registry.update_last_used(model["model_id"])
        
        # Generate
        async with OllamaClient() as client:
            response = await client.generate(model_name, prompt, **kwargs)
            return response.get("response", "")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get model manager statistics.
        
        Returns:
            Dict with various counts and metrics
        """
        registry_stats = await self.registry.get_model_stats()
        
        # Try to get Ollama status
        ollama_healthy = False
        try:
            async with OllamaClient() as client:
                ollama_healthy = await client.health_check()
        except Exception:
            pass
        
        return {
            **registry_stats,
            "ollama_healthy": ollama_healthy
        }
