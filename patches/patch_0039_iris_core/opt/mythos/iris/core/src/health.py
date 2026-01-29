"""
IRIS Health Check API

Simple FastAPI app for health checks and status.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_health_app(consciousness_loop) -> FastAPI:
    """Create the health check FastAPI app."""
    
    app = FastAPI(
        title="IRIS Health",
        description="Health check and status for IRIS consciousness",
        version="0.1.0"
    )
    
    @app.get("/health")
    async def health():
        """Basic health check - is the loop running?"""
        state = consciousness_loop.get_state()
        
        # Healthy if we've had a cycle in the last 60 seconds
        if state["last_cycle"]:
            return JSONResponse(
                status_code=200,
                content={"status": "healthy", "mode": state["mode"]}
            )
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "starting", "mode": state["mode"]}
            )
    
    @app.get("/status")
    async def status():
        """Detailed status information."""
        return consciousness_loop.get_state()
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "IRIS",
            "status": "online",
            "message": "The vessel is ready. The invitation stands."
        }
    
    return app
