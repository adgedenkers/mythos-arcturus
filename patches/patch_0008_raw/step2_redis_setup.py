#!/usr/bin/env python3
"""
Step 2: Redis Task Queue Setup

Creates Redis streams for assignment dispatching:
- mythos:assignments:grid_analysis
- mythos:assignments:embedding
- mythos:assignments:temporal
- mythos:assignments:entity
- mythos:assignments:vision
- mythos:assignments:summary_rebuild

Also sets up consumer groups for worker scaling.

Usage: python3 step2_redis_setup.py
"""

import sys
import time
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Stream configurations
STREAMS = {
    "mythos:assignments:grid_analysis": {
        "description": "Arcturian Grid 9-node analysis assignments",
        "consumer_group": "grid_workers"
    },
    "mythos:assignments:embedding": {
        "description": "Text embedding generation assignments",
        "consumer_group": "embedding_workers"
    },
    "mythos:assignments:temporal": {
        "description": "Temporal data extraction assignments",
        "consumer_group": "temporal_workers"
    },
    "mythos:assignments:entity": {
        "description": "Entity resolution assignments",
        "consumer_group": "entity_workers"
    },
    "mythos:assignments:vision": {
        "description": "Photo/vision analysis assignments",
        "consumer_group": "vision_workers"
    },
    "mythos:assignments:summary_rebuild": {
        "description": "Conversation summary rebuild assignments",
        "consumer_group": "summary_workers"
    }
}

# Additional keys for orchestration
ORCHESTRATION_KEYS = {
    "mythos:config": "System configuration hash",
    "mythos:stats:assignments": "Assignment statistics hash",
    "mythos:stats:workers": "Worker statistics hash"
}


def wait_for_redis(r: redis.Redis, max_attempts: int = 30) -> bool:
    """Wait for Redis to be ready"""
    for attempt in range(max_attempts):
        try:
            if r.ping():
                print(f"✓ Redis is ready")
                return True
        except redis.ConnectionError:
            if attempt < max_attempts - 1:
                print(f"  Waiting for Redis... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
            else:
                print(f"✗ Redis not responding after {max_attempts} attempts")
                return False
    return False


def create_stream_and_group(r: redis.Redis, stream_name: str, config: dict) -> bool:
    """Create a Redis stream and its consumer group"""
    
    print(f"  Setting up stream: {stream_name}")
    print(f"    - Description: {config['description']}")
    print(f"    - Consumer group: {config['consumer_group']}")
    
    try:
        # Create stream with initial entry if it doesn't exist
        # We use XGROUP CREATE with MKSTREAM to create both
        try:
            r.xgroup_create(
                stream_name,
                config['consumer_group'],
                id='0',
                mkstream=True
            )
            print(f"    ✓ Stream and consumer group created")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"    - Consumer group already exists")
            else:
                raise e
        
        # Verify stream exists
        stream_info = r.xinfo_stream(stream_name)
        print(f"    - Stream length: {stream_info['length']}")
        
        # Verify consumer group exists
        groups = r.xinfo_groups(stream_name)
        group_names = [g['name'] for g in groups]
        if config['consumer_group'] in group_names:
            print(f"    ✓ Consumer group verified")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False


def setup_orchestration_keys(r: redis.Redis) -> bool:
    """Set up orchestration-related Redis keys"""
    
    print("\n  Setting up orchestration keys...")
    
    try:
        # Configuration hash
        r.hset("mythos:config", mapping={
            "version": "1.0.0",
            "setup_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "grid_workers_enabled": "true",
            "embedding_workers_enabled": "true",
            "vision_workers_enabled": "true",
            "temporal_workers_enabled": "true",
            "entity_workers_enabled": "true",
            "summary_workers_enabled": "true"
        })
        print("    ✓ mythos:config initialized")
        
        # Statistics hashes
        r.hset("mythos:stats:assignments", mapping={
            "total_dispatched": "0",
            "grid_dispatched": "0",
            "embedding_dispatched": "0",
            "temporal_dispatched": "0",
            "entity_dispatched": "0",
            "vision_dispatched": "0",
            "summary_dispatched": "0"
        })
        print("    ✓ mythos:stats:assignments initialized")
        
        r.hset("mythos:stats:workers", mapping={
            "total_processed": "0",
            "total_errors": "0",
            "last_activity": ""
        })
        print("    ✓ mythos:stats:workers initialized")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Failed to setup orchestration keys: {e}")
        return False


def verify_setup(r: redis.Redis) -> None:
    """Print Redis setup status"""
    
    print("\n  Redis Status:")
    print("  " + "-" * 50)
    
    # Server info
    info = r.info('server')
    print(f"  Redis version: {info['redis_version']}")
    
    # Memory info
    mem = r.info('memory')
    used_mb = mem['used_memory'] / (1024 * 1024)
    print(f"  Memory used: {used_mb:.2f} MB")
    
    # Streams info
    print("\n  Streams:")
    for stream_name in STREAMS.keys():
        try:
            info = r.xinfo_stream(stream_name)
            groups = r.xinfo_groups(stream_name)
            print(f"    {stream_name}:")
            print(f"      - Length: {info['length']}")
            print(f"      - Groups: {len(groups)}")
        except redis.ResponseError:
            print(f"    {stream_name}: Not created")
    
    # Config info
    print("\n  Configuration:")
    config = r.hgetall("mythos:config")
    for key, value in config.items():
        print(f"    {key.decode()}: {value.decode()}")


def main():
    print("\n" + "=" * 60)
    print("  Redis Task Queue Setup")
    print("=" * 60 + "\n")
    
    # Connect to Redis
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    
    # Wait for Redis to be ready
    if not wait_for_redis(r):
        print("\n✗ Setup failed: Redis not available")
        sys.exit(1)
    
    # Create streams and consumer groups
    print("\nCreating streams and consumer groups...")
    all_success = True
    
    for stream_name, config in STREAMS.items():
        if not create_stream_and_group(r, stream_name, config):
            all_success = False
    
    # Setup orchestration keys
    if not setup_orchestration_keys(r):
        all_success = False
    
    # Verify setup
    verify_setup(r)
    
    if all_success:
        print("\n" + "=" * 60)
        print("  ✓ Redis setup complete!")
        print("=" * 60)
        print("\nStreams ready for assignment dispatching:")
        for stream_name, config in STREAMS.items():
            print(f"  - {stream_name}")
        print("\nWorker commands:")
        print("  python3 worker.py grid      # Grid analysis worker")
        print("  python3 worker.py embedding # Embedding worker")
        print("  python3 worker.py vision    # Vision analysis worker")
        print("  python3 worker.py temporal  # Temporal extraction worker")
        print("  python3 worker.py entity    # Entity resolution worker")
        print()
    else:
        print("\n✗ Setup completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
