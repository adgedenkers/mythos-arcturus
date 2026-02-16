"""
Configuration management for Mythos Orchestrator.

Uses pydantic-settings for type-safe environment variable handling.
All settings are loaded from /opt/mythos/orchestrator/.env file.

Example:
    from config import settings
    print(settings.DATABASE_URL)
    print(settings.OLLAMA_HOST)
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    Settings are validated at startup using Pydantic.
    """
    
    # Application
    APP_NAME: str = "Mythos Orchestrator"
    VERSION: str = "1.15.1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://adge@localhost:5432/mythos"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_MAX_RETRIES: int = 3
    
    # Paths (absolute paths required)
    DATA_DIR: str = "/opt/mythos/orchestrator/data"
    TEST_SUITES_DIR: str = "/opt/mythos/orchestrator/test_suites"
    RESULTS_DIR: str = "/opt/mythos/orchestrator/results"
    LOGS_DIR: str = "/opt/mythos/orchestrator/logs"
    
    # Model Defaults
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_MAX_TOKENS: int = 2000
    DEFAULT_MODEL: str = "qwen2.5:32b"
    
    # Performance
    MAX_PARALLEL_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 60
    ASYNC_POOL_SIZE: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_TO_FILE: bool = True
    LOG_TO_CONSOLE: bool = True
    
    class Config:
        """Pydantic config for settings."""
        env_file = "/opt/mythos/orchestrator/.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def get_data_path(self, filename: str) -> Path:
        """
        Get full path to data file.
        
        Args:
            filename: Name of the data file
            
        Returns:
            Path object for the file
            
        Example:
            >>> settings.get_data_path("models.json")
            Path('/opt/mythos/orchestrator/data/models.json')
        """
        return Path(self.DATA_DIR) / filename
    
    def get_test_suite_path(self, suite_name: str) -> Path:
        """
        Get full path to test suite file.
        
        Args:
            suite_name: Name of the test suite (without .json)
            
        Returns:
            Path object for the test suite file
            
        Example:
            >>> settings.get_test_suite_path("math_suite")
            Path('/opt/mythos/orchestrator/test_suites/math_suite.json')
        """
        filename = suite_name if suite_name.endswith('.json') else f"{suite_name}.json"
        return Path(self.TEST_SUITES_DIR) / filename
    
    def get_results_path(self, run_id: str) -> Path:
        """
        Get full path to results file.
        
        Args:
            run_id: Unique run identifier
            
        Returns:
            Path object for the results file
            
        Example:
            >>> settings.get_results_path("run_abc123")
            Path('/opt/mythos/orchestrator/results/run_abc123.json')
        """
        filename = run_id if run_id.endswith('.json') else f"{run_id}.json"
        return Path(self.RESULTS_DIR) / filename
    
    def get_log_path(self, log_name: str) -> Path:
        """
        Get full path to log file.
        
        Args:
            log_name: Name of the log file
            
        Returns:
            Path object for the log file
        """
        filename = log_name if log_name.endswith('.log') else f"{log_name}.log"
        return Path(self.LOGS_DIR) / filename
    
    def ensure_directories(self):
        """
        Ensure all required directories exist.
        Creates them if they don't exist.
        """
        directories = [
            self.DATA_DIR,
            self.TEST_SUITES_DIR,
            self.RESULTS_DIR,
            self.LOGS_DIR
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Global settings instance
# Import this in other modules: from config import settings
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()


def get_settings() -> Settings:
    """
    Get global settings instance.
    
    This function is provided for dependency injection in FastAPI.
    
    Returns:
        Global settings instance
        
    Example:
        from fastapi import Depends
        from config import get_settings, Settings
        
        @app.get("/info")
        def get_info(settings: Settings = Depends(get_settings)):
            return {"version": settings.VERSION}
    """
    return settings
