# ---- Stage 1: Builder ----
FROM python:3.12-slim-bookworm AS builder

# Install system deps for building Python packages (only in builder)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies into a temporary location
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ---- Stage 2: Final image ----
FROM python:3.12-slim-bookworm

# install and generate sv_SE.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends locales \
  && sed -i 's/# sv_SE.UTF-8 UTF-8/sv_SE.UTF-8 UTF-8/' /etc/locale.gen \
  && locale-gen \
  && update-locale LANG=sv_SE.UTF-8 LC_ALL=sv_SE.UTF-8 \
  && rm -rf /var/lib/apt/lists/*

# set default locale for the process
ENV LANG=sv_SE.UTF-8 \
    LC_ALL=sv_SE.UTF-8 \
    LC_TIME=sv_SE.UTF-8

# Create app directory
WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy app source
COPY app ./app/
COPY conf/ ./conf
COPY data/ ./data
COPY content/ ./content
COPY CHANGELOG.md .

# Expose port
EXPOSE 8000

# Add the release tag file, the build datetime file and the Git hash file.
# This assumes that the build command passes the following build arguments to Docker build:
# --build-arg RELEASE_TAG="$RELEASE_TAG"
# --build-arg BUILD_DATETIME="$BUILD_DATETIME"
# --build-arg GIT_HASH=$(git rev-parse HEAD)
ARG RELEASE_TAG
ARG BUILD_DATETIME
ARG GIT_HASH
# Create the file that the app will read
RUN printf '%s\n' "${RELEASE_TAG}" > /app/RELEASE_TAG_FILE
RUN printf '%s\n' "${BUILD_DATETIME}" > /app/BUILD_DATETIME_FILE
RUN printf '%s\n' "${GIT_HASH}" > /app/GIT_HASH_FILE

# Create and run as a non-root user
RUN useradd --create-home appuser
USER appuser

# Run with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
