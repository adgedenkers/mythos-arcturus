#!/bin/bash
# ============================================================================
# PHASE 1: VISION INFRASTRUCTURE
# Creates the Mythos Vision module for image analysis via Ollama
# ============================================================================

set -e

PHASE="1"
PHASE_NAME="Vision Infrastructure"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/mythos/_backups/phase_${PHASE}_${TIMESTAMP}"
LOG_FILE="/var/log/mythos_phase_${PHASE}.log"

# Configuration
MYTHOS_BASE="/opt/mythos"
VENV_PYTHON="/opt/mythos/.venv/bin/python3"
SERVICE_USER="adge"
OLLAMA_HOST="http://localhost:11434"
OLLAMA_MODEL="llava-llama3:latest"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"; exit 1; }

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

preflight_checks() {
    log "Running pre-flight checks..."
    
    # Check Ollama is running
    if ! curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
        error "Ollama is not running at $OLLAMA_HOST"
    fi
    success "Ollama is running"
    
    # Check vision model exists
    if ! curl -s "$OLLAMA_HOST/api/tags" | grep -q "llava"; then
        error "No vision model (llava) found in Ollama"
    fi
    success "Vision model available"
    
    # Check venv exists
    if [ ! -f "$VENV_PYTHON" ]; then
        error "Python venv not found at $VENV_PYTHON"
    fi
    success "Python venv found"
    
    # Check disk space (need at least 1GB free)
    FREE_SPACE=$(df /opt/mythos | tail -1 | awk '{print $4}')
    if [ "$FREE_SPACE" -lt 1048576 ]; then
        error "Less than 1GB free space on /opt/mythos"
    fi
    success "Sufficient disk space"
    
    success "Pre-flight checks passed"
}

# ============================================================================
# BACKUP
# ============================================================================

create_backup() {
    log "Creating backup at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup .env if it exists
    if [ -f "$MYTHOS_BASE/.env" ]; then
        cp "$MYTHOS_BASE/.env" "$BACKUP_DIR/.env.bak"
    fi
    
    # Backup assets/asset_store.py
    if [ -f "$MYTHOS_BASE/assets/asset_store.py" ]; then
        cp "$MYTHOS_BASE/assets/asset_store.py" "$BACKUP_DIR/asset_store.py.bak"
    fi
    
    # Record manifest
    cat > "$BACKUP_DIR/manifest.txt" << EOF
Phase $PHASE Backup - $TIMESTAMP
==============================
Files backed up:
$(ls -la "$BACKUP_DIR")

To rollback: $0 rollback
EOF
    
    success "Backup created at $BACKUP_DIR"
}

# ============================================================================
# CREATE VISION MODULE
# ============================================================================

