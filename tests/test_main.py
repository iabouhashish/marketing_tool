import os
import sys

import click
import pytest
from click.testing import CliRunner

from marketing_project.main import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_main_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Marketing Project CLI" in result.output


def test_run_pipeline_default(monkeypatch, runner):
    async def dummy_run_pipeline(lang, prompts_dir):
        pass

    monkeypatch.setattr(
        "marketing_project.main._run_pipeline_async", dummy_run_pipeline
    )
    result = runner.invoke(cli, ["run"])
    assert result.exit_code == 0


def test_run_pipeline_custom(monkeypatch, runner, tmp_path):
    called = {}

    async def fake_run(lang, prompts_dir):
        called["lang"] = lang
        called["prompts_dir"] = prompts_dir

    monkeypatch.setattr("marketing_project.main._run_pipeline_async", fake_run)
    prompts_dir = str(tmp_path)
    result = runner.invoke(cli, ["run", "--lang", "fr", "--prompts-dir", prompts_dir])
    assert result.exit_code == 0
    assert called["lang"] == "fr"
    assert called["prompts_dir"] == prompts_dir


def test_serve_server(monkeypatch, runner):
    async def dummy_run_server(host, port, lang, prompts_dir):
        pass

    monkeypatch.setattr("marketing_project.main._run_server_async", dummy_run_server)
    result = runner.invoke(
        cli, ["serve", "--host", "127.0.0.1", "--port", "9000", "--lang", "en"]
    )
    assert result.exit_code == 0


def test_test_command_removed(runner):
    """Test that the test command was removed from CLI."""
    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 2  # Command not found
    assert "No such command" in result.output or "Usage:" in result.output


def test_run_pipeline_exception(monkeypatch, runner):
    async def fail_run(lang, prompts_dir):
        raise RuntimeError("fail!")

    monkeypatch.setattr("marketing_project.main._run_pipeline_async", fail_run)
    result = runner.invoke(cli, ["run"])
    assert result.exit_code != 0
    # Optionally, check exception message if output is present
    # assert "fail" in result.output.lower() or "fail" in result.exception.args[0].lower()
