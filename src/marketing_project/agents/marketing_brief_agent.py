"""
Marketing Brief processing agent for Marketing Project.

This agent handles marketing brief generation, target audience definition,
and content strategy creation for comprehensive marketing planning.
"""

import logging
from typing import Any, Dict, Optional

from any_agent import AgentConfig, AnyAgent

from marketing_project.core.prompts import load_agent_prompt
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.plugins.marketing_brief import tasks as brief_tasks

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()


async def get_marketing_brief_agent(prompts_dir, lang="en"):
    """
    Creates and returns a Marketing Brief processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured marketing brief agent
    """
    instructions, description = load_agent_prompt(
        prompts_dir, "marketing_brief_agent", lang
    )

    # Add marketing brief-specific tools
    tools = [
        brief_tasks.generate_brief_outline,
        brief_tasks.define_target_audience,
        brief_tasks.set_content_objectives,
        brief_tasks.create_content_strategy,
        brief_tasks.analyze_competitor_content,
        brief_tasks.generate_content_calendar_suggestions,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="MarketingBriefAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
