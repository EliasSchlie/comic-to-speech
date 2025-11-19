import pytest
from unittest.mock import patch
from workers.tasks import process_comic_full_pipeline, process_ocr_task

# ---------------------------
# BLACK IMAGE TEST
# ---------------------------

@patch("workers.tasks.process_ocr_task")
def test_black_image(mock_ocr):
    mock_ocr.return_value = {
        "success": True,
        "extracted_text": "",
        "panel_count": 0,
        "bubble_count": 0,
        "text_blocks": [],
        "confidence": 0.0
    }

    result = process_comic_full_pipeline(b"black")

    assert result["success"] is False
    assert "no text" in result["error"].lower()


# ---------------------------
# MULTIPLE USERS TEST (Concurrency simulation)
# ---------------------------

@patch("workers.tasks.process_ocr_task", return_value={"success": True, "extracted_text": "Hi", "panel_count":1, "bubble_count":1, "text_blocks":[], "confidence":0.99})
@patch("workers.tasks.process_tts_task", return_value={"success": True, "audio_id":"x", "audio_url":"/x", "characters_used":2})
def test_multiple_users_parallel(_, __):
    import concurrent.futures

    def job():
        return process_comic_full_pipeline(b"img")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda _: job(), range(5)))

    for r in results:
        assert r["success"] is True


# ---------------------------
# TRANSLATION DOWN
# ---------------------------

@patch("workers.tasks.process_ocr_task", return_value={"success": True, "extracted_text": "Hello", "panel_count":1,"bubble_count":1,"text_blocks":[], "confidence":0.9})
@patch("workers.tasks.process_translation_task", return_value={"success": False, "error": "Translation unavailable"})
def test_translation_unavailable(_, __):
    result = process_comic_full_pipeline(b"img", translate=True)

    assert result["translation_error"] is not None


# ---------------------------
# TTS QUOTA FAILS
# ---------------------------

@patch("workers.tasks.process_ocr_task", return_value={"success": True, "extracted_text": "Text", "panel_count":1,"bubble_count":1,"text_blocks":[], "confidence":0.9})
@patch("workers.tasks.process_translation_task", return_value={"success": True, "translated_text": "Text"})
@patch("workers.tasks.process_tts_task", return_value={"success": False, "error": "Quota exceeded"})
def test_tts_quota(_, __, ___):
    result = process_comic_full_pipeline(b"img", translate=True)

    assert result["success"] is False
    assert "quota" in result["error"].lower()
