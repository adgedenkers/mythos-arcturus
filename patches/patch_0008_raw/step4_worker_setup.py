#!/usr/bin/env python3
"""
Step 4: Worker Process Setup

Creates:
- Worker directory structure
- Main worker.py entry point
- Individual worker modules (grid, embedding, vision, temporal, entity, summary)
- Systemd service files for each worker type
- __init__.py for module imports

Usage: python3 step4_worker_setup.py
"""

import os
import sys
from pathlib import Path

MYTHOS_BASE = Path("/opt/mythos")
WORKERS_DIR = MYTHOS_BASE / "workers"


def create_directory_structure():
    """Create workers directory structure"""
    print("  Creating directory structure...")
    
    WORKERS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"    ✓ {WORKERS_DIR}")
    
    return True


def create_init_file():
    """Create __init__.py for workers module"""
    
    content = '''"""
Mythos Workers Module

Worker processes for async extraction and analysis.
"""

from .grid_worker import process_grid_analysis
from .embedding_worker import process_embedding
from .vision_worker import process_vision
from .temporal_worker import process_temporal
from .entity_worker import process_entity
from .summary_worker import process_summary

__all__ = [
    "process_grid_analysis",
    "process_embedding", 
    "process_vision",
    "process_temporal",
    "process_entity",
    "process_summary"
]
'''
    
    file_path = WORKERS_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_worker_main():
    """Create the main worker entry point"""
    
    content = '''#!/usr/bin/env python3
"""
Mythos Worker Framework

Processes assignments from Redis streams.

Usage:
    python3 worker.py <worker_type>
    
Worker types:
    grid      - Arcturian Grid 9-node analysis
    embedding - Text embedding generation
    vision    - Photo/vision analysis
    temporal  - Temporal data extraction
    entity    - Entity resolution
    summary   - Conversation summary rebuilding
"""

import os
import sys
import json
import time
import signal
import logging
from datetime import datetime
from pathlib import Path

import redis
from dotenv import load_dotenv

# Load environment
load_dotenv("/opt/mythos/.env")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Worker registry
WORKER_TYPES = {
    "grid": {
        "stream": "mythos:assignments:grid_analysis",
        "group": "grid_workers",
        "module": "grid_worker",
        "function": "process_grid_analysis"
    },
    "embedding": {
        "stream": "mythos:assignments:embedding",
        "group": "embedding_workers",
        "module": "embedding_worker",
        "function": "process_embedding"
    },
    "vision": {
        "stream": "mythos:assignments:vision",
        "group": "vision_workers",
        "module": "vision_worker",
        "function": "process_vision"
    },
    "temporal": {
        "stream": "mythos:assignments:temporal",
        "group": "temporal_workers",
        "module": "temporal_worker",
        "function": "process_temporal"
    },
    "entity": {
        "stream": "mythos:assignments:entity",
        "group": "entity_workers",
        "module": "entity_worker",
        "function": "process_entity"
    },
    "summary": {
        "stream": "mythos:assignments:summary_rebuild",
        "group": "summary_workers",
        "module": "summary_worker",
        "function": "process_summary"
    }
}


class Worker:
    """Base worker class for processing assignments"""
    
    def __init__(self, worker_type: str):
        if worker_type not in WORKER_TYPES:
            raise ValueError(f"Unknown worker type: {worker_type}")
        
        self.worker_type = worker_type
        self.config = WORKER_TYPES[worker_type]
        self.logger = logging.getLogger(f"worker.{worker_type}")
        
        # Redis connection
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        
        # Generate unique consumer name
        self.consumer_name = f"{worker_type}_{os.getpid()}_{int(time.time())}"
        
        # Shutdown flag
        self.running = True
        
        # Load the appropriate handler
        self._load_handler()
    
    def _load_handler(self):
        """Load the handler function for this worker type"""
        module_name = self.config["module"]
        function_name = self.config["function"]
        
        try:
            # Dynamic import
            import importlib
            module = importlib.import_module(f"workers.{module_name}")
            self.handler = getattr(module, function_name)
            self.logger.info(f"Loaded handler: {module_name}.{function_name}")
            
        except ImportError as e:
            self.logger.warning(f"Handler module not found, using placeholder: {e}")
            self.handler = self._placeholder_handler
        except AttributeError as e:
            self.logger.warning(f"Handler function not found, using placeholder: {e}")
            self.handler = self._placeholder_handler
    
    def _placeholder_handler(self, payload: dict) -> dict:
        """Placeholder handler for testing"""
        self.logger.info(f"Placeholder processing: {json.dumps(payload)[:100]}...")
        time.sleep(1)  # Simulate work
        return {"status": "placeholder", "message": "Handler not implemented"}
    
    def run(self):
        """Main worker loop"""
        stream = self.config["stream"]
        group = self.config["group"]
        
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Starting {self.worker_type} worker")
        self.logger.info(f"  Stream: {stream}")
        self.logger.info(f"  Group: {group}")
        self.logger.info(f"  Consumer: {self.consumer_name}")
        self.logger.info(f"{'='*60}")
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
        
        # Ensure consumer group exists
        try:
            self.redis.xgroup_create(stream, group, id='0', mkstream=True)
            self.logger.info(f"Created consumer group: {group}")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                self.logger.info(f"Consumer group already exists: {group}")
            else:
                raise
        
        # Main loop
        assignments_processed = 0
        errors = 0
        
        while self.running:
            try:
                # Read from stream
                messages = self.redis.xreadgroup(
                    groupname=group,
                    consumername=self.consumer_name,
                    streams={stream: ">"},
                    count=1,
                    block=5000  # 5 second timeout
                )
                
                if not messages:
                    continue
                
                # Process each message
                for stream_name, stream_messages in messages:
                    for message_id, data in stream_messages:
                        success = self._process_message(stream_name, message_id, data)
                        if success:
                            assignments_processed += 1
                        else:
                            errors += 1
                
            except redis.ConnectionError as e:
                self.logger.error(f"Redis connection error: {e}")
                time.sleep(5)
            except Exception as e:
                self.logger.exception(f"Error in worker loop: {e}")
                errors += 1
                time.sleep(1)
        
        self.logger.info(f"Worker shutdown complete")
        self.logger.info(f"  Processed: {assignments_processed}")
        self.logger.info(f"  Errors: {errors}")
    
    def _process_message(self, stream: str, message_id: str, data: dict) -> bool:
        """Process a single message. Returns True on success."""
        start_time = time.time()
        
        try:
            # Parse payload
            raw_data = data.get("data", "{}")
            payload = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            assignment_id = payload.get("id", message_id)
            
            self.logger.info(f"Processing assignment: {assignment_id}")
            
            # Extract the actual payload (may be nested)
            work_payload = payload.get("payload", payload)
            
            # Call handler
            result = self.handler(work_payload)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # Log success
            status = result.get("status", "unknown") if isinstance(result, dict) else "complete"
            self.logger.info(f"Completed {assignment_id} in {processing_time}ms (status: {status})")
            
            # Update stats
            self.redis.hincrby("mythos:stats:workers", "total_processed", 1)
            self.redis.hincrby("mythos:stats:workers", f"{self.worker_type}_processed", 1)
            self.redis.hset("mythos:stats:workers", "last_activity", datetime.now().isoformat())
            
            # Acknowledge message
            self.redis.xack(stream, self.config["group"], message_id)
            
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in message {message_id}: {e}")
            self.redis.xack(stream, self.config["group"], message_id)
            return False
            
        except Exception as e:
            self.logger.exception(f"Error processing message {message_id}: {e}")
            
            # Update error stats
            self.redis.hincrby("mythos:stats:workers", "total_errors", 1)
            self.redis.hincrby("mythos:stats:workers", f"{self.worker_type}_errors", 1)
            
            # Acknowledge anyway to prevent infinite retry
            # TODO: Implement dead-letter queue for failed messages
            self.redis.xack(stream, self.config["group"], message_id)
            
            return False
    
    def _shutdown(self, signum, frame):
        """Handle shutdown signal"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\\nAvailable worker types:")
        for name, config in WORKER_TYPES.items():
            print(f"  {name:12} - Stream: {config['stream']}")
        sys.exit(1)
    
    worker_type = sys.argv[1].lower()
    
    if worker_type == "all":
        print("To run all workers, use separate processes or the systemd services.")
        print("Example: python3 worker.py grid & python3 worker.py embedding &")
        sys.exit(1)
    
    if worker_type not in WORKER_TYPES:
        print(f"Unknown worker type: {worker_type}")
        print("Available types:", ", ".join(WORKER_TYPES.keys()))
        sys.exit(1)
    
    worker = Worker(worker_type)
    worker.run()


if __name__ == "__main__":
    main()
'''
    
    file_path = WORKERS_DIR / "worker.py"
    file_path.write_text(content)
    os.chmod(file_path, 0o755)
    print(f"    ✓ Created {file_path}")
    return True


