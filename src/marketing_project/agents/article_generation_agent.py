"""
Article Generation processing agent for Marketing Project.

This agent handles high-quality article generation based on marketing briefs,
SEO keywords, and content strategy for comprehensive content creation.
"""

from any_agent import AnyAgent, AgentConfig
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.core.prompts import load_agent_prompt
from marketing_project.plugins.article_generation import tasks as article_tasks
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()

async def get_article_generation_agent(prompts_dir, lang="en"):
    """
    Creates and returns an Article Generation processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured article generation agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "article_generation_agent", lang)
    
    # Add article generation-specific tools
    tools = [
        article_tasks.generate_article_structure,
        article_tasks.write_article_content,
        article_tasks.add_supporting_elements,
        article_tasks.review_article_quality,
        article_tasks.optimize_article_flow,
        article_tasks.add_call_to_actions
    ]
    
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="ArticleGenerationAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
