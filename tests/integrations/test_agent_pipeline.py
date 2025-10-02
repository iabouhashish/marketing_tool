import pytest

@pytest.mark.asyncio
async def test_full_pipeline(monkeypatch, tmp_path):
    # Create dummy prompt templates for all agents
    lang = "en"
    d = tmp_path / lang
    d.mkdir(parents=True)
    for name in ["marketing_agent", "content_pipeline_agent"]:
        (d / f"{name}_instructions.j2").write_text("Prompt")
        (d / f"{name}_description.j2").write_text("Description")

    from marketing_project.runner import run_marketing_project_pipeline

    await run_marketing_project_pipeline(str(tmp_path), lang)
