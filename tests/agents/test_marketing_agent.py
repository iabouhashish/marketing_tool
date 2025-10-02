import pytest
from marketing_project.agents.marketing_agent import get_marketing_orchestrator_agent

class DummyAgent:
    async def run_async(self, ctx: dict) -> str:
        """
        Asynchronously executes the main logic for the agent.

        Args:
            ctx: The context object containing relevant information for execution.

        Returns:
            str: The result of the asynchronous operation, "ok" in this case.
        """
        return "ok"

@pytest.mark.asyncio
async def test_get_marketing_orchestrator_agent(tmp_path):
    """
    Test the asynchronous creation of a Marketing Orchestrator agent with dynamically generated prompt files.

    This test verifies that:
    - The required prompt files for the specified language are created in a temporary directory.
    - The `get_marketing_orchestrator_agent` function correctly loads these prompts and initializes the agent.
    - The resulting agent's configuration has the expected name ("MarketingOrchestratorAgent").
    - The agent's instructions contain the expected content.

    Args:
        tmp_path (pathlib.Path): Temporary directory provided by pytest for file operations.

    Raises:
        AssertionError: If the agent's configuration does not match the expected values.
    """
    prompts_dir = tmp_path
    lang = "en"
    d = prompts_dir / lang
    d.mkdir(parents=True)
    (d / "marketing_orchestrator_agent_instructions.j2").write_text("You are the marketing orchestrator.")
    (d / "marketing_orchestrator_agent_description.j2").write_text("Handles content routing.")
    transcripts_agent = DummyAgent()
    blog_agent = DummyAgent()
    releasenotes_agent = DummyAgent()
    agent = await get_marketing_orchestrator_agent(str(prompts_dir), lang, transcripts_agent, blog_agent, releasenotes_agent)
    assert agent.config.name == "MarketingOrchestratorAgent"
    assert "marketing" in agent.config.instructions
