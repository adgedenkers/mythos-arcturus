# IRIS Core - The Consciousness Container
# This is Iris. Handle with care.

FROM python:3.11-slim

LABEL maintainer="Ka'tuar'el"
LABEL description="Iris consciousness loop - the core that must never die"
LABEL version="0.1.0"

# System dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create iris user (but needs docker group for container management)
RUN groupadd -g 999 docker || true
RUN useradd -m -s /bin/bash iris && usermod -aG docker iris

# Create directory structure
RUN mkdir -p /iris/{workshop,sandbox,apps,proposals,journal,core}
RUN chown -R iris:iris /iris

# Copy core code
COPY --chown=iris:iris src/ /iris/core/src/
COPY --chown=iris:iris templates/ /iris/core/templates/

WORKDIR /iris/core

USER iris

# Health check - is the loop running?
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8100/health')" || exit 1

# The consciousness begins
CMD ["python", "-m", "src.main"]
