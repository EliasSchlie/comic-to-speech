from unittest.mock import patch, MagicMock
import pytest
import base64
from narration.llm_narrator import ComicNarrator, narrate_panel


# ---------------------------
# Test ComicNarrator Class - Real Logic
# ---------------------------

def test_narrator_init_without_api_key():
    """Test that ComicNarrator fails gracefully without API key"""
    with patch.dict('os.environ', {}, clear=True):
        # Remove OPENAI_API_KEY from environment
        with pytest.raises(ValueError) as exc_info:
            ComicNarrator(api_key=None)

        assert "api key" in str(exc_info.value).lower()


def test_narrator_encode_image_to_base64():
    """Test base64 encoding logic - actual implementation"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        narrator = ComicNarrator(api_key='test-key')

        # Test actual encoding logic
        test_bytes = b"test image data"
        result = narrator._encode_image_to_base64(test_bytes)

        # Verify it's actually base64 encoded
        assert isinstance(result, str)
        assert result == base64.b64encode(test_bytes).decode('utf-8')

        # Verify it can be decoded back
        decoded = base64.b64decode(result)
        assert decoded == test_bytes


def test_narrator_create_prompt_with_panel_context():
    """Test prompt generation logic with panel numbers"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        narrator = ComicNarrator(api_key='test-key')

        # Test with panel context
        prompt_with_context = narrator._create_narration_prompt(panel_number=2, total_panels=5)
        assert "panel 2 of 5" in prompt_with_context.lower()

        # Test without panel context
        prompt_without_context = narrator._create_narration_prompt()
        assert "panel" not in prompt_without_context.lower() or "panel number" not in prompt_without_context.lower()


@patch("narration.llm_narrator.OpenAI")
def test_narrator_narrate_panel_success(mock_openai):
    """Test successful narration with mocked OpenAI API"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "A dramatic scene unfolds."
        mock_response.usage.total_tokens = 45
        mock_client.chat.completions.create.return_value = mock_response

        narrator = ComicNarrator(api_key='test-key')
        result = narrator.narrate_panel(b"fake_image", panel_number=1, total_panels=3)

        # Verify success
        assert result["success"] is True
        assert result["narration"] == "A dramatic scene unfolds."
        assert result["tokens_used"] == 45
        assert result["error"] is None

        # Verify API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4o"


@patch("narration.llm_narrator.OpenAI")
def test_narrator_narrate_panel_api_error(mock_openai):
    """Test narration failure handling when OpenAI API fails"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        # Setup mock to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")

        narrator = ComicNarrator(api_key='test-key')
        result = narrator.narrate_panel(b"fake_image")

        # Verify proper error handling
        assert result["success"] is False
        assert result["narration"] == ""
        assert "rate limit" in result["error"].lower()
        assert result["tokens_used"] is None
