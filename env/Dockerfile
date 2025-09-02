# Base image
FROM python:3.11-slim

# Set environment variables to non-interactive
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1

# Set workdir
WORKDIR /app

# Add src to PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Install system dependencies, including GDAL for geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
# Set GDAL environment variables for pip to find gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
RUN pip install --no-cache-dir ".[dev,docs]"

# Copy the rest of the project source
COPY . .

# Expose port for Jupyter or other web services
EXPOSE 8888

# Default command to keep the container running
CMD ["/bin/bash"]
