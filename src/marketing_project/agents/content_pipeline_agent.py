"""
Content Pipeline Orchestrator Agent for Marketing Project.

This agent serves as the main orchestrator for the new 7-step content pipeline:
1. AnalyzeContent → 2. ExtractSEOKeywords → 3. GenerateMarketingBrief → 
4. GenerateArticle → 5. OptimizeSEO → 6. SuggestInternalDocs → 7. FormatContent

The orchestrator handles the complete content analysis and generation workflow.
"""

from any_agent import AnyAgent, AgentConfig
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.core.prompts import load_agent_prompt
from marketing_project.plugins.content_analysis import tasks as content_analysis_tasks
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()

async def get_content_pipeline_agent(
    prompts_dir, 
    lang="en", 
    content_analysis_agent=None,
    seo_keywords_agent=None,
    marketing_brief_agent=None,
    article_generation_agent=None,
    seo_optimization_agent=None,
    internal_docs_agent=None,
    content_formatting_agent=None
):
    """
    Creates and returns a Content Pipeline Orchestrator agent that manages
    the complete 7-step content analysis and generation workflow.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")
        content_analysis_agent (AnyAgent): Agent for content analysis
        seo_keywords_agent (AnyAgent): Agent for SEO keywords extraction
        marketing_brief_agent (AnyAgent): Agent for marketing brief generation
        article_generation_agent (AnyAgent): Agent for article generation
        seo_optimization_agent (AnyAgent): Agent for SEO optimization
        internal_docs_agent (AnyAgent): Agent for internal docs suggestions
        content_formatting_agent (AnyAgent): Agent for content formatting

    Returns:
        AnyAgent: Configured content pipeline orchestrator agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "content_pipeline_agent", lang)
    
    # Build tools list from all pipeline agents
    tools = []
    
    # Add content analysis tools (enhanced existing plugin)
    tools.extend([
        content_analysis_tasks.analyze_content_for_pipeline,
        content_analysis_tasks.analyze_content_type,
        content_analysis_tasks.extract_content_metadata,
        content_analysis_tasks.validate_content_structure,
        content_analysis_tasks.route_to_appropriate_agent
    ])
    
    # Add agent tools if available
    if content_analysis_agent:
        tools.append(content_analysis_agent.run_async)
        logger.info("Added content_analysis_agent to pipeline orchestrator tools")
    if seo_keywords_agent:
        tools.append(seo_keywords_agent.run_async)
        logger.info("Added seo_keywords_agent to pipeline orchestrator tools")
    if marketing_brief_agent:
        tools.append(marketing_brief_agent.run_async)
        logger.info("Added marketing_brief_agent to pipeline orchestrator tools")
    if article_generation_agent:
        tools.append(article_generation_agent.run_async)
        logger.info("Added article_generation_agent to pipeline orchestrator tools")
    if seo_optimization_agent:
        tools.append(seo_optimization_agent.run_async)
        logger.info("Added seo_optimization_agent to pipeline orchestrator tools")
    if internal_docs_agent:
        tools.append(internal_docs_agent.run_async)
        logger.info("Added internal_docs_agent to pipeline orchestrator tools")
    if content_formatting_agent:
        tools.append(content_formatting_agent.run_async)
        logger.info("Added content_formatting_agent to pipeline orchestrator tools")
    
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="ContentPipelineAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
