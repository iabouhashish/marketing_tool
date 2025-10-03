"""
Release notes processing agent for Marketing Project.

This agent handles analysis and processing of release notes content including
software releases, product updates, and version announcements.
"""

import logging
from typing import Any, Dict, Optional

from any_agent import AgentConfig, AnyAgent

from marketing_project.core.prompts import load_agent_prompt
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.plugins.release_notes import tasks as release_tasks

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()


async def get_releasenotes_agent(prompts_dir, lang="en"):
    """
    Creates and returns a Release notes processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured release notes agent
    """
    instructions, description = load_agent_prompt(
        prompts_dir, "releasenotes_agent", lang
    )

    # Add release notes-specific tools
    tools = [
        release_tasks.analyze_release_type,
        release_tasks.extract_release_metadata,
        release_tasks.validate_release_structure,
        release_tasks.enhance_release_notes_with_ocr,
        release_tasks.route_release_processing,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="ReleaseNotesAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