create_vision_module() {
    log "Creating vision module..."
    
    mkdir -p "$MYTHOS_BASE/vision/prompts"
    
    # -------------------------------------------------------------------------
    # vision/__init__.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/__init__.py" << 'PYEOF'
"""
Mythos Vision Module
====================
Provides image analysis capabilities via Ollama vision models.

Usage:
    from vision import analyze_image
    from vision.prompts import sales, journal, chat
    
    # For sales item extraction
    result = analyze_image(photos, prompt=sales.ITEM_ANALYSIS)
    
    # For journal entry
    result = analyze_image(photos, prompt=journal.DESCRIBE_FOR_JOURNAL)
    
    # For general chat
    result = analyze_image(photos, prompt=chat.GENERAL_DESCRIPTION)
"""

from .core import analyze_image, analyze_image_async, test_vision
from .config import get_config, VisionConfig

__all__ = [
    'analyze_image',
    'analyze_image_async', 
    'test_vision',
    'get_config',
    'VisionConfig'
]

__version__ = '1.0.0'
PYEOF

    # -------------------------------------------------------------------------
    # vision/config.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/config.py" << 'PYEOF'
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
    ollama_model: str = "llava-llama3:latest"
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
            ollama_model=os.getenv('OLLAMA_VISION_MODEL', 'llava-llama3:latest'),
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
PYEOF

    # -------------------------------------------------------------------------
    # vision/core.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/core.py" << 'PYEOF'
"""
Core vision analysis functionality using Ollama
"""

import base64
import json
import logging
import re
import httpx
from pathlib import Path
from typing import Union, Optional

from .config import get_config

logger = logging.getLogger(__name__)


def _load_image_as_base64(image_path: Union[str, Path]) -> str:
    """Load an image file and return as base64 string"""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def _extract_json_from_response(text: str) -> dict:
    """
    Extract JSON from model response, handling markdown code blocks
    and other common formatting issues.
    """
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    
    # Clean up common issues
    text = text.strip()
    
    # Try to parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        # Return as plain text if we can't parse
        return {"raw_response": text, "parse_error": True}


def analyze_image(
    images: Union[str, Path, list],
    prompt: str,
    model: Optional[str] = None,
    response_format: str = "auto",
    timeout: Optional[int] = None
) -> Union[str, dict]:
    """
    Analyze one or more images using Ollama vision model.
    
    Args:
        images: Single image path or list of image paths
        prompt: Analysis prompt (use prompts from vision.prompts module)
        model: Override default model (default: from config)
        response_format: "text", "json", or "auto" (detect from prompt)
        timeout: Override default timeout in seconds
    
    Returns:
        String for text format, dict for json format
    
    Example:
        from vision import analyze_image
        from vision.prompts import sales
        
        result = analyze_image(
            ["photo1.jpg", "photo2.jpg", "photo3.jpg"],
            prompt=sales.ITEM_ANALYSIS
        )
    """
    config = get_config()
    
    model = model or config.ollama_model
    timeout = timeout or config.timeout
    
    # Normalize images to list
    if isinstance(images, (str, Path)):
        images = [images]
    
    # Load images as base64
    image_data = []
    for img in images:
        try:
            image_data.append(_load_image_as_base64(img))
        except Exception as e:
            logger.error(f"Failed to load image {img}: {e}")
            raise
    
    # Determine response format
    if response_format == "auto":
        # If prompt mentions JSON, expect JSON response
        if "json" in prompt.lower() or "JSON" in prompt:
            response_format = "json"
        else:
            response_format = "text"
    
    # Build request
    request_body = {
        "model": model,
        "prompt": prompt,
        "images": image_data,
        "stream": False,
        "options": {
            "temperature": 0.1 if response_format == "json" else 0.7
        }
    }
    
    # Make request
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                f"{config.ollama_host}/api/generate",
                json=request_body
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            if response_format == "json":
                return _extract_json_from_response(response_text)
            else:
                return response_text.strip()
                
    except httpx.TimeoutException:
        logger.error(f"Ollama request timed out after {timeout}s")
        raise TimeoutError(f"Vision analysis timed out after {timeout} seconds")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error: {e}")
        raise
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        raise


async def analyze_image_async(
    images: Union[str, Path, list],
    prompt: str,
    model: Optional[str] = None,
    response_format: str = "auto",
    timeout: Optional[int] = None
) -> Union[str, dict]:
    """
    Async version of analyze_image.
    
    Same parameters and return values as analyze_image.
    """
    config = get_config()
    
    model = model or config.ollama_model
    timeout = timeout or config.timeout
    
    # Normalize images to list
    if isinstance(images, (str, Path)):
        images = [images]
    
    # Load images as base64
    image_data = []
    for img in images:
        try:
            image_data.append(_load_image_as_base64(img))
        except Exception as e:
            logger.error(f"Failed to load image {img}: {e}")
            raise
    
    # Determine response format
    if response_format == "auto":
        if "json" in prompt.lower() or "JSON" in prompt:
            response_format = "json"
        else:
            response_format = "text"
    
    # Build request
    request_body = {
        "model": model,
        "prompt": prompt,
        "images": image_data,
        "stream": False,
        "options": {
            "temperature": 0.1 if response_format == "json" else 0.7
        }
    }
    
    # Make async request
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{config.ollama_host}/api/generate",
                json=request_body
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            if response_format == "json":
                return _extract_json_from_response(response_text)
            else:
                return response_text.strip()
                
    except httpx.TimeoutException:
        logger.error(f"Ollama request timed out after {timeout}s")
        raise TimeoutError(f"Vision analysis timed out after {timeout} seconds")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error: {e}")
        raise
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        raise


def test_vision(image_path: Optional[str] = None) -> dict:
    """
    Test that vision analysis is working.
    
    Args:
        image_path: Optional path to test image. If not provided,
                   just tests Ollama connectivity.
    
    Returns:
        Dict with test results
    """
    config = get_config()
    results = {
        "ollama_host": config.ollama_host,
        "model": config.ollama_model,
        "connectivity": False,
        "model_available": False,
        "vision_working": False,
        "error": None
    }
    
    try:
        # Test connectivity
        with httpx.Client(timeout=10) as client:
            response = client.get(f"{config.ollama_host}/api/tags")
            response.raise_for_status()
            results["connectivity"] = True
            
            # Check model is available
            tags = response.json()
            models = [m["name"] for m in tags.get("models", [])]
            results["available_models"] = models
            results["model_available"] = config.ollama_model in models
            
            # Test vision if image provided
            if image_path and results["model_available"]:
                result = analyze_image(
                    image_path,
                    "Describe this image in one sentence.",
                    response_format="text"
                )
                results["vision_working"] = len(result) > 10
                results["test_response"] = result[:200]
                
    except Exception as e:
        results["error"] = str(e)
    
    return results
PYEOF

    # -------------------------------------------------------------------------
    # vision/prompts/__init__.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/prompts/__init__.py" << 'PYEOF'
"""
Vision analysis prompts for different modes.

Each prompt module provides specialized prompts for specific use cases.
"""

from . import sales
from . import journal
from . import chat
from . import symbols
from . import documents

__all__ = ['sales', 'journal', 'chat', 'symbols', 'documents']
PYEOF

    # -------------------------------------------------------------------------
    # vision/prompts/sales.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/prompts/sales.py" << 'PYEOF'
"""
Prompts for sales item analysis
"""

ITEM_ANALYSIS = """You are analyzing photos of an item being listed for sale.
Examine all photos carefully to extract accurate information.

TASK: Extract item details and generate marketplace listing content.

RULES:
- Read text from labels/tags exactly as written
- If you cannot determine something with confidence, use null
- Be conservative with condition assessment
- Price should reflect fair resale value (not retail)
- For shoes, check for box/packaging in photos

OUTPUT FORMAT - Respond with ONLY this JSON, no other text:

{
  "item_type": "clothing|shoes|other",
  "brand": "string or null",
  "model": "string or null (style name if visible)",
  "category": "string (jeans, sneakers, boots, shirt, dress, jacket, etc.)",
  "gender_category": "mens|womens|unisex|kids",
  "size_label": "string (exactly as written on tag)",
  "size_numeric": number or null,
  "size_width": "narrow|medium|wide|null (shoes only)",
  "condition": "new_with_tags|new_without_tags|like_new|gently_used|used|well_worn",
  "colors": ["array", "of", "colors"],
  "materials": ["array", "of", "materials"] or null,
  "features": {
    "waterproof": boolean or null,
    "heel_height": "flat|low|mid|high|null",
    "closure_type": "lace|slip-on|zipper|button|velcro|null",
    "style": "string describing style (bootcut, skinny, athletic, etc.)",
    "other": "any other notable features"
  },
  "country_of_manufacture": "string or null",
  "care_instructions": "string or null (from care label)",
  "estimated_price": number (fair USD resale price),
  "confidence_score": 0.0-1.0 (your confidence in extraction accuracy),
  "inferred_fields": ["list", "of", "fields", "that", "were", "guessed"],
  "extraction_notes": "any notes about what you couldn't determine",
  "title": "Marketplace title, 60-80 chars, brand + item + size + condition",
  "description": "Compelling description 100-200 words. Include: brand, size, condition, materials, features. Professional but friendly tone."
}"""


ITEM_ANALYSIS_SIMPLE = """Analyze this item for sale. Extract:
- Type (clothing/shoes/other)
- Brand
- Size
- Condition
- Estimated price

Respond in JSON format."""


CONDITION_CHECK = """Examine this item's condition carefully.
Look for: wear, stains, damage, tags, original packaging.

Rate the condition as one of:
- new_with_tags: Never worn, original tags attached
- new_without_tags: Never worn, no tags
- like_new: Worn once or twice, no visible wear
- gently_used: Light wear, good condition
- used: Normal wear, still functional
- well_worn: Significant wear, still usable

Respond with just the condition rating and a brief explanation."""


BRAND_IDENTIFICATION = """Identify the brand of this item.
Look for logos, labels, tags, and distinctive design elements.

Respond with:
- Brand name
- Confidence (high/medium/low)
- How you identified it"""
PYEOF

    # -------------------------------------------------------------------------
    # vision/prompts/journal.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/prompts/journal.py" << 'PYEOF'
"""
Prompts for journal/personal documentation
"""

DESCRIBE_FOR_JOURNAL = """Describe this image for a personal journal entry.
Write in a warm, reflective tone as if describing a meaningful moment.
Focus on:
- What's happening in the image
- The mood or atmosphere
- Sensory details (colors, textures, light)
- What makes this moment noteworthy

Write 2-3 paragraphs, flowing and personal."""


MEMORY_CAPTURE = """This photo captures a memory. Help preserve it by describing:
1. What's in the image (people, places, objects)
2. The setting and time of day (if apparent)
3. The emotional tone or mood
4. Any details that might be forgotten over time

Write as if helping someone remember this moment years from now."""


DAILY_LOG = """Add this image to a daily log. Provide:
- Brief description (1-2 sentences)
- Category (meal, work, nature, social, creative, other)
- Mood/energy level suggested by the image
- One-word tag

Format as structured notes."""
PYEOF

    # -------------------------------------------------------------------------
    # vision/prompts/chat.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/prompts/chat.py" << 'PYEOF'
"""
Prompts for general chat/conversation about images
"""

GENERAL_DESCRIPTION = """Describe what you see in this image.
Be conversational and helpful, as if chatting with a friend.
Point out interesting details they might want to know about."""


DETAILED_ANALYSIS = """Provide a detailed analysis of this image:
1. Main subject/focus
2. Setting/background
3. Colors and composition
4. Mood/atmosphere
5. Any text visible
6. Notable details

Be thorough but organized."""


QUICK_SUMMARY = """In 1-2 sentences, what's in this image?"""


QUESTION_ANSWER = """Look at this image and answer any questions about it.
Be specific and reference what you can actually see.
If you're unsure about something, say so."""


COMPARE_IMAGES = """Compare these images and describe:
- What's similar
- What's different
- Any progression or change
- Which stands out and why"""
PYEOF

    # -------------------------------------------------------------------------
    # vision/prompts/symbols.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/prompts/symbols.py" << 'PYEOF'
"""
Prompts for symbolic/esoteric analysis (Seraphe mode)
"""

ESOTERIC_ANALYSIS = """Examine this image through a symbolic and esoteric lens.
Consider:
- Sacred geometry patterns
- Archetypal symbols
- Numerological significance
- Color symbolism
- Natural symbols (animals, plants, elements)
- Cultural or religious iconography

Describe what resonates spiritually or symbolically.
Speak with depth but accessibility."""


DREAM_INTERPRETATION = """This image relates to a dream or vision.
Analyze it symbolically:
- Key symbols and their traditional meanings
- Personal significance (what might it mean to the dreamer)
- Archetypal themes
- Messages or guidance it might contain

Be insightful and intuitive in your interpretation."""


TAROT_STYLE = """Describe this image as if it were a tarot card:
- What archetype does it represent?
- Upright meaning (positive aspects)
- Shadow meaning (challenges)
- Advice it offers
- Element and astrological correspondence (if apparent)"""


SYNCHRONICITY_CHECK = """Examine this image for synchronistic meaning.
What patterns, symbols, or messages might the universe be communicating?
Consider timing, repetition, and meaningful coincidence."""
PYEOF

    # -------------------------------------------------------------------------
    # vision/prompts/documents.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/vision/prompts/documents.py" << 'PYEOF'
"""
Prompts for document/text analysis
"""

READ_DOCUMENT = """Extract all readable text from this document.
Preserve the structure and formatting as much as possible.
Note any text that's unclear or partially visible."""


SUMMARIZE_DOCUMENT = """Read this document and provide:
1. Document type (letter, form, certificate, etc.)
2. Key information (names, dates, numbers)
3. Brief summary of contents
4. Any notable or important details"""


GENEALOGY_DOCUMENT = """This is a genealogical document. Extract:
- Names (with roles: parent, child, spouse, witness)
- Dates (birth, death, marriage, etc.)
- Places mentioned
- Relationships indicated
- Document type and date

Format as structured data:
{
  "document_type": "",
  "document_date": "",
  "people": [
    {"name": "", "role": "", "dates": {}, "notes": ""}
  ],
  "places": [],
  "relationships": [],
  "other_details": ""
}"""


HANDWRITING_TRANSCRIPTION = """Transcribe the handwritten text in this image.
- Use [unclear] for words you can't read
- Preserve line breaks where apparent
- Note any crossed-out or corrected text
- Include any marginalia or notes"""


RECEIPT_EXTRACTION = """Extract information from this receipt:
- Store/vendor name
- Date and time
- Items and prices
- Subtotal, tax, total
- Payment method
- Any other relevant details

Format as JSON."""
PYEOF

    success "Vision module created"
}

