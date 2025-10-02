import pytest

# Test configuration for Marketing Project

# Dummy LLM to avoid any real API/network calls in plugin tasks
class DummyLLM:
    def __call__(self, prompt, **kwargs):
        if "transcript" in prompt.lower():
            return "Test transcript analysis result"
        elif "blog" in prompt.lower():
            return "Test blog post analysis result"
        elif "release" in prompt.lower():
            return "Test release notes analysis result"
        return "Dummy response"

@pytest.fixture(autouse=True)
def patch_llms(monkeypatch):
    # Mock LLM for any plugin tasks that might use it
    # This can be extended when needed for specific plugin tests
    pass