def create_grid_worker():
    """Create the grid analysis worker module"""
    
    content = '''#!/usr/bin/env python3
"""
Grid Analysis Worker

Performs Arcturian Grid 9-node analysis on messages.
Stores results in TimescaleDB and Neo4j.
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.grid")

GRID_NODES = ["anchor", "echo", "beacon", "synth", "nexus", "mirror", "glyph", "harmonia", "gateway"]
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def analyze_with_llm(content: str) -> Dict[str, Any]:
    """Call LLM to perform grid analysis"""
    
    prompt = f"""Analyze this text through the Arcturian Grid - a 9-node consciousness processing framework.

Score each node 0-100 based on how present that domain is in the text:

ANCHOR (matter, location, physical world, body, domestic systems):
ECHO (memory, identity, ancestors, past events, timelines):
BEACON (value, manifestation, finance, signaling presence):
SYNTH (systems, logic, code, integration of disparate parts):
NEXUS (time, scheduling, convergence, decision points):
MIRROR (emotions, psyche, shadow work, self-reflection):
GLYPH (symbols, rituals, encoding, artifacts, meta-language):
HARMONIA (relationships, heart field, balance, connection):
GATEWAY (dreams, spiritual contact, transitions, portals):

Text to analyze:
"{content}"

Respond ONLY with valid JSON in this exact format:
{{
    "anchor": <0-100>,
    "echo": <0-100>,
    "beacon": <0-100>,
    "synth": <0-100>,
    "nexus": <0-100>,
    "mirror": <0-100>,
    "glyph": <0-100>,
    "harmonia": <0-100>,
    "gateway": <0-100>,
    "dominant_node": "<name of highest scoring node>",
    "entities": {{
        "people": ["names mentioned"],
        "places": ["locations mentioned"],
        "concepts": ["key concepts"],
        "symbols": ["symbols or significant objects"]
    }},
    "emotional_tone": "<primary emotion detected>",
    "themes": ["theme1", "theme2"]
}}
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "{}")
            return json.loads(response_text)
        else:
            logger.error(f"LLM call failed: {response.status_code} - {response.text}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"LLM request failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"LLM analysis failed: {e}")
        return None


def store_grid_results(message_id: int, user_uuid: str, conversation_id: str, results: Dict[str, Any]) -> None:
    """Store grid analysis results in TimescaleDB"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        total = sum(results.get(node, 0) for node in GRID_NODES)
        dominant = results.get("dominant_node", max(GRID_NODES, key=lambda n: results.get(n, 0)))
        
        cur.execute("""
            INSERT INTO grid_activation_timeseries (
                time, user_uuid, conversation_id, message_id,
                anchor_score, echo_score, beacon_score, synth_score,
                nexus_score, mirror_score, glyph_score, harmonia_score,
                gateway_score, dominant_node, total_activation,
                analysis_model
            ) VALUES (
                NOW(), %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """, (
            user_uuid, conversation_id, message_id,
            results.get("anchor", 0), results.get("echo", 0), results.get("beacon", 0),
            results.get("synth", 0), results.get("nexus", 0), results.get("mirror", 0),
            results.get("glyph", 0), results.get("harmonia", 0), results.get("gateway", 0),
            dominant, total, OLLAMA_MODEL
        ))
        
        # Also store emotional state if detected
        emotional_tone = results.get("emotional_tone")
        if emotional_tone:
            cur.execute("""
                INSERT INTO emotional_state_timeseries (
                    time, user_uuid, conversation_id, message_id,
                    emotional_tone, themes
                ) VALUES (NOW(), %s, %s, %s, %s, %s)
            """, (user_uuid, conversation_id, message_id, emotional_tone, results.get("themes", [])))
        
        conn.commit()
        logger.info(f"Stored grid results: dominant={dominant}, total={total}")
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store grid results: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_grid_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for grid analysis worker"""
    
    message_id = payload.get("message_id")
    content = payload.get("content", "")
    user_uuid = payload.get("user_uuid")
    conversation_id = payload.get("conversation_id")
    
    if not content:
        logger.warning(f"Empty content for message {message_id}")
        return {"status": "skipped", "message_id": message_id, "reason": "empty_content"}
    
    logger.info(f"Analyzing message {message_id} ({len(content)} chars)")
    
    # Perform LLM analysis
    results = analyze_with_llm(content)
    
    if not results:
        return {"status": "failed", "message_id": message_id, "reason": "llm_failed"}
    
    # Store results
    try:
        store_grid_results(message_id, user_uuid, conversation_id, results)
    except Exception as e:
        return {"status": "failed", "message_id": message_id, "reason": str(e)}
    
    return {
        "status": "success",
        "message_id": message_id,
        "dominant_node": results.get("dominant_node"),
        "total_activation": sum(results.get(node, 0) for node in GRID_NODES),
        "entities": results.get("entities", {})
    }
'''
    
    file_path = WORKERS_DIR / "grid_worker.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_embedding_worker():
    """Create the embedding generation worker module"""
    
    content = '''#!/usr/bin/env python3
"""
Embedding Worker

Generates text embeddings and stores them in Qdrant.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.embedding")

# Lazy-loaded globals
_model = None
_qdrant = None


def get_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded successfully")
    return _model


def get_qdrant():
    global _qdrant
    if _qdrant is None:
        from qdrant_client import QdrantClient
        _qdrant = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
    return _qdrant


def process_embedding(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate and store text embedding in Qdrant"""
    
    from qdrant_client.models import PointStruct
    
    message_id = payload.get("message_id")
    content = payload.get("content", "")
    user_uuid = payload.get("user_uuid")
    conversation_id = payload.get("conversation_id")
    
    if not content or not content.strip():
        logger.warning(f"Empty content for message {message_id}")
        return {"status": "skipped", "message_id": message_id, "reason": "empty_content"}
    
    logger.info(f"Generating embedding for message {message_id}")
    
    try:
        # Generate embedding
        embedding = get_model().encode(content).tolist()
        
        # Store in Qdrant
        get_qdrant().upsert(
            collection_name="text_embeddings",
            points=[
                PointStruct(
                    id=message_id,
                    vector=embedding,
                    payload={
                        "user_uuid": user_uuid,
                        "conversation_id": conversation_id,
                        "content_preview": content[:500],
                        "content_length": len(content),
                        "message_type": "user_message",
                        "created_at": datetime.now().isoformat()
                    }
                )
            ]
        )
        
        logger.info(f"Stored embedding for message {message_id} (dim={len(embedding)})")
        
        return {
            "status": "success",
            "message_id": message_id,
            "embedding_dim": len(embedding)
        }
        
    except Exception as e:
        logger.exception(f"Failed to generate/store embedding: {e}")
        return {"status": "failed", "message_id": message_id, "error": str(e)}
'''
    
    file_path = WORKERS_DIR / "embedding_worker.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_vision_worker():
    """Create the vision analysis worker module"""
    
    content = '''#!/usr/bin/env python3
"""
Vision Analysis Worker

Analyzes photos using Llama Vision via Ollama.
Stores results in PostgreSQL and optionally generates image embeddings for Qdrant.
"""

import os
import base64
import json
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.vision")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def analyze_image(image_path: str) -> Dict[str, Any]:
    """Analyze image using Llama Vision"""
    
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Read and encode image
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    prompt = """Analyze this image thoroughly. Provide:

1. A general description (2-3 sentences)
2. Objects and elements visible
3. People (count and brief description if visible)
4. Any text visible (transcribe if possible)
5. Symbols or patterns (especially sacred geometry, spirals, spiritual symbols)
6. The emotional tone or mood
7. Suggested tags for categorization

Respond in JSON format:
{
    "description": "General description of the image",
    "objects": ["object1", "object2"],
    "people_count": 0,
    "people_description": "Description of people if any",
    "text_detected": "Any text found in image",
    "symbols": ["symbol1", "symbol2"],
    "sacred_geometry": false,
    "emotional_tone": "mood/emotion",
    "colors_dominant": ["color1", "color2"],
    "tags": ["tag1", "tag2", "tag3"]
}
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [image_data],
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.loads(result.get("response", "{}"))
        else:
            logger.error(f"Vision API failed: {response.status_code}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse vision response: {e}")
        return None
    except Exception as e:
        logger.exception(f"Vision analysis failed: {e}")
        return None


def store_analysis(photo_id: str, analysis: Dict[str, Any]) -> None:
    """Store vision analysis results in PostgreSQL"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE media_files SET
                analysis_data = %s,
                auto_tags = %s,
                processed = TRUE,
                processed_at = NOW()
            WHERE id = %s
        """, (
            json.dumps(analysis),
            analysis.get("tags", []),
            photo_id
        ))
        
        if cur.rowcount == 0:
            logger.warning(f"No media_files row found for id {photo_id}")
        
        conn.commit()
        logger.info(f"Stored analysis for photo {photo_id}")
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store analysis: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_vision(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for vision analysis worker"""
    
    photo_id = payload.get("photo_id")
    file_path = payload.get("file_path")
    user_uuid = payload.get("user_uuid")
    
    if not file_path:
        return {"status": "failed", "photo_id": photo_id, "error": "no_file_path"}
    
    logger.info(f"Analyzing photo {photo_id}: {file_path}")
    
    # Check file exists
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        return {"status": "failed", "photo_id": photo_id, "error": "file_not_found"}
    
    # Analyze image
    analysis = analyze_image(file_path)
    
    if not analysis:
        return {"status": "failed", "photo_id": photo_id, "reason": "analysis_failed"}
    
    # Store results
    try:
        store_analysis(photo_id, analysis)
    except Exception as e:
        return {"status": "failed", "photo_id": photo_id, "error": str(e)}
    
    return {
        "status": "success",
        "photo_id": photo_id,
        "tags_count": len(analysis.get("tags", [])),
        "symbols_detected": len(analysis.get("symbols", [])),
        "has_sacred_geometry": analysis.get("sacred_geometry", False)
    }
'''
    
    file_path = WORKERS_DIR / "vision_worker.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_temporal_worker():
    """Create the temporal extraction worker module"""
    
    content = '''#!/usr/bin/env python3
"""
Temporal Extraction Worker

Extracts dates, times, and temporal references from messages.
Links to astrological events when relevant.
"""

import os
import re
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.temporal")

# Relative time patterns
RELATIVE_PATTERNS = {
    r"\\byesterday\\b": -1,
    r"\\btoday\\b": 0,
    r"\\btomorrow\\b": 1,
    r"\\blast week\\b": -7,
    r"\\bnext week\\b": 7,
    r"\\blast month\\b": -30,
    r"\\bnext month\\b": 30,
    r"\\blast year\\b": -365,
    r"\\bnext year\\b": 365,
}


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def extract_dates(text: str) -> List[datetime]:
    """Extract date references from text"""
    dates = []
    now = datetime.now()
    
    # Check relative patterns
    for pattern, days_offset in RELATIVE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            dates.append(now + timedelta(days=days_offset))
    
    # ISO format dates: 2026-01-21
    iso_matches = re.findall(r"\\b(\\d{4}-\\d{2}-\\d{2})\\b", text)
    for match in iso_matches:
        try:
            dates.append(datetime.strptime(match, "%Y-%m-%d"))
        except ValueError:
            pass
    
    # US format dates: 1/21/2026 or 01/21/2026
    us_matches = re.findall(r"\\b(\\d{1,2}/\\d{1,2}/\\d{4})\\b", text)
    for match in us_matches:
        try:
            dates.append(datetime.strptime(match, "%m/%d/%Y"))
        except ValueError:
            pass
    
    # Month name dates: January 21, 2026
    month_matches = re.findall(
        r"\\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{1,2},?\\s+\\d{4})\\b",
        text, re.IGNORECASE
    )
    for match in month_matches:
        try:
            # Try multiple formats
            for fmt in ["%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"]:
                try:
                    dates.append(datetime.strptime(match.replace(",", ""), fmt.replace(",", "")))
                    break
                except ValueError:
                    continue
        except Exception:
            pass
    
    return dates


def find_active_transits(date: datetime) -> List[Dict[str, Any]]:
    """Find astrological events active on a given date"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, event_type, body1, body2, description, significance
            FROM astrological_events
            WHERE %s BETWEEN COALESCE(influence_start, exact_time - INTERVAL '7 days') 
                        AND COALESCE(influence_end, exact_time + INTERVAL '7 days')
        """, (date,))
        
        results = []
        for row in cur.fetchall():
            results.append({
                "id": str(row[0]),
                "event_type": row[1],
                "body1": row[2],
                "body2": row[3],
                "description": row[4],
                "significance": row[5]
            })
        
        return results
        
    finally:
        cur.close()
        conn.close()


def store_temporal_data(message_id: int, user_uuid: str, dates: List[datetime], transits: List[Dict]) -> None:
    """Store extracted temporal data and link to astrological events"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Update message with mentioned dates (if column exists)
        if dates:
            try:
                cur.execute("""
                    UPDATE chat_messages
                    SET mentioned_dates = %s
                    WHERE message_id = %s
                """, ([d.date() for d in dates], message_id))
            except psycopg2.Error:
                # Column might not exist yet
                pass
        
        # Link to astrological events
        for transit in transits:
            cur.execute("""
                INSERT INTO message_astrological_context (message_id, astrological_event_id, auto_linked, relevance_score)
                VALUES (%s, %s, TRUE, 0.8)
                ON CONFLICT (message_id, astrological_event_id) DO NOTHING
            """, (message_id, transit["id"]))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store temporal data: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_temporal(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for temporal extraction worker"""
    
    message_id = payload.get("message_id")
    content = payload.get("content", "")
    user_uuid = payload.get("user_uuid")
    
    if not content:
        return {"status": "skipped", "message_id": message_id, "reason": "empty_content"}
    
    logger.info(f"Extracting temporal data from message {message_id}")
    
    # Extract dates from text
    dates = extract_dates(content)
    logger.info(f"Found {len(dates)} date references")
    
    # Find active transits for mentioned dates
    all_transits = []
    for date in dates:
        transits = find_active_transits(date)
        all_transits.extend(transits)
    
    # Also check current date for context
    current_transits = find_active_transits(datetime.now())
    
    # Deduplicate transits
    seen_ids = set()
    unique_transits = []
    for t in all_transits + current_transits:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            unique_transits.append(t)
    
    # Store results
    if dates or unique_transits:
        try:
            store_temporal_data(message_id, user_uuid, dates, unique_transits)
        except Exception as e:
            return {"status": "failed", "message_id": message_id, "error": str(e)}
    
    return {
        "status": "success",
        "message_id": message_id,
        "dates_found": len(dates),
        "transits_linked": len(unique_transits),
        "dates": [d.isoformat() for d in dates]
    }
'''
    
    file_path = WORKERS_DIR / "temporal_worker.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_entity_worker():
    """Create the entity resolution worker module"""
    
    content = '''#!/usr/bin/env python3
"""
Entity Resolution Worker

Resolves entities mentioned in messages to canonical forms.
Creates/updates entities in Neo4j and tracks mentions in TimescaleDB.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.entity")

# Known aliases for entity resolution
KNOWN_ALIASES = {
    # People
    "rebecca": "seraphe",
    "becca": "seraphe",
    "seraphe": "seraphe",
    "ka": "kataurel",
    "adge": "kataurel",
    "adriaan": "kataurel",
    "fitz": "fitz",
    # Concepts
    "merovingian": "merovingian_bloodline",
    "merovingians": "merovingian_bloodline",
}


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def get_neo4j():
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "")
        )
    )


def resolve_entity(name: str, entity_type: str) -> str:
    """Resolve entity name to canonical form"""
    name_lower = name.lower().strip()
    
    if name_lower in KNOWN_ALIASES:
        return KNOWN_ALIASES[name_lower]
    
    # Default: lowercase, replace spaces with underscores
    return name_lower.replace(" ", "_").replace("-", "_")


def create_or_update_entity(driver, canonical_id: str, name: str, entity_type: str) -> str:
    """Create or update entity in Neo4j"""
    
    # Map to proper Neo4j label
    label_map = {
        "person": "Person",
        "people": "Person",
        "place": "Place",
        "places": "Place",
        "concept": "Concept",
        "concepts": "Concept",
        "symbol": "Symbol",
        "symbols": "Symbol"
    }
    label = label_map.get(entity_type.lower(), "Entity")
    
    with driver.session() as session:
        result = session.run(f"""
            MERGE (e:{label} {{canonical_id: $canonical_id}})
            ON CREATE SET
                e.name = $name,
                e.created_at = datetime(),
                e.mention_count = 1
            ON MATCH SET
                e.mention_count = COALESCE(e.mention_count, 0) + 1,
                e.last_mentioned = datetime()
            RETURN e.canonical_id as id
        """, canonical_id=canonical_id, name=name)
        
        record = result.single()
        return record["id"] if record else None


def store_entity_mention(user_uuid: str, conversation_id: str, message_id: int,
                        canonical_id: str, name: str, entity_type: str) -> None:
    """Store entity mention in TimescaleDB"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO entity_mention_timeseries (
                time, user_uuid, conversation_id, message_id,
                entity_canonical_id, entity_name, entity_type
            ) VALUES (NOW(), %s, %s, %s, %s, %s, %s)
        """, (user_uuid, conversation_id, message_id, canonical_id, name, entity_type))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        logger.warning(f"Failed to store entity mention: {e}")
    finally:
        cur.close()
        conn.close()


def process_entity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for entity resolution worker"""
    
    message_id = payload.get("message_id")
    user_uuid = payload.get("user_uuid")
    conversation_id = payload.get("conversation_id")
    entities = payload.get("entities", {})
    
    if not entities:
        return {"status": "skipped", "message_id": message_id, "reason": "no_entities"}
    
    logger.info(f"Resolving entities for message {message_id}")
    
    driver = get_neo4j()
    resolved_count = 0
    
    try:
        for entity_type, names in entities.items():
            if not isinstance(names, list):
                continue
                
            for name in names:
                if not name or not isinstance(name, str):
                    continue
                    
                # Resolve to canonical form
                canonical_id = resolve_entity(name, entity_type)
                
                # Create/update in Neo4j
                create_or_update_entity(driver, canonical_id, name, entity_type)
                
                # Store mention in TimescaleDB
                store_entity_mention(
                    user_uuid, conversation_id, message_id,
                    canonical_id, name, entity_type
                )
                
                resolved_count += 1
                logger.debug(f"Resolved: {name} -> {canonical_id} ({entity_type})")
        
        return {
            "status": "success",
            "message_id": message_id,
            "entities_resolved": resolved_count
        }
        
    except Exception as e:
        logger.exception(f"Entity resolution failed: {e}")
        return {"status": "failed", "message_id": message_id, "error": str(e)}
    finally:
        driver.close()
'''
    
    file_path = WORKERS_DIR / "entity_worker.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_summary_worker():
    """Create the summary rebuild worker module"""
    
    content = '''#!/usr/bin/env python3
"""
Summary Rebuild Worker

Rebuilds conversation summaries (Tier 1 and Tier 2) when triggered.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.summary")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def get_messages_for_summary(conversation_id: str, start_idx: int, end_idx: int) -> List[Dict]:
    """Get messages within a range for summarization"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            WITH ranked AS (
                SELECT 
                    message_id, role, content, created_at,
                    ROW_NUMBER() OVER (ORDER BY created_at) as rn
                FROM chat_messages
                WHERE conversation_id = %s
            )
            SELECT message_id, role, content, created_at
            FROM ranked
            WHERE rn BETWEEN %s AND %s
            ORDER BY created_at
        """, (conversation_id, start_idx, end_idx))
        
        messages = []
        for row in cur.fetchall():
            messages.append({
                "message_id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3].isoformat() if row[3] else None
            })
        
        return messages
        
    finally:
        cur.close()
        conn.close()


def generate_summary(messages: List[Dict], tier: int) -> Dict[str, Any]:
    """Generate summary using LLM"""
    
    # Format messages for prompt
    formatted = []
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"][:500] if len(msg["content"]) > 500 else msg["content"]
        formatted.append(f"{role}: {content}")
    
    messages_text = "\\n\\n".join(formatted)
    
    # Tier determines verbosity
    word_target = 500 if tier == 1 else 800
    
    prompt = f"""Summarize this conversation segment. Target length: ~{word_target} words.

PRIORITIZE:
1. Main themes and topics discussed
2. Emotional tone and shifts
3. Key entities mentioned (people, places, concepts)
4. Important decisions or realizations
5. Context (where, when, circumstances)

CONVERSATION TO SUMMARIZE:
{messages_text}

Respond in JSON format:
{{
    "summary": "The narrative summary...",
    "themes": ["theme1", "theme2"],
    "emotional_tone": "primary emotion",
    "context_notes": "environmental/situational context",
    "key_entities": {{
        "people": ["names"],
        "concepts": ["concepts"],
        "places": ["places"]
    }}
}}
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.loads(result.get("response", "{}"))
        else:
            logger.error(f"LLM call failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.exception(f"Summary generation failed: {e}")
        return None


def store_summary(conversation_id: str, user_uuid: str, tier: int, 
                  start_msg_id: int, end_msg_id: int, summary_data: Dict) -> str:
    """Store summary in database"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Mark old summary as superseded
        cur.execute("""
            UPDATE conversation_summaries
            SET is_current = FALSE, superseded_by = NULL
            WHERE conversation_id = %s AND tier = %s AND is_current = TRUE
            RETURNING id
        """, (conversation_id, tier))
        old_id = cur.fetchone()
        
        # Calculate metrics
        summary_text = summary_data.get("summary", "")
        original_tokens = len(summary_text.split()) * 2  # Rough estimate
        summary_tokens = len(summary_text.split())
        compression = original_tokens / summary_tokens if summary_tokens > 0 else 1.0
        
        # Insert new summary
        cur.execute("""
            INSERT INTO conversation_summaries (
                conversation_id, user_uuid, tier,
                start_message_id, end_message_id, message_count,
                summary_text, themes, emotional_tone, context_notes, key_entities,
                original_tokens, summary_tokens, compression_ratio,
                is_current
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE
            )
            RETURNING id
        """, (
            conversation_id, user_uuid, tier,
            start_msg_id, end_msg_id, end_msg_id - start_msg_id + 1,
            summary_text,
            summary_data.get("themes", []),
            summary_data.get("emotional_tone"),
            summary_data.get("context_notes"),
            json.dumps(summary_data.get("key_entities", {})),
            original_tokens, summary_tokens, compression
        ))
        
        new_id = cur.fetchone()[0]
        
        # Link old to new
        if old_id:
            cur.execute("""
                UPDATE conversation_summaries
                SET superseded_by = %s
                WHERE id = %s
            """, (new_id, old_id[0]))
        
        conn.commit()
        return str(new_id)
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store summary: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for summary rebuild worker"""
    
    conversation_id = payload.get("conversation_id")
    user_uuid = payload.get("user_uuid")
    tier = payload.get("tier", 1)
    start_idx = payload.get("start_idx", 1)
    end_idx = payload.get("end_idx", 20)
    
    logger.info(f"Rebuilding Tier {tier} summary for conversation {conversation_id[:8]}...")
    
    # Get messages
    messages = get_messages_for_summary(conversation_id, start_idx, end_idx)
    
    if not messages:
        return {"status": "skipped", "conversation_id": conversation_id, "reason": "no_messages"}
    
    logger.info(f"Summarizing {len(messages)} messages")
    
    # Generate summary
    summary_data = generate_summary(messages, tier)
    
    if not summary_data:
        return {"status": "failed", "conversation_id": conversation_id, "reason": "generation_failed"}
    
    # Store summary
    try:
        start_msg_id = messages[0]["message_id"]
        end_msg_id = messages[-1]["message_id"]
        summary_id = store_summary(
            conversation_id, user_uuid, tier,
            start_msg_id, end_msg_id, summary_data
        )
    except Exception as e:
        return {"status": "failed", "conversation_id": conversation_id, "error": str(e)}
    
    return {
        "status": "success",
        "conversation_id": conversation_id,
        "tier": tier,
        "summary_id": summary_id,
        "messages_summarized": len(messages),
        "themes": summary_data.get("themes", [])
    }
'''
    
    file_path = WORKERS_DIR / "summary_worker.py"
    file_path.write_text(content)
    print(f"    ✓ Created {file_path}")
    return True


