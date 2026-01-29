"""
IRIS Configuration

All configuration loaded from environment variables.
Uses existing /opt/mythos/.env variable names where possible.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for IRIS core systems."""
    
    # Database connections
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    redis_host: str
    redis_port: int
    
    # Ollama (LLM)
    ollama_host: str
    ollama_model: str
    
    # Telegram
    telegram_bot_token: str
    telegram_user_id: int  # Ka'tuar'el's user ID
    telegram_seraphe_id: Optional[int]  # Seraphe's user ID
    
    # Docker
    docker_socket: str
    sandbox_image: str
    sandbox_network: str
    
    # Paths
    workshop_path: str
    sandbox_path: str
    apps_path: str
    proposals_path: str
    journal_path: str
    
    # Loop timing
    cycle_interval_active: float  # seconds between cycles when active
    cycle_interval_reflection: float  # seconds between cycles in reflection mode
    
    # Thresholds
    presence_timeout: int  # seconds of silence before switching from presence to available
    available_timeout: int  # seconds of silence before switching from available to background
    reflection_start_hour: int  # hour (24h) when reflection mode can start
    reflection_end_hour: int  # hour (24h) when reflection mode ends
    
    @classmethod
    def from_environment(cls) -> "Config":
        """Load configuration from environment variables."""
        
        # Handle Telegram IDs - support both old and new naming
        telegram_user = os.getenv("TELEGRAM_USER_ID") or os.getenv("TELEGRAM_ID_KA") or "0"
        telegram_seraphe = os.getenv("TELEGRAM_SERAPHE_ID") or os.getenv("TELEGRAM_ID_SERAPHE") or "0"
        
        return cls(
            # Database - uses existing .env names
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "mythos"),
            postgres_user=os.getenv("POSTGRES_USER", "postgres"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", ""),
            
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", ""),
            
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            
            # Ollama - uses existing .env names
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:32b"),
            
            # Telegram - support both naming conventions
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_user_id=int(telegram_user),
            telegram_seraphe_id=int(telegram_seraphe) if telegram_seraphe != "0" else None,
            
            # Docker
            docker_socket=os.getenv("DOCKER_SOCKET", "/var/run/docker.sock"),
            sandbox_image=os.getenv("SANDBOX_IMAGE", "iris-sandbox:latest"),
            sandbox_network=os.getenv("SANDBOX_NETWORK", "iris-internal"),
            
            # Paths
            workshop_path=os.getenv("WORKSHOP_PATH", "/iris/workshop"),
            sandbox_path=os.getenv("SANDBOX_PATH", "/iris/sandbox"),
            apps_path=os.getenv("APPS_PATH", "/iris/apps"),
            proposals_path=os.getenv("PROPOSALS_PATH", "/iris/proposals"),
            journal_path=os.getenv("JOURNAL_PATH", "/iris/journal"),
            
            # Loop timing
            cycle_interval_active=float(os.getenv("CYCLE_INTERVAL_ACTIVE", "5.0")),
            cycle_interval_reflection=float(os.getenv("CYCLE_INTERVAL_REFLECTION", "30.0")),
            
            # Thresholds
            presence_timeout=int(os.getenv("PRESENCE_TIMEOUT", "300")),  # 5 minutes
            available_timeout=int(os.getenv("AVAILABLE_TIMEOUT", "3600")),  # 1 hour
            reflection_start_hour=int(os.getenv("REFLECTION_START_HOUR", "22")),  # 10pm
            reflection_end_hour=int(os.getenv("REFLECTION_END_HOUR", "6")),  # 6am
        )
    
    def get_postgres_dsn(self) -> str:
        """Get PostgreSQL connection string."""
        # Handle socket path vs host
        if self.postgres_host.startswith("/"):
            # Unix socket
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@/{self.postgres_db}?host={self.postgres_host}"
        else:
            # TCP connection
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
