from unittest.mock import patch
from workers.tasks import process_comic_full_pipeline

@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_translation_task")
@patch("workers.tasks.process_tts_task")
def test_full_pipeline(mock_tts, mock_trans, mock_ocr):

    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Hello",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": [],
        "confidence": 0.9
    }

    mock_trans.return_value = {
        "success": True,
        "translated_text": "Hallo"
    }

    mock_tts.return_value = {
        "success": True,
        "audio_id": "123",
        "audio_url": "/audio/123",
        "characters_used": 5
    }

    result = process_comic_full_pipeline(
        b"fake",
        language_code="en-US",
        voice_name="TestVoice",
        preprocess=True,
        translate=True,
        target_language="nl"
    )

    assert result["success"] is True
    assert result["translated_text"] == "Hallo"
    assert result["audio_id"] == "123"
