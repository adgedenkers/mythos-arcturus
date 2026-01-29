"""
IRIS Health & API Endpoints

Provides:
- /health - Basic health check
- /status - Detailed status for monitoring
- /test_agency - Run a simple test task
- /run_code - Execute arbitrary code in sandbox
- /task - Queue a task for self-directed work
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import structlog

log = structlog.get_logger("iris.api")


class CodeRequest(BaseModel):
    """Request to run code in sandbox"""
    code: str


class TaskRequest(BaseModel):
    """Request to queue a task"""
    goal: str
    name: Optional[str] = None
    max_attempts: Optional[int] = 5


class TaskResponse(BaseModel):
    """Response from task operations"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None


def create_health_app(consciousness_loop) -> FastAPI:
    """
    Create FastAPI app for health checks and API.
    
    Args:
        consciousness_loop: The ConsciousnessLoop instance
    """
    app = FastAPI(
        title="Iris API",
        description="Interface to Iris consciousness system",
        version="0.2.0"
    )
    
    @app.get("/health")
    async def health():
        """Basic health check"""
        return {"status": "ok", "service": "iris-core"}
    
    @app.get("/status")
    async def status():
        """Detailed status for monitoring"""
        return consciousness_loop.get_state()
    
    @app.post("/test_agency", response_model=TaskResponse)
    async def test_agency():
        """
        Run a simple test to verify agency/sandbox is working.
        
        This runs a basic Python script in the sandbox and returns the result.
        """
        log.info("api_test_agency_requested")
        
        agency = consciousness_loop.agency
        if not agency:
            raise HTTPException(status_code=503, detail="Agency system not initialized")
        
        if not agency._initialized:
            raise HTTPException(status_code=503, detail="Agency system not ready")
        
        # Simple test code
        test_code = '''
import os
import sys
from datetime import datetime

print("=" * 40)
print("IRIS SANDBOX TEST")
print("=" * 40)
print(f"Python: {sys.version}")
print(f"Time: {datetime.now().isoformat()}")
print(f"Working dir: {os.getcwd()}")
print()

# Test environment variables
print("Database connections available:")
print(f"  POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT SET')}")
print(f"  NEO4J_URI: {os.getenv('NEO4J_URI', 'NOT SET')}")
print(f"  REDIS_HOST: {os.getenv('REDIS_HOST', 'NOT SET')}")
print()

# Test imports
print("Testing imports...")
try:
    import pandas as pd
    print("  ✓ pandas")
except ImportError as e:
    print(f"  ✗ pandas: {e}")

try:
    import psycopg2
    print("  ✓ psycopg2")
except ImportError as e:
    print(f"  ✗ psycopg2: {e}")

try:
    import neo4j
    print("  ✓ neo4j")
except ImportError as e:
    print(f"  ✗ neo4j: {e}")

try:
    import redis
    print("  ✓ redis")
except ImportError as e:
    print(f"  ✗ redis: {e}")

print()
print("=" * 40)
print("TEST COMPLETE - Sandbox is operational")
print("=" * 40)
'''
        
        result = await agency.run_code(test_code)
        
        log.info("api_test_agency_complete", 
                 success=result.get("success"),
                 duration=result.get("duration"))
        
        return TaskResponse(
            success=result.get("success", False),
            output=result.get("stdout", ""),
            error=result.get("stderr") if not result.get("success") else None,
            duration=result.get("duration", 0),
            stdout=result.get("stdout", ""),
            stderr=result.get("stderr", ""),
            exit_code=result.get("exit_code")
        )
    
    @app.post("/run_code", response_model=TaskResponse)
    async def run_code(request: CodeRequest):
        """
        Run arbitrary code in the sandbox.
        
        This is for testing and debugging - runs code directly without
        the generate/evaluate loop.
        """
        log.info("api_run_code_requested", code_length=len(request.code))
        
        agency = consciousness_loop.agency
        if not agency:
            raise HTTPException(status_code=503, detail="Agency system not initialized")
        
        if not agency._initialized:
            raise HTTPException(status_code=503, detail="Agency system not ready")
        
        result = await agency.run_code(request.code)
        
        log.info("api_run_code_complete",
                 success=result.get("success"),
                 duration=result.get("duration"))
        
        return TaskResponse(
            success=result.get("success", False),
            output=result.get("stdout", ""),
            error=result.get("stderr") if not result.get("success") else None,
            duration=result.get("duration", 0),
            stdout=result.get("stdout", ""),
            stderr=result.get("stderr", ""),
            exit_code=result.get("exit_code")
        )
    
    @app.post("/task")
    async def queue_task(request: TaskRequest):
        """
        Queue a task for Iris to work on.
        
        The task will be processed during reflection mode (night) or
        when Iris has free cycles in background mode.
        """
        log.info("api_task_queued", goal=request.goal[:100])
        
        task = {
            "name": request.name or "api_task",
            "goal": request.goal,
            "max_attempts": request.max_attempts or 5,
        }
        
        await consciousness_loop.queue_task(task)
        
        return {
            "status": "queued",
            "task": task,
            "message": "Task queued for processing"
        }
    
    return app