def create_systemd_services():
    """Create systemd service files for workers"""
    
    service_template = '''[Unit]
Description=Mythos {worker_name} Worker
After=network.target redis.service postgresql.service

[Service]
Type=simple
User={user}
WorkingDirectory=/opt/mythos
Environment="PATH=/opt/mythos/.venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/opt/mythos/.venv/bin/python3 /opt/mythos/workers/worker.py {worker_type}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    
    # Get current user
    user = os.getenv("USER", "adge")
    
    workers = [
        ("grid", "Grid Analysis"),
        ("embedding", "Embedding"),
        ("vision", "Vision Analysis"),
        ("temporal", "Temporal"),
        ("entity", "Entity Resolution"),
        ("summary", "Summary")
    ]
    
    services_dir = MYTHOS_BASE / "services"
    services_dir.mkdir(exist_ok=True)
    
    print("  Creating systemd service files...")
    
    for worker_type, worker_name in workers:
        service_content = service_template.format(
            worker_name=worker_name,
            worker_type=worker_type,
            user=user
        )
        
        service_file = services_dir / f"mythos-worker-{worker_type}.service"
        service_file.write_text(service_content)
        print(f"    ✓ Created {service_file}")
    
    # Create install script
    install_script = '''#!/bin/bash
# Install Mythos worker systemd services

