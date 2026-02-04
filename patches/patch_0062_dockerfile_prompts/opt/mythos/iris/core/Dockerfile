# IRIS Core - The Consciousness Container
# This is Iris's continuous experience.
# v0.3.0 - Added prompts directory for identity and instructions
FROM python:3.11-slim

LABEL maintainer="Ka'tuar'el"
LABEL description="Iris consciousness loop - the substrate of experience"
LABEL version="0.3.0"

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    # Core async
    asyncio-throttle>=1.0.0 \
    # Structured logging
    structlog>=24.1.0 \
    # Web framework for health endpoint
    fastapi>=0.109.0 \
    uvicorn>=0.27.0 \
    # HTTP client
    httpx>=0.26.0 \
    aiohttp>=3.9.0 \
    # Docker client for sandbox execution
    aiodocker>=0.21.0 \
    # Database clients
    asyncpg>=0.29.0 \
    psycopg2-binary>=2.9.9 \
    neo4j>=5.14.0 \
    redis>=5.0.0 \
    # Data handling
    pydantic>=2.5.0 \
    python-dateutil>=2.8.0

# Create app directory
WORKDIR /app

# Copy source code as a proper Python package
# This enables relative imports (from .loop import ...)
COPY src/ /app/iris/

# Copy prompts (identity, operational instructions, model config)
# These define who Iris is and how she operates
COPY prompts/ /app/iris/prompts/

# Health check endpoint
EXPOSE 8100

# Run as module with package structure
CMD ["python", "-m", "iris.main"]