# ============================================================================
# CREATE INTAKE DIRECTORIES
# ============================================================================

create_directories() {
    log "Creating intake directories..."
    
    mkdir -p "$MYTHOS_BASE/intake/pending"
    mkdir -p "$MYTHOS_BASE/intake/processed"
    mkdir -p "$MYTHOS_BASE/intake/failed"
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$MYTHOS_BASE/intake"
    chmod -R 755 "$MYTHOS_BASE/intake"
    
    success "Intake directories created"
}

# ============================================================================
# UPDATE ENVIRONMENT
# ============================================================================

update_environment() {
    log "Updating environment variables..."
    
    ENV_FILE="$MYTHOS_BASE/.env"
    
    # Check if variables already exist
    if grep -q "OLLAMA_HOST" "$ENV_FILE" 2>/dev/null; then
        warn "OLLAMA_HOST already in .env, skipping"
    else
        cat >> "$ENV_FILE" << EOF

# Vision Module Configuration (added by Phase 1)
OLLAMA_HOST=http://localhost:11434
OLLAMA_VISION_MODEL=llava-llama3:latest
OLLAMA_TIMEOUT=120

# Intake Paths
MYTHOS_INTAKE_PENDING=/opt/mythos/intake/pending
MYTHOS_INTAKE_PROCESSED=/opt/mythos/intake/processed
MYTHOS_INTAKE_FAILED=/opt/mythos/intake/failed
MYTHOS_ASSETS_PATH=/opt/mythos/assets/images

# Sales Defaults
DEFAULT_PICKUP_LOCATION=Magro's Restaurant & Pizzeria, 104 East Main Street, Norwich NY
DEFAULT_PICKUP_CONTACT=Hannah
DEFAULT_PAYMENT_METHOD=cash
EOF
        success "Environment variables added"
    fi
}

