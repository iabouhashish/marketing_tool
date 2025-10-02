"""
Content Formatting processing agent for Marketing Project.

This agent handles content formatting, readability optimization,
visual elements, and final publication preparation.
"""

from any_agent import AnyAgent, AgentConfig
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.core.prompts import load_agent_prompt
from marketing_project.plugins.content_formatting import tasks as formatting_tasks
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()

async def get_content_formatting_agent(prompts_dir, lang="en"):
    """
    Creates and returns a Content Formatting processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured content formatting agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "content_formatting_agent", lang)
    
    # Add content formatting-specific tools
    tools = [
        formatting_tasks.apply_formatting_rules,
        formatting_tasks.optimize_readability,
        formatting_tasks.add_visual_elements,
        formatting_tasks.finalize_content,
        formatting_tasks.validate_formatting,
        formatting_tasks.generate_publication_ready_content
    ]
    
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="ContentFormattingAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
