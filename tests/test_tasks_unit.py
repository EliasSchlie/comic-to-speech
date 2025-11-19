import pytest
from unittest.mock import patch, MagicMock
from workers.tasks import (
    process_ocr_task,
    process_translation_task,
    process_tts_task,
)

# ---------------------------
# OCR TASK TESTS
# ---------------------------

@patch("workers.tasks.ComicOCR")
def test_ocr_task_success(mock_ocr):
    instance = mock_ocr.return_value
    instance.extract_text.return_value = {
        "text": "Hello",
        "panel_count": 1,
        "bubble_count": 1,
        "text_blocks": [],
        "confidence": 0.95,
        "narration_mode": "ocr"
    }

    result = process_ocr_task(b"fakeimage")

    assert result["success"] is True
    assert result["extracted_text"] == "Hello"


@patch("workers.tasks.ComicOCR")
def test_ocr_task_failure(mock_ocr):
    instance = mock_ocr.return_value
    instance.extract_text.side_effect = Exception("OCR boom")

    result = process_ocr_task(b"fake")

    assert result["success"] is False
    assert "OCR error" in result["error"]


# ---------------------------
# TRANSLATION TESTS
# ---------------------------

@patch("workers.tasks.is_translation_available", return_value=True)
@patch("workers.tasks.translate_text")
def test_translation_task_success(mock_trans, _):
    mock_trans.return_value = "Hallo wereld"

    result = process_translation_task("Hello world", src_lang="en", tgt_lang="nl")

    assert result["success"] is True
    assert result["translated_text"] == "Hallo wereld"


@patch("workers.tasks.is_translation_available", return_value=False)
def test_translation_task_unavailable(_):
    result = process_translation_task("Hello")

    assert result["success"] is False
    assert "not available" in result["error"].lower()


# ---------------------------
# TTS TESTS
# ---------------------------

@patch("workers.tasks.get_tts_client")
def test_tts_success(mock_tts):
    client = MagicMock()
    mock_tts.return_value = client

    client.synthesize_speech.return_value = MagicMock(audio_content=b"AUDIO")

    result = process_tts_task("Hello")

    assert result["success"] is True
    assert "audio_id" in result
    assert "audio_url" in result
    assert result["characters_used"] == len("Hello")


@patch("workers.tasks.get_tts_client")
def test_tts_failure(mock_tts):
    client = MagicMock()
    mock_tts.return_value = client

    client.synthesize_speech.side_effect = Exception("TTS failed")

    result = process_tts_task("Hello")

    assert result["success"] is False
    assert "TTS error" in result["error"]