# ============================================================================
# INSTALL PYTHON DEPENDENCIES
# ============================================================================

install_dependencies() {
    log "Checking Python dependencies..."
    
    # httpx is needed for Ollama API calls
    if ! "$VENV_PYTHON" -c "import httpx" 2>/dev/null; then
        log "Installing httpx..."
        "$MYTHOS_BASE/.venv/bin/pip" install httpx
        success "httpx installed"
    else
        success "httpx already installed"
    fi
}

# ============================================================================
# SET PERMISSIONS
# ============================================================================

set_permissions() {
    log "Setting permissions..."
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$MYTHOS_BASE/vision"
    chmod -R 755 "$MYTHOS_BASE/vision"
    
    success "Permissions set"
}

# ============================================================================
# VALIDATION
# ============================================================================

validate_phase() {
    log "Validating Phase $PHASE installation..."
    
    ERRORS=0
    
    # Check module can be imported
    if ! "$VENV_PYTHON" -c "import sys; sys.path.insert(0, '/opt/mythos'); from vision import analyze_image" 2>/dev/null; then
        error "Failed to import vision module"
        ERRORS=$((ERRORS + 1))
    else
        success "Vision module imports correctly"
    fi
    
    # Check prompts
    if ! "$VENV_PYTHON" -c "import sys; sys.path.insert(0, '/opt/mythos'); from vision.prompts import sales, journal, chat" 2>/dev/null; then
        error "Failed to import prompt modules"
        ERRORS=$((ERRORS + 1))
    else
        success "Prompt modules import correctly"
    fi
    
    # Check config
    if ! "$VENV_PYTHON" -c "import sys; sys.path.insert(0, '/opt/mythos'); from vision.config import get_config; c = get_config(); print(c.ollama_host)" 2>/dev/null; then
        error "Failed to load config"
        ERRORS=$((ERRORS + 1))
    else
        success "Config loads correctly"
    fi
    
    # Check directories exist
    for dir in pending processed failed; do
        if [ ! -d "$MYTHOS_BASE/intake/$dir" ]; then
            error "Directory missing: $MYTHOS_BASE/intake/$dir"
            ERRORS=$((ERRORS + 1))
        fi
    done
    success "Intake directories exist"
    
    # Test Ollama connectivity
    log "Testing Ollama connectivity..."
    TEST_RESULT=$("$VENV_PYTHON" << 'PYTEST'
import sys
sys.path.insert(0, '/opt/mythos')
from vision import test_vision
result = test_vision()
if result['connectivity'] and result['model_available']:
    print("OK")
else:
    print(f"FAIL: {result.get('error', 'Model not available')}")
PYTEST
)
    
    if [ "$TEST_RESULT" = "OK" ]; then
        success "Ollama connectivity test passed"
    else
        warn "Ollama test: $TEST_RESULT"
    fi
    
    if [ $ERRORS -gt 0 ]; then
        error "Validation failed with $ERRORS errors"
    fi
    
    success "Validation complete"
}

