"""
Internal Documents processing agent for Marketing Project.

This agent handles internal document suggestions, cross-references,
and content relationship mapping for enhanced content strategy.
"""

import logging
from typing import Any, Dict, Optional

from any_agent import AgentConfig, AnyAgent

from marketing_project.core.prompts import load_agent_prompt
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.plugins.internal_docs import tasks as internal_docs_tasks

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()


async def get_internal_docs_agent(prompts_dir, lang="en"):
    """
    Creates and returns an Internal Documents processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured internal docs agent
    """
    instructions, description = load_agent_prompt(
        prompts_dir, "internal_docs_agent", lang
    )

    # Add internal docs-specific tools
    tools = [
        internal_docs_tasks.analyze_content_gaps,
        internal_docs_tasks.suggest_related_docs,
        internal_docs_tasks.identify_cross_references,
        internal_docs_tasks.generate_doc_suggestions,
        internal_docs_tasks.create_content_relationships,
        internal_docs_tasks.optimize_internal_linking,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="InternalDocsAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
