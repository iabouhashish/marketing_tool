"""
Design Kit processing agent for Marketing Project.

This agent handles design template selection, brand guidelines application,
visual component generation, responsive layout optimization, and design compliance validation.
"""

import logging
from typing import Any, Dict, Optional

from any_agent import AgentConfig, AnyAgent

from marketing_project.core.prompts import load_agent_prompt
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.plugins.design_kit import tasks as design_kit_tasks

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()


async def get_design_kit_agent(prompts_dir, lang="en"):
    """
    Creates and returns a Design Kit processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured design kit agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "design_kit_agent", lang)

    # Add design kit-specific tools
    tools = [
        design_kit_tasks.select_design_template,
        design_kit_tasks.apply_brand_guidelines,
        design_kit_tasks.generate_visual_components,
        design_kit_tasks.optimize_responsive_layout,
        design_kit_tasks.create_visual_assets,
        design_kit_tasks.validate_design_compliance,
        design_kit_tasks.apply_design_kit_enhancement,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="DesignKitAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
