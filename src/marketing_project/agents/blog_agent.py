"""
Blog post processing agent for Marketing Project.

This agent handles analysis and processing of blog post content including
articles, tutorials, and other written content.
"""

import logging
from typing import Any, Dict, Optional

from any_agent import AgentConfig, AnyAgent

from marketing_project.core.prompts import load_agent_prompt
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.plugins.blog_posts import tasks as blog_tasks

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()


async def get_blog_agent(prompts_dir, lang="en"):
    """
    Creates and returns a Blog post processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured blog agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "blog_agent", lang)

    # Add blog-specific tools
    tools = [
        blog_tasks.analyze_blog_post_type,
        blog_tasks.extract_blog_post_metadata,
        blog_tasks.validate_blog_post_structure,
        blog_tasks.enhance_blog_post_with_ocr,
        blog_tasks.route_blog_post_processing,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="BlogAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
