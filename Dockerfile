# OSI Docker Container
# This creates a self-contained OSI environment that requires no local Python installation

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy OSI source code
COPY osi/ ./osi/
COPY scripts/ ./scripts/
COPY kits/ ./kits/

# Create directories for OSI (including wheels directory)
RUN mkdir -p /app/environments /app/logs /app/wheels

# Create a wrapper script for OSI
RUN echo '#!/bin/bash\npython /app/scripts/osi.py "$@"' > /usr/local/bin/osi && \
    chmod +x /usr/local/bin/osi

# Set environment variables
ENV PYTHONPATH=/app
ENV OSI_ROOT=/app

# Create volume mount points for user data
VOLUME ["/workspace", "/app/environments", "/app/logs"]

# Set default working directory for user operations
WORKDIR /workspace

# Default command
ENTRYPOINT ["osi"]
CMD ["--help"]
