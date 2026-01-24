"""
Vision module configuration
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class VisionConfig:
    """Configuration for vision analysis"""
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llava:34b"
    timeout: int = 120  # seconds
    max_retries: int = 2
    
    # Paths
    intake_pending_path: str = "/opt/mythos/intake/pending"
    intake_processed_path: str = "/opt/mythos/intake/processed"
    intake_failed_path: str = "/opt/mythos/intake/failed"
    assets_path: str = "/opt/mythos/assets/images"
    
    # Defaults for sales
    default_pickup_location: str = "Magro's Restaurant & Pizzeria, 104 East Main Street, Norwich NY"
    default_pickup_contact: str = "Hannah"
    default_payment_method: str = "cash"


_config: Optional[VisionConfig] = None


def get_config() -> VisionConfig:
    """Get or create the vision configuration"""
    global _config
    
    if _config is None:
        _config = VisionConfig(
            ollama_host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            ollama_model=os.getenv('OLLAMA_VISION_MODEL', 'llava:34b'),
            timeout=int(os.getenv('OLLAMA_TIMEOUT', '120')),
            intake_pending_path=os.getenv('MYTHOS_INTAKE_PENDING', '/opt/mythos/intake/pending'),
            intake_processed_path=os.getenv('MYTHOS_INTAKE_PROCESSED', '/opt/mythos/intake/processed'),
            intake_failed_path=os.getenv('MYTHOS_INTAKE_FAILED', '/opt/mythos/intake/failed'),
            assets_path=os.getenv('MYTHOS_ASSETS_PATH', '/opt/mythos/assets/images'),
            default_pickup_location=os.getenv('DEFAULT_PICKUP_LOCATION', 
                "Magro's Restaurant & Pizzeria, 104 East Main Street, Norwich NY"),
            default_pickup_contact=os.getenv('DEFAULT_PICKUP_CONTACT', 'Hannah'),
            default_payment_method=os.getenv('DEFAULT_PAYMENT_METHOD', 'cash'),
        )
    
    return _config


def reload_config() -> VisionConfig:
    """Force reload configuration from environment"""
    global _config
    _config = None
    return get_config()
