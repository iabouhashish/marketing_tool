# CI/CD Pipeline Documentation

This document describes the CI/CD pipeline setup for the Marketing Project.

## Overview

The project uses GitHub Actions with a streamlined pipeline that includes:
- Automated testing (unit and integration) on Python 3.12
- Code quality checks (linting, formatting, type checking)
- Security scanning (vulnerability and SAST checks)
- Docker image building and publishing
- Automated deployment to staging and production environments

## Pipeline Stages

### 1. Test Stage
- **test:unit**: Runs unit tests with coverage reporting
- **test:integration**: Runs integration tests (marked with `@pytest.mark.integration`)

### 2. Security Stage
- **security:safety**: Scans for known security vulnerabilities in dependencies
- **security:bandit**: Performs static analysis security testing on Python code

### 3. Build Stage
- **build:docker**: Builds and pushes Docker images to GitLab Container Registry

### 4. Deploy Stage
- **deploy:staging**: Automatically deploys to staging environment on `develop` branch
- **deploy:production**: Manual deployment to production environment on `main` branch

## Code Quality Checks

The pipeline includes several code quality checks:

### Linting
- **black**: Code formatting check
- **isort**: Import sorting check
- **flake8**: Style and error checking
- **mypy**: Static type checking

### Security
- **safety**: Dependency vulnerability scanning
- **bandit**: Python security linting

## Docker Configuration

### Dockerfile
- Based on Python 3.12 slim image
- Installs system dependencies and Python packages
- Copies application code and configuration
- Sets up proper entrypoint for run/serve modes

### .dockerignore
- Excludes development files, tests, and documentation
- Optimizes build context size

## Kubernetes Deployment

### Health Checks
- **Liveness Probe**: `/health` endpoint (30s initial delay, 10s interval)
- **Readiness Probe**: `/ready` endpoint (5s initial delay, 5s interval)

### Resource Limits
- **Requests**: 256Mi memory, 250m CPU
- **Limits**: 512Mi memory, 500m CPU

### Environment Variables
- Configuration loaded from ConfigMap
- Secrets loaded from Secret objects
- Entrypoint mode configurable via `ENTRYPOINT_MODE`

## Local Development

### Prerequisites
- Python 3.12+
- Docker (optional)
- kubectl (for deployment)

### Setup
```bash
# Install development dependencies
make install-dev

# Set up development environment
make dev-setup

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Build Docker image
make docker-build

# Run application
make run
# or
make serve
```

## Environment Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for LLM operations
- `MARKETING_PROJECT_LOG_LEVEL`: Logging level (default: DEBUG)
- `MARKETING_PROJECT_LOG_DIR`: Log directory (default: logs)
- `TEMPLATE_VERSION`: Prompt template version (default: v1)

### Optional Environment Variables
- `CONTENT_API_URL`: External content API URL
- `CONTENT_API_KEY`: API key for content API
- `CONTENT_DATABASE_URL`: Database connection string
- `SCRAPE_URLS`: URLs for web scraping

## Deployment Process

### Staging Deployment
1. Push to `develop` branch
2. GitHub Actions automatically triggers
3. Tests and security checks run
4. Docker image is built and pushed to GitHub Container Registry
5. Staging deployment is updated via Kubernetes

### Production Deployment
1. Push to `main` branch or create tag
2. GitHub Actions runs all checks
3. Docker image is built and pushed to GitHub Container Registry
4. Production deployment is automated (or manual via GitHub UI)
5. Use `make deploy-production` or GitHub Actions UI

## Monitoring and Logging

### Health Endpoints
- `GET /health`: Service health status
- `GET /ready`: Service readiness status

### Logging
- Structured logging to separate files by module
- Log levels configurable via environment variables
- Log files rotated daily

### Metrics
- Container resource usage
- Application performance metrics
- Error rates and response times

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies are in requirements.txt
   - Check Docker build context

2. **Test Failures**
   - Run tests locally: `make test`
   - Check test environment setup
   - Verify test data and fixtures

3. **Deployment Issues**
   - Check Kubernetes cluster connectivity
   - Verify image registry access
   - Check resource limits and quotas

4. **Health Check Failures**
   - Verify health endpoints are accessible
   - Check application startup logs
   - Verify configuration loading

### Debug Commands
```bash
# Check application logs
kubectl logs -f deployment/marketing-project-server -n marketing-project

# Check pod status
kubectl get pods -n marketing-project

# Check service status
kubectl get svc -n marketing-project

# Check ingress status
kubectl get ingress -n marketing-project
```

## Security Considerations

- All secrets stored in Kubernetes Secret objects
- Container images scanned for vulnerabilities
- Code security analysis performed on every commit
- Network policies can be applied for additional security
- Regular dependency updates recommended

## Performance Optimization

- Multi-stage Docker builds for smaller images
- Resource limits prevent resource exhaustion
- Horizontal Pod Autoscaling (HPA) configured
- Caching strategies for content sources
- Connection pooling for database connections
