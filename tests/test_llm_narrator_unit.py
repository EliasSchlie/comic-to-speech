import pytest
from unittest.mock import patch, MagicMock
from llm_narrator import ComicNarrator

@patch("llm_narrator.OpenAI")
def test_narrate_panel_success(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Narration text"))],
        usage=MagicMock(total_tokens=42)
    )

    narrator = ComicNarrator(api_key="test")

    result = narrator.narrate_panel(b"fakeimage")

    assert result["success"] is True
    assert result["narration"] == "Narration text"
    assert result["tokens_used"] == 42


@patch("llm_narrator.OpenAI")
def test_narrate_panel_failure(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_client.chat.completions.create.side_effect = Exception("API error")

    narrator = ComicNarrator(api_key="test")
    result = narrator.narrate_panel(b"fakeimage")

    assert result["success"] is False
    assert "API error" in result["error"]
