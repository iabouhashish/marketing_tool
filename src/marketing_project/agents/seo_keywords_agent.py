"""
SEO Keywords processing agent for Marketing Project.

This agent handles SEO keyword extraction, analysis, and optimization
for content marketing and search engine visibility.
"""

import logging
from typing import Any, Dict, Optional

from any_agent import AgentConfig, AnyAgent

from marketing_project.core.prompts import load_agent_prompt
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.plugins.seo_keywords import tasks as seo_tasks

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()


async def get_seo_keywords_agent(prompts_dir, lang="en"):
    """
    Creates and returns a SEO Keywords processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured SEO keywords agent
    """
    instructions, description = load_agent_prompt(
        prompts_dir, "seo_keywords_agent", lang
    )

    # Add SEO keywords-specific tools
    tools = [
        seo_tasks.extract_primary_keywords,
        seo_tasks.extract_secondary_keywords,
        seo_tasks.analyze_keyword_density,
        seo_tasks.generate_keyword_suggestions,
        seo_tasks.optimize_keyword_placement,
        seo_tasks.calculate_keyword_scores,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="SEOKeywordsAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
