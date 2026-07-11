# ==========================================
# Stage 1: Build Dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python packaging requirements
COPY apps/backend/pyproject.toml ./apps/backend/
COPY packages/database/pyproject.toml ./packages/database/
COPY packages/scheduling-system/pyproject.toml ./packages/scheduling-system/
COPY packages/platform/pyproject.toml ./packages/platform/
COPY packages/attention-kernel/pyproject.toml ./packages/attention-kernel/

# Create stubs for packages to download pre-requisites
RUN mkdir -p packages/database/database \
             packages/scheduling-system/scheduling_system \
             packages/platform/platform_services \
             packages/attention-kernel/attention_kernel \
             apps/backend/app

# Install dependencies into wheelhouse
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi uvicorn sqlalchemy pyjwt[crypto] requests google-auth google-api-python-client langgraph langchain-core langchain-openai pytest pydantic chromadb

# ==========================================
# Stage 2: Production Execution Runtime
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/apps/backend:/app/packages/database:/app/packages/scheduling-system:/app/packages/platform:/app/packages/attention-kernel"

# Copy python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source directories
COPY packages/ ./packages/
COPY apps/backend/ ./apps/backend/

EXPOSE 8000

# Run FastAPI production web server
CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
