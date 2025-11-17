import pytest
from unittest.mock import MagicMock
import tasks

# ---------- Translation ----------

def test_process_translation_task_no_text():
    result = tasks.process_translation_task("")
    assert result["success"] is False
    assert "No text" in result["error"]

def test_process_translation_task_model_unavailable(monkeypatch):
    monkeypatch.setattr(tasks, "is_translation_available", lambda: False)

    result = tasks.process_translation_task("hello")
    assert result["success"] is False
    assert "not available" in result["error"]

def test_process_translation_task_success(monkeypatch):
    monkeypatch.setattr(tasks, "is_translation_available", lambda: True)
    monkeypatch.setattr(
        tasks,
        "translate_text",
        lambda text, src_lang="en", tgt_lang="nl": "hallo wereld",
    )

    result = tasks.process_translation_task("hello world")
    assert result["success"] is True
    assert result["translated_text"] == "hallo wereld"
    assert result["src_lang"] == "en"
    assert result["tgt_lang"] == "nl"

# ---------- TTS ----------

def test_process_tts_task_no_text(monkeypatch):
    # avoid real GCP client even on failure path
    monkeypatch.setattr(tasks, "get_tts_client", lambda: MagicMock())
    result = tasks.process_tts_task("")
    assert result["success"] is False
    assert "No text" in result["error"]

def test_process_tts_task_success(monkeypatch, tmp_path):
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.audio_content = b"fake-mp3-data"
    fake_client.synthesize_speech.return_value = fake_response

    monkeypatch.setattr(tasks, "get_tts_client", lambda: fake_client)
    # write audio into temp dir instead of real AUDIO_DIR
    monkeypatch.setattr(tasks, "AUDIO_DIR", tmp_path)

    result = tasks.process_tts_task("Hello there", "en-US", "en-US-TestVoice")

    assert result["success"] is True
    assert "audio_id" in result
    audio_path = tmp_path / f"{result['audio_id']}.mp3"
    assert audio_path.exists()
    fake_client.synthesize_speech.assert_called_once()

# ---------- OCR / text extraction wrapper ----------

def test_process_ocr_task_success(monkeypatch):
    class FakeOCR:
        def extract_text(self, image_bytes, preprocess=True):
            return {
                "text": "Hello from comic",
                "panel_count": 1,
                "bubble_count": 2,
                "text_blocks": ["Hello", "world"],
                "confidence": 0.95,
                "narration_mode": "llm",
                "tokens_used": 123,
            }

    monkeypatch.setattr(tasks, "ComicOCR", FakeOCR)

    result = tasks.process_ocr_task(b"fake-image")

    assert result["success"] is True
    assert result["extracted_text"] == "Hello from comic"
    assert result["panel_count"] == 1
    assert result["bubble_count"] == 2
    assert result["text_blocks"] == 2
    assert result["narration_mode"] == "llm"
    assert result["tokens_used"] == 123

def test_process_ocr_task_error(monkeypatch):
    class FakeOCR:
        def __init__(self):
            raise RuntimeError("init fail")

    monkeypatch.setattr(tasks, "ComicOCR", FakeOCR)

    result = tasks.process_ocr_task(b"fake-image")
    assert result["success"] is False
    assert "init fail" in result["error"]
