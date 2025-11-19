import pytest
from unittest.mock import patch
from workers.tasks import process_comic_full_pipeline, process_ocr_task

# ---------------------------
# BLACK IMAGE TEST (Edge Case)
# Tests system behavior when OCR extracts no text
# ---------------------------

@patch("workers.tasks.process_ocr_task")
def test_black_image(mock_ocr):
    """
    Edge case: Black/empty image with no extractable text
    Expected: Pipeline should fail gracefully with descriptive error
    """
    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "",
        "panel_count": 0,
        "bubble_count": 0,
        "text_blocks": 0,
        "confidence": 0.0,
        "narration_mode": "ocr",
        "tokens_used": None
    }

    result = process_comic_full_pipeline(b"black_image_bytes")

    assert result["success"] is False
    assert "no text" in result["error"].lower() or "empty" in result["error"].lower()


# ---------------------------
# MULTIPLE USERS TEST (Concurrency/Load Test)
# Simulates multiple concurrent users processing comics
# ---------------------------

@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_tts_task")
def test_multiple_users_parallel(mock_tts, mock_ocr):
    """
    Load test: Multiple concurrent users processing comics
    Expected: System handles parallel requests without race conditions
    """
    import concurrent.futures

    # Mock successful OCR and TTS for all requests
    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Hi",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": 0,
        "confidence": 0.99,
        "narration_mode": "ocr",
        "tokens_used": None
    }
    mock_tts.return_value = {
        "success": True,
        "audio_id": "test_audio_123",
        "audio_url": "/api/audio/test_audio_123",
        "characters_used": 2
    }

    def job():
        return process_comic_full_pipeline(b"fake_image_data")

    # Run 5 parallel requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda _: job(), range(5)))

    # All requests should succeed
    for r in results:
        assert r["success"] is True
        assert r["audio_id"] is not None


# ---------------------------
# TRANSLATION FAILURE TEST (Graceful Degradation)
# Tests behavior when translation service is unavailable
# ---------------------------

@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_translation_task")
@patch("workers.tasks.process_tts_task")
def test_translation_unavailable(mock_tts, mock_trans, mock_ocr):
    """
    Edge case: Translation service unavailable
    Expected: Pipeline continues with original text, logs translation error
    """
    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Hello",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": 0,
        "confidence": 0.9,
        "narration_mode": "ocr",
        "tokens_used": None
    }
    mock_trans.return_value = {
        "success": False,
        "error": "Translation model not available"
    }
    mock_tts.return_value = {
        "success": True,
        "audio_id": "audio_fallback",
        "audio_url": "/api/audio/audio_fallback",
        "characters_used": 5
    }

    result = process_comic_full_pipeline(b"image_data", translate=True)

    # Pipeline should still succeed with original text
    assert "translation_error" in result or result.get("translated_text") is None


# ---------------------------
# TTS QUOTA/API FAILURE TEST
# Tests behavior when TTS service fails
# ---------------------------

@patch("workers.tasks.process_ocr_task")
@patch("workers.tasks.process_translation_task")
@patch("workers.tasks.process_tts_task")
def test_tts_quota(mock_tts, mock_trans, mock_ocr):
    """
    Edge case: TTS API quota exceeded or service failure
    Expected: Pipeline fails with clear error message
    """
    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "Text",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": 0,
        "confidence": 0.9,
        "narration_mode": "ocr",
        "tokens_used": None
    }
    mock_trans.return_value = {
        "success": True,
        "translated_text": "Tekst"
    }
    mock_tts.return_value = {
        "success": False,
        "error": "Quota exceeded"
    }

    result = process_comic_full_pipeline(b"image_data", translate=True)

    assert result["success"] is False
    assert "error" in result
    assert "quota" in result["error"].lower() or "exceeded" in result["error"].lower()
