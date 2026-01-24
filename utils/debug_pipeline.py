#!/usr/bin/env python3
"""Extended debug tool for Mythos pipeline"""

import json
import sys
import redis
import requests
from datetime import datetime

API_URL = "http://localhost:8000"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
API_KEY = "cHPIHNR7DOE_rq85ZDjJkAiJcbik8ub7U9iTGCjbwyc"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def status():
    """Show full system status"""
    print("\n" + "=" * 60)
    print("  MYTHOS SYSTEM STATUS")
    print("=" * 60)
    
    # API
    print("\n[API]")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        print(f"  ✅ API: {resp.json()}")
    except Exception as e:
        print(f"  ❌ API: {e}")
    
    # Redis
    print("\n[REDIS]")
    try:
        print(f"  ✅ Connected: {r.ping()}")
        queues = ['mythos:grid', 'mythos:embedding', 'mythos:vision', 
                  'mythos:temporal', 'mythos:entity', 'mythos:summary']
        for q in queues:
            length = r.llen(q)
            status = f"📥 {length}" if length > 0 else "empty"
            print(f"     {q}: {status}")
    except Exception as e:
        print(f"  ❌ Redis: {e}")
    
    # Qdrant
    print("\n[QDRANT]")
    try:
        resp = requests.get("http://localhost:6333/collections", timeout=5)
        collections = resp.json().get('result', {}).get('collections', [])
        print(f"  ✅ Connected")
        if collections:
            for c in collections:
                print(f"     - {c['name']}")
        else:
            print(f"     (no collections)")
    except Exception as e:
        print(f"  ❌ Qdrant: {e}")
    
    # Workers (via systemd)
    print("\n[WORKERS]")
    import subprocess
    workers = ['grid', 'embedding', 'vision', 'temporal', 'entity', 'summary']
    for w in workers:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', f'mythos-worker-{w}'],
                capture_output=True, text=True
            )
            status = "✅" if result.stdout.strip() == "active" else "❌"
            print(f"  {status} mythos-worker-{w}: {result.stdout.strip()}")
        except:
            print(f"  ❓ mythos-worker-{w}: unknown")

def queues():
    """Show all queue contents"""
    print("\n[QUEUE CONTENTS]")
    queues = ['mythos:grid', 'mythos:embedding', 'mythos:vision', 
              'mythos:temporal', 'mythos:entity', 'mythos:summary']
    for q in queues:
        length = r.llen(q)
        print(f"\n  {q}: {length} items")
        if length > 0:
            items = r.lrange(q, 0, 4)  # Show first 5
            for i, item in enumerate(items):
                try:
                    data = json.loads(item)
                    print(f"    [{i}] {data.get('type', 'unknown')}: {str(data)[:80]}...")
                except:
                    print(f"    [{i}] {item[:80]}...")

def results():
    """Show worker results"""
    print("\n[WORKER RESULTS]")
    keys = r.keys("mythos:result:*")
    print(f"  Total results: {len(keys)}")
    for key in keys[:10]:
        try:
            data = json.loads(r.get(key))
            print(f"\n  {key}:")
            print(f"    worker: {data.get('worker_type', 'unknown')}")
            print(f"    status: {data.get('status', 'unknown')}")
            if 'result' in data:
                print(f"    result: {str(data['result'])[:100]}...")
        except Exception as e:
            print(f"  {key}: error - {e}")

def clear():
    """Clear all queues and results"""
    print("\n[CLEARING QUEUES]")
    queues = ['mythos:grid', 'mythos:embedding', 'mythos:vision', 
              'mythos:temporal', 'mythos:entity', 'mythos:summary']
    for q in queues:
        deleted = r.delete(q)
        print(f"  Cleared {q}")
    
    keys = r.keys("mythos:result:*")
    for key in keys:
        r.delete(key)
    print(f"  Cleared {len(keys)} results")
    print("  ✅ Done")

def send(message=None):
    """Send a test message"""
    if not message:
        message = "Testing the pipeline at " + datetime.now().isoformat()
    
    print(f"\n[SENDING MESSAGE]")
    print(f"  Content: {message[:80]}...")
    
    payload = {
        "conversation_id": "debug-test-001",
        "user_id": "ka",
        "message": message
    }
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    try:
        resp = requests.post(f"{API_URL}/message", json=payload, headers=headers, timeout=30)
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def logs(worker='grid', lines=20):
    """Show worker logs"""
    import subprocess
    print(f"\n[LOGS: mythos-worker-{worker}]")
    result = subprocess.run(
        ['journalctl', '-u', f'mythos-worker-{worker}', '-n', str(lines), '--no-pager'],
        capture_output=True, text=True
    )
    print(result.stdout)

def help():
    """Show available commands"""
    print("""
MYTHOS DEBUG TOOL
=================

Usage: python3 debug_pipeline.py <command> [args]

Commands:
  status          - Show full system status
  queues          - Show queue contents
  results         - Show worker results
  clear           - Clear all queues and results
  send [message]  - Send a test message
  logs [worker]   - Show worker logs (default: grid)
  help            - Show this help

Examples:
  python3 debug_pipeline.py status
  python3 debug_pipeline.py send "Test message about spiral time"
  python3 debug_pipeline.py logs embedding 50
""")

if __name__ == "__main__":
    commands = {
        'status': status,
        'queues': queues,
        'results': results,
        'clear': clear,
        'send': send,
        'logs': logs,
        'help': help
    }
    
    if len(sys.argv) < 2:
        status()
    else:
        cmd = sys.argv[1]
        if cmd in commands:
            if cmd == 'send' and len(sys.argv) > 2:
                send(' '.join(sys.argv[2:]))
            elif cmd == 'logs':
                worker = sys.argv[2] if len(sys.argv) > 2 else 'grid'
                lines = int(sys.argv[3]) if len(sys.argv) > 3 else 20
                logs(worker, lines)
            else:
                commands[cmd]()
        else:
            print(f"Unknown command: {cmd}")
            help()
