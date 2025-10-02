"""
SEO Optimization processing agent for Marketing Project.

This agent handles comprehensive SEO optimization including title tags,
meta descriptions, headings, content structure, and internal linking.
"""

from any_agent import AnyAgent, AgentConfig
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.core.prompts import load_agent_prompt
from marketing_project.plugins.seo_optimization import tasks as seo_opt_tasks
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()

async def get_seo_optimization_agent(prompts_dir, lang="en"):
    """
    Creates and returns a SEO Optimization processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured SEO optimization agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "seo_optimization_agent", lang)
    
    # Add SEO optimization-specific tools
    tools = [
        seo_opt_tasks.optimize_title_tags,
        seo_opt_tasks.optimize_meta_descriptions,
        seo_opt_tasks.optimize_headings,
        seo_opt_tasks.optimize_content_structure,
        seo_opt_tasks.add_internal_links,
        seo_opt_tasks.analyze_seo_performance
    ]
    
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="SEOOptimizationAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
