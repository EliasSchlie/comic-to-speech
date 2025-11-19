from unittest.mock import patch
from narration.llm_narrator import narrate_panel

@patch("narration.llm_narrator.get_openai_client")
def test_narrate_panel_success(mock_client):
    instance = mock_client.return_value
    instance.responses.return_value.create.return_value = {
        "output_text": "Narration."
    }

    result = narrate_panel("Girl walks home.")

    assert result["success"] is True
    assert "Narration" in result["narration"]


@patch("narration.llm_narrator.get_openai_client")
def test_narrate_panel_failure(mock_client):
    instance = mock_client.return_value
    instance.responses.return_value.create.side_effect = Exception("LLM error")

    result = narrate_panel("test")

    assert result["success"] is False
