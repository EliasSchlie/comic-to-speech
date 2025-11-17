import pytest
from unittest.mock import patch, MagicMock
from tasks import process_comic_full_pipeline

@patch("tasks.process_ocr_task")
@patch("tasks.process_translation_task")
@patch("tasks.process_tts_task")
def test_full_pipeline(mock_tts, mock_trans, mock_ocr):

    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Hello world",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": [],
        "confidence": 0.9
    }

    mock_trans.return_value = {
        "success": True,
        "translated_text": "Hallo wereld"
    }

    mock_tts.return_value = {
        "success": True,
        "audio_id": "123",
        "audio_url": "/api/audio/123"
    }

    result = process_comic_full_pipeline(
        b"fake",
        language_code="en-US",
        voice_name="en-US-Neural2-F",
        preprocess=True,
        translate=True,
        target_language="nl"
    )

    assert result["success"] is True
    assert result["extracted_text"] == "Hello world"
    assert result["translated_text"] == "Hallo wereld"
    assert result["audio_id"] == "123"
