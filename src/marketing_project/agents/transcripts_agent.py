"""
Transcript processing agent for Marketing Project.

This agent handles analysis and processing of transcript content including
podcasts, videos, meetings, and interviews.
"""

from any_agent import AnyAgent, AgentConfig
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.core.prompts import load_agent_prompt
from marketing_project.plugins.transcripts import tasks as transcript_tasks
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()

async def get_transcripts_agent(prompts_dir, lang="en"):
    """
    Creates and returns a Transcript processing agent.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")

    Returns:
        AnyAgent: Configured transcript agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "transcripts_agent", lang)
    
    # Add transcript-specific tools
    tools = [
        transcript_tasks.analyze_transcript_type,
        transcript_tasks.extract_transcript_metadata,
        transcript_tasks.validate_transcript_structure,
        transcript_tasks.enhance_transcript_with_ocr,
        transcript_tasks.route_transcript_processing
    ]
    
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="TranscriptsAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
