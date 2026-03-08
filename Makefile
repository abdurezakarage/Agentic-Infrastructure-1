.PHONY: setup test spec-check docker-build docker-test clean

IMAGE_NAME ?= chimera
IMAGE_TAG ?= $(if $(GITHUB_SHA),$(GITHUB_SHA),latest)

# Initialize environment
setup:
	uv sync
	uv pip install -e .

# Run tests
test:
	uv run pytest tests/ -v

# Run tests in Docker
docker-test:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -t $(IMAGE_NAME):latest .
	docker run --rm $(IMAGE_NAME):$(IMAGE_TAG)

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -t $(IMAGE_NAME):latest .

# Validate specs against implementation
spec-check:
	uv run python scripts/validate_specs.py

# Code quality checks
lint:
	uv run --with ruff ruff check .
	uv run --with mypy mypy .

# Clean up
clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -name "*.pyc" -delete