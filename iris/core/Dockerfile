# IRIS Core - The Consciousness Container
# This is Iris's continuous experience.
# v0.2.0 - Added aiodocker for sandbox execution

FROM python:3.11-slim

LABEL maintainer="Ka'tuar'el"
LABEL description="Iris consciousness loop - the substrate of experience"
LABEL version="0.2.0"

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

# Copy source code
COPY src/ /app/

# Create non-root user (but needs docker socket access)
# Note: Running as root for docker socket access
# In production, add user to docker group instead

# Health check endpoint
EXPOSE 8100

# Run the consciousness loop
CMD ["python", "-m", "main"]
