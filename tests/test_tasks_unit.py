import pytest
from unittest.mock import patch, MagicMock
from tasks import process_ocr_task, process_translation_task, process_tts_task


# -------- OCR UNIT TEST --------
@patch("tasks.ComicOCR")
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
    assert result["panel_count"] == 1


@patch("tasks.ComicOCR")
def test_ocr_task_failure(mock_ocr):
    instance = mock_ocr.return_value
    instance.extract_text.side_effect = Exception("OCR failed")

    result = process_ocr_task(b"fakeimage")

    assert result["success"] is False
    assert "OCR failed" in result["error"]


# -------- TRANSLATION UNIT TEST --------
@patch("tasks.is_translation_available", return_value=True)
@patch("tasks.translate_text", return_value="Hallo wereld")
def test_translation_task_success(mock_trans, mock_avail):
    result = process_translation_task("Hello world")

    assert result["success"] is True
    assert result["translated_text"] == "Hallo wereld"


@patch("tasks.is_translation_available", return_value=False)
def test_translation_task_unavailable(_):
    result = process_translation_task("test")

    assert result["success"] is False
    assert "not available" in result["error"]


# -------- TTS UNIT TEST --------
@patch("tasks.get_tts_client")
def test_tts_success(mock_tts):
    mock_client = MagicMock()
    mock_tts.return_value = mock_client

    mock_client.synthesize_speech.return_value = MagicMock(audio_content=b"FAKEAUDIO")

    result = process_tts_task("Hello world")

    assert result["success"] is True
    assert "audio_id" in result


@patch("tasks.get_tts_client")
def test_tts_failure(mock_tts):
    mock_tts.side_effect = Exception("TTS unavailable")

    result = process_tts_task("Hello world")

    assert result["success"] is False
    assert "TTS" in result["error"]
