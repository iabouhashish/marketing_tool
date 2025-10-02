# Marketing Project Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Marketing Project to a Kubernetes cluster.

## Files Overview

- `namespace.yml` - Creates the marketing-project namespace
- `configmap.yml` - Configuration values for the application
- `secret-template.yml` - Template for secrets (copy and fill with actual values)
- `deployment.yml` - Main application deployment
- `service.yml` - Service to expose the application
- `ingress.yml` - Ingress for external access with TLS
- `hpa.yml` - Horizontal Pod Autoscaler for automatic scaling
- `cronjob.yml` - CronJob to trigger the marketing pipeline

## Quick Start

1. **Create the namespace:**
   ```bash
   kubectl apply -f namespace.yml
   ```

2. **Create secrets:**
   ```bash
   # Copy the template and fill with actual values
   cp secret-template.yml secret.yml
   # Edit secret.yml with your actual base64-encoded secrets
   kubectl apply -f secret.yml
   ```

3. **Deploy the application:**
   ```bash
   kubectl apply -f configmap.yml
   kubectl apply -f deployment.yml
   kubectl apply -f service.yml
   kubectl apply -f ingress.yml
   kubectl apply -f hpa.yml
   kubectl apply -f cronjob.yml
   ```

## Configuration

### Environment Variables

The application uses the following environment variables:

- `OPENAI_API_KEY` - OpenAI API key for AI processing
- `TEMPLATE_VERSION` - Version of prompts to use (default: v1)
- `LOG_LEVEL` - Logging level (default: INFO)

### Resource Requirements

- **CPU:** 250m request, 500m limit
- **Memory:** 256Mi request, 512Mi limit

### Scaling

The HPA is configured to:
- Scale based on CPU (70% utilization) and memory (80% utilization)
- Scale from 1 to 10 replicas
- Use conservative scaling policies

## Monitoring

The deployment includes:
- Liveness and readiness probes
- Resource limits and requests
- Health check endpoint at `/health`

## Security

- Secrets are stored in Kubernetes secrets
- TLS termination at the ingress level
- Resource limits prevent resource exhaustion
- Read-only secret mounts

## Troubleshooting

1. **Check pod status:**
   ```bash
   kubectl get pods -n marketing-project
   ```

2. **View logs:**
   ```bash
   kubectl logs -f deployment/marketing-project-server -n marketing-project
   ```

3. **Check events:**
   ```bash
   kubectl get events -n marketing-project
   ```

4. **Test the service:**
   ```bash
   kubectl port-forward service/marketing-project 8000:80 -n marketing-project
   curl http://localhost:8000/health
   ```
