#!/usr/bin/env bash

# Make sure the script fails fast and loudly if something goes wrong
set -euo pipefail

# Configuration
IMAGE_NAME="microbirding-app"
CONTAINER_NAME="microbirding-local"
PORT="8000:8000"

TAILWIND_IN="./tailwind.css"
TAILWIND_OUT="./app/assets/tailwind.css"

# Build metadata
RELEASE_TAG="${RELEASE_TAG:-dev}"
BUILD_DATETIME="${BUILD_DATETIME:-$(date +"%Y-%m-%d %H:%M")}"
GIT_HASH="${GIT_HASH:-$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")}"

# Ensure .env exists
if [ ! -f .env ]; then
  echo "Error: .env file not found in project root."
  echo "Create a .env file before running the dev script,"
  echo "with the following environment variables:"
  echo "ENVIRONMENT=DEV"
  echo "ARTPORTALEN_OBSERVATIONS_API_KEY=<API-KEY>"
  echo "ARTPORTALEN_SPECIES_API_KEY=<API-KEY>"
  echo "FEATURES__CACHE_DATABASE_ENABLED=true"
  echo "FEATURES__SPECIES_PAGE_ENABLED=true"
  exit 1
fi

# Step 1: Build Tailwind CSS
echo "▶ Building Tailwind CSS ..."
./tailwindcss \
  -i "$TAILWIND_IN" \
  -o "$TAILWIND_OUT"

# Step 2: Docker build
echo "▶ Building Docker image ..."
docker build \
  -t "${IMAGE_NAME}:latest" \
  --build-arg RELEASE_TAG="$RELEASE_TAG" \
  --build-arg BUILD_DATETIME="$BUILD_DATETIME" \
  --build-arg GIT_HASH="$GIT_HASH" \
  .

# Step 3: Run container
echo "▶ Running container ..."
docker run \
  --rm \
  --name="$CONTAINER_NAME" \
  -p "$PORT" \
  --env-file .env \
  "${IMAGE_NAME}:latest"