# ============================================================================
# ROLLBACK
# ============================================================================

rollback() {
    warn "Rolling back Phase $PHASE..."
    
    # Find most recent backup
    LATEST_BACKUP=$(ls -td /opt/mythos/_backups/phase_${PHASE}_* 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error "No backup found for Phase $PHASE"
    fi
    
    log "Using backup: $LATEST_BACKUP"
    
    # Remove vision module
    if [ -d "$MYTHOS_BASE/vision" ]; then
        rm -rf "$MYTHOS_BASE/vision"
        success "Removed vision module"
    fi
    
    # Remove intake directories (only if empty)
    for dir in pending processed failed; do
        if [ -d "$MYTHOS_BASE/intake/$dir" ] && [ -z "$(ls -A $MYTHOS_BASE/intake/$dir)" ]; then
            rmdir "$MYTHOS_BASE/intake/$dir" 2>/dev/null || true
        fi
    done
    rmdir "$MYTHOS_BASE/intake" 2>/dev/null || true
    
    # Restore .env if backed up
    if [ -f "$LATEST_BACKUP/.env.bak" ]; then
        cp "$LATEST_BACKUP/.env.bak" "$MYTHOS_BASE/.env"
        success "Restored .env"
    fi
    
    success "Rollback complete"
}

# ============================================================================
# TEST COMMAND
# ============================================================================

run_test() {
    log "Running vision test..."
    
    "$VENV_PYTHON" << 'PYTEST'
import sys
sys.path.insert(0, '/opt/mythos')

from vision import test_vision
from vision.prompts import sales, journal, chat

print("\n=== Vision Module Test ===\n")

# Test connectivity
result = test_vision()
print(f"Ollama Host: {result['ollama_host']}")
print(f"Model: {result['model']}")
print(f"Connectivity: {'✓' if result['connectivity'] else '✗'}")
print(f"Model Available: {'✓' if result['model_available'] else '✗'}")

if result.get('available_models'):
    print(f"Available Models: {', '.join(result['available_models'])}")

if result.get('error'):
    print(f"Error: {result['error']}")

print("\n=== Prompt Modules ===\n")
print(f"Sales prompts: {len(dir(sales))} defined")
print(f"Journal prompts: {len(dir(journal))} defined")
print(f"Chat prompts: {len(dir(chat))} defined")

print("\n=== Sample Prompt ===\n")
print(sales.ITEM_ANALYSIS[:200] + "...")

print("\n✓ Vision module ready\n")
PYTEST
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}PHASE $PHASE: $PHASE_NAME${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
    
    case "${1:-install}" in
        install)
            preflight_checks
            create_backup
            create_vision_module
            create_directories
            update_environment
            install_dependencies
            set_permissions
            validate_phase
            
            echo ""
            success "Phase $PHASE complete!"
            echo ""
            echo "The vision module is now available at /opt/mythos/vision/"
            echo ""
            echo "Usage:"
            echo "  from vision import analyze_image"
            echo "  from vision.prompts import sales"
            echo "  result = analyze_image(['photo1.jpg'], prompt=sales.ITEM_ANALYSIS)"
            echo ""
            echo "Next steps:"
            echo "  1. Test: $0 test"
            echo "  2. If issues: $0 rollback"
            echo "  3. If OK: Proceed to Phase 2 (Telegram Integration)"
            ;;
        rollback)
            rollback
            ;;
        validate)
            validate_phase
            ;;
        test)
            run_test
            ;;
        *)
            echo "Usage: $0 [install|rollback|validate|test]"
            echo ""
            echo "Commands:"
            echo "  install   - Install Phase $PHASE (default)"
            echo "  rollback  - Revert to pre-installation state"
            echo "  validate  - Check installation integrity"
            echo "  test      - Run vision module tests"
            exit 1
            ;;
    esac
}

main "$@"
