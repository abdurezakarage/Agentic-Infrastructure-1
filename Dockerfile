FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 chimera && chown -R chimera:chimera /app
USER chimera

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-m", "pytest", "tests/"]