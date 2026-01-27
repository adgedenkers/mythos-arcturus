#!/usr/bin/env python3
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
import importlib
from datetime import datetime
from pathlib import Path

# Add /opt/mythos to Python path for imports
sys.path.insert(0, '/opt/mythos')

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
        
        # Stats
        self.assignments_processed = 0
        self.errors = 0
        
        # Load the appropriate handler
        self._load_handler()
    
    def _load_handler(self):
        """Load the handler function for this worker type"""
        module_name = self.config["module"]
        function_name = self.config["function"]
        
        try:
            # Dynamic import from workers package
            module = importlib.import_module(f"workers.{module_name}")
            self.handler = getattr(module, function_name)
            self.logger.info(f"Loaded handler: workers.{module_name}.{function_name}")
            
        except ImportError as e:
            self.logger.error(f"Failed to import handler module 'workers.{module_name}': {e}")
            self.logger.info("Falling back to placeholder handler")
            self.handler = self._placeholder_handler
        except AttributeError as e:
            self.logger.error(f"Handler function '{function_name}' not found in module: {e}")
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
                            self.assignments_processed += 1
                        else:
                            self.errors += 1
                
            except redis.ConnectionError as e:
                self.logger.error(f"Redis connection error: {e}")
                time.sleep(5)
            except Exception as e:
                self.logger.exception(f"Error in worker loop: {e}")
                self.errors += 1
                time.sleep(1)
        
        self.logger.info(f"Worker shutdown complete")
        self.logger.info(f"  Processed: {self.assignments_processed}")
        self.logger.info(f"  Errors: {self.errors}")
    
    def _process_message(self, stream: str, message_id: str, data: dict) -> bool:
        """Process a single message. Returns True on success."""
        start_time = time.time()
        
        try:
            # Parse payload
            raw_data = data.get("data", "{}")
            payload = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            assignment_id = payload.get("id", message_id)
            
            self.logger.info(f"Processing assignment: {assignment_id[:8] if len(assignment_id) > 8 else assignment_id}...")
            
            # Extract the actual payload (may be nested)
            work_payload = payload.get("payload", payload)
            
            # Call handler
            result = self.handler(work_payload)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # Log success
            status = result.get("status", "unknown") if isinstance(result, dict) else "complete"
            self.logger.info(f"Completed {assignment_id[:8]}... in {processing_time}ms (status: {status})")
            
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
        print("\nAvailable worker types:")
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
