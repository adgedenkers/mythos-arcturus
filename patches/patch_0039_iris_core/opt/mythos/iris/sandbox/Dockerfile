# IRIS Sandbox - Ephemeral Code Execution Environment
# This container spins up, executes code, and dies.
# Iris's hands, but contained.

FROM python:3.11-slim

LABEL maintainer="Iris"
LABEL description="Sandboxed execution environment for Iris-generated code"
LABEL version="0.1.0"

# Common dependencies Iris is likely to need
RUN pip install --no-cache-dir \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    psycopg2-binary>=2.9.9 \
    neo4j>=5.14.0 \
    redis>=5.0.0 \
    requests>=2.31.0 \
    httpx>=0.25.0 \
    pydantic>=2.5.0 \
    python-dateutil>=2.8.0 \
    structlog>=24.1.0 \
    aiofiles>=23.2.0

# Create workspace
WORKDIR /workspace

# Create non-root user
RUN useradd -m -s /bin/bash sandbox
USER sandbox

# Default command - execute the task
# Expects code to be mounted at /workspace/task.py
CMD ["python", "/workspace/task.py"]