echo "Installing Mythos worker services..."

for service in /opt/mythos/services/mythos-worker-*.service; do
    name=$(basename "$service")
    echo "  Installing $name..."
    sudo cp "$service" /etc/systemd/system/
done

sudo systemctl daemon-reload

echo ""
echo "Services installed. To enable and start:"
echo "  sudo systemctl enable mythos-worker-grid"
echo "  sudo systemctl start mythos-worker-grid"
echo ""
echo "Or enable all workers:"
echo "  for w in grid embedding vision temporal entity summary; do"
echo "    sudo systemctl enable mythos-worker-\\$w"
echo "    sudo systemctl start mythos-worker-\\$w"
echo "  done"
'''
    
    install_file = services_dir / "install_services.sh"
    install_file.write_text(install_script)
    os.chmod(install_file, 0o755)
    print(f"    ✓ Created {install_file}")
    
    return True


def verify_setup():
    """Verify worker setup"""
    
    print("\n  Verifying worker setup...")
    
    required_files = [
        WORKERS_DIR / "__init__.py",
        WORKERS_DIR / "worker.py",
        WORKERS_DIR / "grid_worker.py",
        WORKERS_DIR / "embedding_worker.py",
        WORKERS_DIR / "vision_worker.py",
        WORKERS_DIR / "temporal_worker.py",
        WORKERS_DIR / "entity_worker.py",
        WORKERS_DIR / "summary_worker.py",
    ]
    
    all_present = True
    for f in required_files:
        if f.exists():
            print(f"    ✓ {f.name}")
        else:
            print(f"    ✗ {f.name} MISSING")
            all_present = False
    
    return all_present


def main():
    print("\n" + "=" * 60)
    print("  Step 4: Worker Process Setup")
    print("=" * 60 + "\n")
    
    all_success = True
    
    # Create directory structure
    print("Creating worker directory structure...")
    if not create_directory_structure():
        all_success = False
    
    # Create files
    print("\nCreating worker modules...")
    
    if not create_init_file():
        all_success = False
    
    if not create_worker_main():
        all_success = False
    
    if not create_grid_worker():
        all_success = False
    
    if not create_embedding_worker():
        all_success = False
    
    if not create_vision_worker():
        all_success = False
    
    if not create_temporal_worker():
        all_success = False
    
    if not create_entity_worker():
        all_success = False
    
    if not create_summary_worker():
        all_success = False
    
    # Create systemd services
    print("\nCreating systemd service files...")
    if not create_systemd_services():
        all_success = False
    
    # Verify
    if not verify_setup():
        all_success = False
    
    if all_success:
        print("\n" + "=" * 60)
        print("  ✓ Worker setup complete!")
        print("=" * 60)
        print("\nWorker files created in:", WORKERS_DIR)
        print("\nTo run a worker manually:")
        print("  cd /opt/mythos")
        print("  source .venv/bin/activate")
        print("  python3 workers/worker.py grid")
        print("\nTo install systemd services:")
        print("  sudo bash /opt/mythos/services/install_services.sh")
        print("\nAvailable workers:")
        print("  grid      - Arcturian Grid 9-node analysis")
        print("  embedding - Text embedding generation (Qdrant)")
        print("  vision    - Photo analysis (Llama Vision)")
        print("  temporal  - Temporal data extraction")
        print("  entity    - Entity resolution (Neo4j)")
        print("  summary   - Conversation summary rebuilding")
        print()
    else:
        print("\n✗ Setup completed with errors")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
