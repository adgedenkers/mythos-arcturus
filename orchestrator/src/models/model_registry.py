"""
Model Registry

Database-backed registry for LLM models.
Tracks installed models, capabilities, and metadata.

Example:
    registry = ModelRegistry()
    await registry.register_model("llama3.1:70b", provider="ollama")
    model = await registry.get_model("llama3_70b")
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from utils import generate_id, safe_json_dumps, safe_json_loads

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Registry for managing models in the database.
    
    Provides CRUD operations for models and their capabilities.
    """
    
    @staticmethod
    def normalize_model_id(name: str) -> str:
        """
        Convert model name to safe model_id.
        
        Args:
            name: Model name (e.g., "llama3.1:70b")
            
        Returns:
            Safe model_id (e.g., "llama3_1_70b")
            
        Example:
            >>> ModelRegistry.normalize_model_id("llama3.1:70b")
            'llama3_1_70b'
        """
        return name.replace(":", "_").replace(".", "_").replace("-", "_")
    
    async def register_model(
        self,
        name: str,
        provider: str = "ollama",
        size_params: Optional[str] = None,
        context_window: Optional[int] = None,
        metadata: Optional[Dict] = None,
        mark_installed: bool = True
    ) -> str:
        """
        Register a model in the database.
        
        Args:
            name: Model name
            provider: Model provider (ollama, openai, etc.)
            size_params: Parameter size (e.g., "70B")
            context_window: Context window size
            metadata: Additional metadata
            mark_installed: Whether to mark as installed
            
        Returns:
            model_id
            
        Example:
            model_id = await registry.register_model(
                "llama3.1:70b",
                size_params="70B",
                context_window=128000
            )
        """
        model_id = self.normalize_model_id(name)
        
        now = datetime.now()
        metadata_json = safe_json_dumps(metadata or {})
        
        await db.execute("""
            INSERT INTO orch_models (
                model_id, name, provider, size_params, context_window,
                installed, installed_at, metadata, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (model_id) DO UPDATE SET
                name = EXCLUDED.name,
                provider = EXCLUDED.provider,
                size_params = EXCLUDED.size_params,
                context_window = EXCLUDED.context_window,
                installed = EXCLUDED.installed,
                installed_at = EXCLUDED.installed_at,
                metadata = EXCLUDED.metadata
        """, model_id, name, provider, size_params, context_window,
             mark_installed, now if mark_installed else None, metadata_json, now)
        
        logger.info(f"Registered model: {name} (id: {model_id})")
        return model_id
    
    async def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get model by ID.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model dict or None
        """
        row = await db.fetchrow("""
            SELECT * FROM orch_models WHERE model_id = $1
        """, model_id)
        
        if row:
            return dict(row)
        return None
    
    async def get_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get model by name.
        
        Args:
            name: Model name
            
        Returns:
            Model dict or None
        """
        model_id = self.normalize_model_id(name)
        return await self.get_model(model_id)
    
    async def list_models(
        self,
        provider: Optional[str] = None,
        installed_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all models.
        
        Args:
            provider: Filter by provider
            installed_only: Only return installed models
            
        Returns:
            List of model dicts
        """
        conditions = []
        params = []
        
        if provider:
            conditions.append(f"provider = ${len(params) + 1}")
            params.append(provider)
        
        if installed_only:
            conditions.append("installed = true")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        rows = await db.fetch(f"""
            SELECT * FROM orch_models
            {where_clause}
            ORDER BY name
        """, *params)
        
        return [dict(row) for row in rows]
    
    async def mark_installed(self, model_id: str, installed: bool = True):
        """
        Mark model as installed or uninstalled.
        
        Args:
            model_id: Model identifier
            installed: Installation status
        """
        now = datetime.now() if installed else None
        
        await db.execute("""
            UPDATE orch_models
            SET installed = $1, installed_at = $2
            WHERE model_id = $3
        """, installed, now, model_id)
        
        logger.info(f"Model {model_id} marked as {'installed' if installed else 'uninstalled'}")
    
    async def update_last_used(self, model_id: str):
        """
        Update last_used timestamp for a model.
        
        Args:
            model_id: Model identifier
        """
        await db.execute("""
            UPDATE orch_models
            SET last_used = $1
            WHERE model_id = $2
        """, datetime.now(), model_id)
    
    async def delete_model(self, model_id: str) -> bool:
        """
        Delete a model from registry.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if deleted
        """
        try:
            await db.execute("""
                DELETE FROM orch_models WHERE model_id = $1
            """, model_id)
            
            logger.info(f"Deleted model: {model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {e}")
            return False
    
    async def add_capability(
        self,
        model_id: str,
        task_type: str,
        quality_score: Optional[float] = None,
        speed_tier: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Add capability for a model.
        
        Args:
            model_id: Model identifier
            task_type: Type of task (math, code, dates, etc.)
            quality_score: Quality score 0.0-1.0
            speed_tier: Speed tier (fast, medium, slow)
            notes: Additional notes
            
        Returns:
            capability_id
        """
        capability_id = generate_id("cap")
        
        await db.execute("""
            INSERT INTO orch_model_capabilities (
                capability_id, model_id, task_type,
                quality_score, speed_tier, notes, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, capability_id, model_id, task_type, quality_score,
             speed_tier, notes, datetime.now())
        
        logger.info(f"Added capability {task_type} for model {model_id}")
        return capability_id
    
    async def get_capabilities(
        self,
        model_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all capabilities for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            List of capability dicts
        """
        rows = await db.fetch("""
            SELECT * FROM orch_model_capabilities
            WHERE model_id = $1
            ORDER BY task_type
        """, model_id)
        
        return [dict(row) for row in rows]
    
    async def get_best_model_for_task(
        self,
        task_type: str,
        installed_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get best model for a specific task type.
        
        Args:
            task_type: Type of task
            installed_only: Only consider installed models
            
        Returns:
            Model dict with highest quality score for task
        """
        installed_filter = "AND m.installed = true" if installed_only else ""
        
        row = await db.fetchrow(f"""
            SELECT m.*, c.quality_score, c.speed_tier
            FROM orch_models m
            JOIN orch_model_capabilities c ON m.model_id = c.model_id
            WHERE c.task_type = $1 {installed_filter}
            ORDER BY c.quality_score DESC NULLS LAST
            LIMIT 1
        """, task_type)
        
        if row:
            return dict(row)
        return None
    
    async def get_model_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict with total, installed, by provider counts
        """
        stats = await db.fetchrow("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE installed = true) as installed,
                COUNT(DISTINCT provider) as providers
            FROM orch_models
        """)
        
        return dict(stats)
