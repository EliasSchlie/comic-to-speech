import pytest
from unittest.mock import patch, MagicMock
from llm_narrator import ComicNarrator

@pytest.fixture
def narrator():
    return ComicNarrator(api_key="fake")

@patch("openai.resources.chat.completions.Completions.create")
def test_narrate_panel_success(mock_openai, narrator):
    mock_openai.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Sample narration"))],
        usage=MagicMock(total_tokens=42)
    )

    result = narrator.narrate_panel(b"fakeimage")
    assert result["success"] is True
    assert "Sample narration" in result["narration"]
    assert result["tokens_used"] == 42


@patch("openai.resources.chat.completions.Completions.create", side_effect=Exception("API failure"))
def test_narrate_panel_failure(mock_openai, narrator):
    result = narrator.narrate_panel(b"fakeimage")
    assert result["success"] is False
    assert "error" in result
