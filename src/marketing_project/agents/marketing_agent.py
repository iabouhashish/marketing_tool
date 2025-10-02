"""
Marketing Project Orchestrator Agent.

This agent serves as the main orchestrator for the Marketing Project, routing content
to the three specialized agents: transcripts, blog posts, and release notes.

The orchestrator handles:
- TranscriptContext → transcripts_agent
- BlogPostContext → blog_agent  
- ReleaseNotesContext → releasenotes_agent
"""

from any_agent import AnyAgent, AgentConfig
from marketing_project.logging_config import LangChainLoggingCallbackHandler
from marketing_project.core.prompts import load_agent_prompt
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("marketing_project.agents")
handler = LangChainLoggingCallbackHandler()

async def get_marketing_orchestrator_agent(prompts_dir, lang="en", transcripts_agent=None, blog_agent=None, releasenotes_agent=None):
    """
    Creates and returns a Marketing Project Orchestrator agent that routes content
    to the three specialized agents.

    Args:
        prompts_dir (str): Directory containing agent prompt templates
        lang (str): Language code for prompts (default: "en")
        transcripts_agent (AnyAgent): Agent for processing transcripts
        blog_agent (AnyAgent): Agent for processing blog posts
        releasenotes_agent (AnyAgent): Agent for processing release notes

    Returns:
        AnyAgent: Configured orchestrator agent
    """
    instructions, description = load_agent_prompt(prompts_dir, "marketing_orchestrator_agent", lang)
    
    # Build tools list from the three main agents
    tools = []
    if transcripts_agent:
        tools.append(transcripts_agent.run_async)
        logger.info("Added transcripts_agent to orchestrator tools")
    if blog_agent:
        tools.append(blog_agent.run_async)
        logger.info("Added blog_agent to orchestrator tools")
    if releasenotes_agent:
        tools.append(releasenotes_agent.run_async)
        logger.info("Added releasenotes_agent to orchestrator tools")
    
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="MarketingOrchestratorAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
