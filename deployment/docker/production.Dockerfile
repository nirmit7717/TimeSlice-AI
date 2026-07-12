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
COPY packages/adaptive-intelligence/pyproject.toml ./packages/adaptive-intelligence/
COPY packages/notification-system/pyproject.toml ./packages/notification-system/
COPY packages/analytics-system/pyproject.toml ./packages/analytics-system/
COPY packages/execution-system/pyproject.toml ./packages/execution-system/
COPY packages/context-vault/pyproject.toml ./packages/context-vault/

# Create stubs for packages to download pre-requisites
RUN mkdir -p packages/database/database \
             packages/scheduling-system/scheduling_system \
             packages/platform/platform_services \
             packages/attention-kernel/attention_kernel \
             packages/adaptive-intelligence/adaptive_intelligence \
             packages/notification-system/notification_system \
             packages/analytics-system/analytics_system \
             packages/execution-system/execution_system \
             packages/context-vault/context_vault \
             apps/backend/app

# Install dependencies into wheelhouse
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi uvicorn sqlalchemy pyjwt[crypto] requests google-auth google-api-python-client langgraph langchain-core langchain-openai pytest pydantic chromadb apscheduler python-jose passlib bcrypt plyer ruff

# ==========================================
# Stage 2: Production Execution Runtime
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/apps/backend:/app/packages/database:/app/packages/scheduling-system:/app/packages/platform:/app/packages/attention-kernel:/app/packages/adaptive-intelligence:/app/packages/notification-system:/app/packages/analytics-system:/app/packages/execution-system:/app/packages/context-vault"

# Copy python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source directories
COPY packages/ ./packages/
COPY apps/backend/ ./apps/backend/

EXPOSE 8000

# Run FastAPI production web server
CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
