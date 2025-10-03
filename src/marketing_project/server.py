"""
Marketing Project FastAPI server module.

This module defines the FastAPI application for the marketing project MCP server. It loads configuration, initializes shared services, and exposes an endpoint to trigger the project pipeline asynchronously.

Endpoints:
    POST /run: Triggers the project pipeline as a background task and returns immediately with a 202 Accepted status.

Usage:
    Run this module directly to start a local development server with Uvicorn.
"""

# src/marketing_project/server.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os, yaml
import logging

from marketing_project.runner import run_marketing_project_pipeline
from marketing_project.scheduler import Scheduler

# Initialize logger
logger = logging.getLogger('marketing_project.server')

app = FastAPI(title="Marketing Project MCP Server")

# Load config once
BASE        = os.path.dirname(__file__)
SPEC_PATH   = os.path.abspath(os.path.join(BASE, "..", "..", "config", "pipeline.yml"))
with open(SPEC_PATH) as f:
    PIPELINE_SPEC = yaml.safe_load(f)
TEMPLATE_VERSION = os.getenv("TEMPLATE_VERSION", "v1")
PROMPTS_DIR      = os.path.abspath(os.path.join(BASE, "prompts", TEMPLATE_VERSION))

# Instantiate shared services
scheduler   = Scheduler()

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns 200 OK if the service is healthy.
    """
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "service": "marketing-project",
            "version": "1.0.0",
            "checks": {
                "config_loaded": PIPELINE_SPEC is not None,
                "prompts_dir_exists": os.path.exists(PROMPTS_DIR),
                "scheduler_ready": scheduler is not None
            }
        }
        
        # Check if any critical checks failed
        if not all(health_status["checks"].values()):
            health_status["status"] = "unhealthy"
            return JSONResponse(
                status_code=503,
                content=health_status
            )
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes probes.
    Returns 200 OK if the service is ready to accept traffic.
    """
    try:
        # Check if the service is ready to process requests
        ready_status = {
            "status": "ready",
            "service": "marketing-project",
            "checks": {
                "config_loaded": PIPELINE_SPEC is not None,
                "prompts_dir_exists": os.path.exists(PROMPTS_DIR),
                "scheduler_ready": scheduler is not None
            }
        }
        
        if not all(ready_status["checks"].values()):
            ready_status["status"] = "not_ready"
            return JSONResponse(
                status_code=503,
                content=ready_status
            )
        
        return ready_status
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e)
            }
        )

@app.post("/run")
async def run_pipeline(background: BackgroundTasks):
    """
    Trigger the Marketing Project pipeline asynchronously.
    Returns immediately with a 202 Accepted.
    """
    try:
        background.add_task(run_marketing_project_pipeline, PROMPTS_DIR, "en")
        logger.info("Pipeline execution triggered")
        return {"status": "accepted", "message": "Pipeline execution started"}
    except Exception as e:
        logger.error(f"Failed to trigger pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger pipeline: {str(e)}")

if __name__ == "__main__":
    # local dev server
    uvicorn.run("marketing_project.server:app", host="0.0.0.0", port=8000, reload=True)
