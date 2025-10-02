"""
Marketing Project FastAPI server module.

This module defines the FastAPI application for the marketing project MCP server. It loads configuration, initializes shared services, and exposes an endpoint to trigger the project pipeline asynchronously.

Endpoints:
    POST /run: Triggers the project pipeline as a background task and returns immediately with a 202 Accepted status.

Usage:
    Run this module directly to start a local development server with Uvicorn.
"""

# src/marketing_project/server.py
from fastapi import FastAPI, BackgroundTasks
import uvicorn
import os, yaml

from marketing_project.runner import run_marketing_project_pipeline
from marketing_project.scheduler import Scheduler

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

@app.post("/run")
async def run_pipeline(background: BackgroundTasks):
    """
    Trigger the Marketing Project pipeline asynchronously.
    Returns immediately with a 202 Accepted.
    """
    background.add_task(run_marketing_project_pipeline, PROMPTS_DIR, "en")
    return {"status": "accepted"}

if __name__ == "__main__":
    # local dev server
    uvicorn.run("marketing_project.server:app", host="0.0.0.0", port=8000, reload=True)
