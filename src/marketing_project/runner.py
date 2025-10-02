import json
import os
from datetime import datetime
from marketing_project.agents.transcripts_agent import get_transcripts_agent
from marketing_project.agents.blog_agent import get_blog_agent
from marketing_project.agents.releasenotes_agent import get_releasenotes_agent
from marketing_project.agents.marketing_agent import get_marketing_orchestrator_agent
from marketing_project.agents.content_pipeline_agent import get_content_pipeline_agent
from marketing_project.agents.seo_keywords_agent import get_seo_keywords_agent
from marketing_project.agents.marketing_brief_agent import get_marketing_brief_agent
from marketing_project.agents.article_generation_agent import get_article_generation_agent
from marketing_project.agents.seo_optimization_agent import get_seo_optimization_agent
from marketing_project.agents.internal_docs_agent import get_internal_docs_agent
from marketing_project.agents.content_formatting_agent import get_content_formatting_agent
from marketing_project.core.models import (
    AppContext, TranscriptContext, BlogPostContext, ReleaseNotesContext
)

# For HTTP serving (optional)
from fastapi import FastAPI, BackgroundTasks
import uvicorn

async def run_marketing_project_pipeline(prompts_dir, lang):
    """
    Run the Marketing Project pipeline for content processing.
    
    This pipeline processes different types of content:
    - Transcripts (podcasts, videos, meetings)
    - Blog posts (articles, tutorials)
    - Release notes (software releases, updates)
    """
    # Set up specialized agents and orchestrator
    transcripts_agent = await get_transcripts_agent(prompts_dir, lang)
    blog_agent = await get_blog_agent(prompts_dir, lang)
    releasenotes_agent = await get_releasenotes_agent(prompts_dir, lang)
    orchestrator_agent = await get_marketing_orchestrator_agent(
        prompts_dir, lang, transcripts_agent, blog_agent, releasenotes_agent
    )
    
    # Content processing pipeline
    # In practice, content would come from your actual sources:
    # - Content management systems
    # - APIs (YouTube, podcast platforms, etc.)
    # - File uploads
    # - Web scraping
    # - Database queries
    
    # TODO: Implement content source integration
    # For now, the pipeline is ready to process content when provided
    print("Marketing Project pipeline initialized and ready for content processing")
    print("Available agents:")
    print("- Transcripts Agent: For podcasts, videos, meetings")
    print("- Blog Agent: For articles, tutorials, written content") 
    print("- Release Notes Agent: For software releases, updates")
    print("- Orchestrator Agent: Routes content to appropriate agents")

async def run_content_analysis_pipeline(prompts_dir, lang):
    """
    Run the new Content Analysis Pipeline for comprehensive content processing.
    
    This pipeline follows a 7-step workflow:
    1. AnalyzeContent → 2. ExtractSEOKeywords → 3. GenerateMarketingBrief → 
    4. GenerateArticle → 5. OptimizeSEO → 6. SuggestInternalDocs → 7. FormatContent
    """
    # Set up all specialized agents for the new pipeline
    seo_keywords_agent = await get_seo_keywords_agent(prompts_dir, lang)
    marketing_brief_agent = await get_marketing_brief_agent(prompts_dir, lang)
    article_generation_agent = await get_article_generation_agent(prompts_dir, lang)
    seo_optimization_agent = await get_seo_optimization_agent(prompts_dir, lang)
    internal_docs_agent = await get_internal_docs_agent(prompts_dir, lang)
    content_formatting_agent = await get_content_formatting_agent(prompts_dir, lang)
    
    # Create the main content pipeline orchestrator
    content_pipeline_agent = await get_content_pipeline_agent(
        prompts_dir, lang,
        seo_keywords_agent=seo_keywords_agent,
        marketing_brief_agent=marketing_brief_agent,
        article_generation_agent=article_generation_agent,
        seo_optimization_agent=seo_optimization_agent,
        internal_docs_agent=internal_docs_agent,
        content_formatting_agent=content_formatting_agent
    )
    
    print("Content Analysis Pipeline initialized and ready for processing")
    print("Available agents:")
    print("- SEO Keywords Agent: Extract and analyze SEO keywords")
    print("- Marketing Brief Agent: Generate marketing briefs and strategy")
    print("- Article Generation Agent: Create high-quality articles")
    print("- SEO Optimization Agent: Apply comprehensive SEO optimizations")
    print("- Internal Docs Agent: Suggest internal documents and cross-references")
    print("- Content Formatting Agent: Format and finalize content")
    print("- Content Pipeline Agent: Orchestrates the complete 7-step workflow")
    
    return content_pipeline_agent
    

# Optional: Async FastAPI server for MCP/K8s deployment
def build_fastapi_app(prompts_dir, lang):
    app = FastAPI(title="Marketing Project Server")

    @app.post("/run")
    async def run_pipeline_endpoint(background: BackgroundTasks):
        background.add_task(run_marketing_project_pipeline, prompts_dir, lang)
        return {"status": "accepted"}
    return app

async def run_marketing_project_server(host, port, prompts_dir, lang):
    app = build_fastapi_app(prompts_dir, lang)
    uvicorn.run(app, host=host, port=port)
