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
            "temperature": 0.1 if response_format == "json" else 0.7,
            "num_predict": 2048
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
            "temperature": 0.1 if response_format == "json" else 0.7,
            "num_predict": 2048
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
