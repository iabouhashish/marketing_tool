# Marketing Project Makefile
.PHONY: help install install-dev test test-unit test-integration lint format clean build run serve docker-build docker-run deploy-staging deploy-production

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  lint             Run all linting checks"
	@echo "  format           Format code with black and isort"
	@echo "  clean            Clean up temporary files"
	@echo "  build            Build the package"
	@echo "  run              Run the application"
	@echo "  serve            Start the FastAPI server"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run Docker container"
	@echo "  deploy-staging   Deploy to staging environment"
	@echo "  deploy-production Deploy to production environment"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test: test-unit test-integration

test-unit:
	pytest tests/ -v --cov=src/marketing_project --cov-report=xml --cov-report=html

test-integration:
	pytest tests/integrations/ -v -m integration

# Linting and formatting
lint: lint-black lint-isort lint-flake8

lint-black:
	black --check --diff src/ tests/

lint-isort:
	isort --check-only --diff src/ tests/

lint-flake8:
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

# Security checks
security: security-bandit

security-bandit:
	bandit -r src/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name "htmlcov" -delete
	rm -f .coverage coverage.xml

# Build
build:
	python setup.py sdist bdist_wheel

# Run application
run:
	marketing-project run

serve:
	marketing-project serve

# Docker operations
docker-build:
	docker build -t marketing-project:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env marketing-project:latest

# Deployment (requires kubectl and proper context)
deploy-staging:
	kubectl set image deployment/marketing-project-server marketing-project=registry.gitlab.com/your-group/arthur-marketing-generator:latest -n marketing-project
	kubectl rollout status deployment/marketing-project-server -n marketing-project

deploy-production:
	kubectl set image deployment/marketing-project-server marketing-project=registry.gitlab.com/your-group/arthur-marketing-generator:latest -n marketing-project
	kubectl rollout status deployment/marketing-project-server -n marketing-project

# Development helpers
dev-setup: install-dev
	@echo "Setting up development environment..."
	@echo "Creating logs directory..."
	@mkdir -p logs
	@echo "Copying environment file..."
	@cp env.example .env
	@echo "Development environment ready!"

# CI/CD helpers
ci-test: install-dev test lint security

ci-build: docker-build

ci-deploy: deploy-staging

# GitHub Actions helpers
gh-format: format
	@echo "Code formatted. Commit and push to trigger GitHub Actions."

gh-test: test lint security
	@echo "All checks passed. Ready for GitHub Actions."

gh-release:
	@echo "To create a release:"
	@echo "1. Update version in setup.py"
	@echo "2. Create and push a tag: git tag v1.0.0 && git push origin v1.0.0"
	@echo "3. GitHub Actions will automatically create a release"
