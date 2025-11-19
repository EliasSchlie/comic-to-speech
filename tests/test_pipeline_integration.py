from unittest.mock import patch
from workers.tasks import process_comic_full_pipeline


@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_translation_task")
@patch("workers.tasks.process_tts_task")
def test_full_pipeline_with_translation(mock_tts, mock_trans, mock_ocr):
    """
    Integration test: Full pipeline with translation enabled
    Tests orchestration logic: OCR -> Translation -> TTS with translated text
    """

    # Mock OCR to return extracted text
    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Hello world",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": 0,
        "confidence": 0.9,
        "narration_mode": "ocr",
        "tokens_used": None
    }

    # Mock translation to return translated text
    mock_trans.return_value = {
        "success": True,
        "translated_text": "Hallo wereld"
    }

    # Mock TTS to return audio info
    mock_tts.return_value = {
        "success": True,
        "audio_id": "123",
        "audio_url": "/audio/123",
        "characters_used": 12
    }

    # Run the full pipeline with translation
    result = process_comic_full_pipeline(
        b"fake_image_bytes",
        language_code="nl-NL",
        voice_name="nl-NL-Standard-A",
        preprocess=True,
        translate=True,
        target_language="nl"
    )

    # Verify orchestration logic: all steps completed
    assert result["success"] is True
    assert result["extracted_text"] == "Hello world"
    assert result["translated_text"] == "Hallo wereld"
    assert result["audio_id"] == "123"
    assert result["translation_enabled"] is True
    assert result["target_language"] == "nl"

    # Verify TTS received the TRANSLATED text (orchestration logic)
    mock_tts.assert_called_once_with("Hallo wereld", "nl-NL", "nl-NL-Standard-A")


@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_tts_task")
def test_full_pipeline_without_translation(mock_tts, mock_ocr):
    """
    Integration test: Pipeline without translation
    Tests that translation step is skipped when translate=False
    """

    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Hello world",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": 0,
        "confidence": 0.9,
        "narration_mode": "ocr",
        "tokens_used": None
    }

    mock_tts.return_value = {
        "success": True,
        "audio_id": "456",
        "audio_url": "/audio/456",
        "characters_used": 11
    }

    # Run without translation
    result = process_comic_full_pipeline(
        b"fake_image_bytes",
        translate=False
    )

    # Verify translation was skipped (orchestration logic)
    assert result["success"] is True
    assert result["extracted_text"] == "Hello world"
    assert "translated_text" not in result or result.get("translation_enabled") is None

    # Verify TTS received the ORIGINAL text (orchestration logic)
    mock_tts.assert_called_once()
    call_args = mock_tts.call_args[0]
    assert call_args[0] == "Hello world"


@patch("workers.tasks.process_ocr_task")
def test_pipeline_stops_on_ocr_failure(mock_ocr):
    """
    Integration test: Pipeline should stop if OCR fails
    Tests early-exit orchestration logic
    """

    mock_ocr.return_value = {
        "success": False,
        "error": "OCR failed to process image"
    }

    result = process_comic_full_pipeline(b"bad_image")

    # Verify pipeline stopped at OCR (orchestration logic)
    assert result["success"] is False
    assert "OCR failed" in result["error"]
    # No other fields should exist
    assert "audio_id" not in result


@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_translation_task")
@patch("workers.tasks.process_tts_task")
def test_pipeline_uses_original_text_when_translation_fails(mock_tts, mock_trans, mock_ocr):
    """
    Integration test: Graceful degradation when translation fails
    Tests that pipeline continues with original text (orchestration logic)
    """

    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Original text",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": 0,
        "confidence": 0.9,
        "narration_mode": "ocr",
        "tokens_used": None
    }

    # Translation fails
    mock_trans.return_value = {
        "success": False,
        "error": "Translation model not loaded"
    }

    mock_tts.return_value = {
        "success": True,
        "audio_id": "789",
        "audio_url": "/audio/789",
        "characters_used": 13
    }

    result = process_comic_full_pipeline(
        b"image",
        translate=True,
        target_language="nl"
    )

    # Verify graceful degradation (orchestration logic)
    assert result["success"] is True  # Pipeline should still succeed
    assert result["translation_error"] == "Translation model not loaded"

    # Verify TTS received ORIGINAL text, not translated (orchestration logic)
    mock_tts.assert_called_once()
    call_args = mock_tts.call_args[0]
    assert call_args[0] == "Original text"


@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_translation_task")
@patch("workers.tasks.process_tts_task")
def test_pipeline_result_structure_completeness(mock_tts, mock_trans, mock_ocr):
    """
    Integration test: Verify complete result structure
    Tests that all expected fields are present in result
    """

    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Test",
        "panel_count": 2,
        "bubble_count": 3,
        "text_blocks": 4,
        "confidence": 0.85,
        "narration_mode": "llm",
        "tokens_used": 100
    }

    mock_trans.return_value = {
        "success": True,
        "translated_text": "Getest"
    }

    mock_tts.return_value = {
        "success": True,
        "audio_id": "abc123",
        "audio_url": "/audio/abc123",
        "characters_used": 6
    }

    result = process_comic_full_pipeline(b"image", translate=True)

    # Verify all orchestrated fields are present (orchestration logic)
    required_fields = [
        "success", "extracted_text", "panel_count", "bubble_count",
        "text_blocks", "confidence", "narration_mode", "audio_id",
        "audio_url", "characters_used", "translation_enabled",
        "target_language", "translated_text"
    ]

    for field in required_fields:
        assert field in result, f"Missing field: {field}"

    # Verify values were properly combined
    assert result["panel_count"] == 2
    assert result["bubble_count"] == 3
    assert result["narration_mode"] == "llm"
    assert result["tokens_used"] == 100
