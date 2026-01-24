#!/usr/bin/env python3
"""Test the Mythos orchestration pipeline"""

import json
import time
import redis
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
API_KEY = "cHPIHNR7DOE_rq85ZDjJkAiJcbik8ub7U9iTGCjbwyc"  # ka key

def test_api_health():
    """Check API is responding"""
    print("\n=== Testing API Health ===")
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.json()}")
        return r.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_redis_connection():
    """Check Redis is responding"""
    print("\n=== Testing Redis Connection ===")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        pong = r.ping()
        print(f"  Ping: {pong}")
        
        # Check queue lengths
        queues = ['mythos:grid', 'mythos:embedding', 'mythos:vision', 
                  'mythos:temporal', 'mythos:entity', 'mythos:summary']
        for q in queues:
            length = r.llen(q)
            print(f"  Queue {q}: {length} items")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_qdrant():
    """Check Qdrant is responding"""
    print("\n=== Testing Qdrant ===")
    try:
        r = requests.get("http://localhost:6333/collections", timeout=5)
        data = r.json()
        collections = data.get('result', {}).get('collections', [])
        print(f"  Status: {r.status_code}")
        print(f"  Collections: {[c['name'] for c in collections] if collections else 'None yet'}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_message_endpoint():
    """Send a test message through the pipeline"""
    print("\n=== Testing Message Pipeline ===")
    
    test_payload = {
        "conversation_id": "test-conv-001",
        "user_id": "ka",
        "message": "I've been feeling a strong connection to the spiral time cycles lately. The 9-day rhythm seems to align with something deeper - perhaps related to the work at Montségur. What patterns do you see emerging?"
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"  Sending test message...")
    print(f"  Content: {test_payload['message'][:80]}...")
    
    try:
        r = requests.post(
            f"{API_URL}/message",
            json=test_payload,
            headers=headers,
            timeout=30
        )
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            response = r.json()
            print(f"  Response: {json.dumps(response, indent=2)[:500]}")
            return True
        else:
            print(f"  ❌ Error: {r.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_worker_processing():
    """Check if workers are processing"""
    print("\n=== Checking Worker Activity ===")
    
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    
    # Check for results
    result_keys = r.keys("mythos:result:*")
    print(f"  Results in Redis: {len(result_keys)}")
    
    # Check processing queues
    processing_keys = r.keys("mythos:processing:*")
    print(f"  Currently processing: {len(processing_keys)}")
    
    # Check all queues again
    queues = ['mythos:grid', 'mythos:embedding', 'mythos:vision', 
              'mythos:temporal', 'mythos:entity', 'mythos:summary']
    print("\n  Queue status after message:")
    for q in queues:
        length = r.llen(q)
        if length > 0:
            print(f"    {q}: {length} items waiting")

def main():
    print("=" * 60)
    print("  Mythos Pipeline Test")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results['api'] = test_api_health()
    results['redis'] = test_redis_connection()
    results['qdrant'] = test_qdrant()
    results['message'] = test_message_endpoint()
    
    # Wait a moment for workers to process
    if results['message']:
        print("\n  Waiting 3 seconds for worker processing...")
        time.sleep(3)
        check_worker_processing()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test}")
    
    all_passed = all(results.values())
    print("\n" + ("  ✅ All tests passed!" if all_passed else "  ⚠️  Some tests failed"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
