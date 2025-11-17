# tests/test_integration_pipeline.py

import tasks

def test_full_pipeline_no_translation(monkeypatch):
    """
    Integration test:
    process_comic_full_pipeline with OCR mocked,
    translation disabled, and TTS mocked
    """

    # --- Mock OCR result (LLM narration acts as OCR replacement) ---
    def fake_ocr(image_bytes, preprocess=True):
        return {
            "success": True,
            "extracted_text": "Hello from comic",
            "panel_count": 1,
            "bubble_count": 1,
            "text_blocks": 1,
            "confidence": 0.9,
            "narration_mode": "llm",
            "tokens_used": 30,
        }

    # --- Mock TTS result ---
    def fake_tts(text, language_code, voice_name):
        return {
            "success": True,
            "audio_id": "audio-123",
            "audio_url": "/api/audio/audio-123",
            "characters_used": len(text),
        }

    monkeypatch.setattr(tasks, "process_ocr_task", fake_ocr)
    monkeypatch.setattr(tasks, "process_tts_task", fake_tts)

    result = tasks.process_comic_full_pipeline(
        b"fake-image-data",
        language_code="en-US",
        voice_name="en-US-Neural2-F",
        translate=False,
    )

    assert result["success"] is True
    assert result["extracted_text"] == "Hello from comic"
    assert result["audio_id"] == "audio-123"
    assert result["characters_used"] == len("Hello from comic")
    assert "translated_text" not in result
    assert "translation_enabled" not in result


def test_full_pipeline_with_translation(monkeypatch):
    """
    Integration test:
    OCR mocked, translation mocked, TTS mocked
    """

    # --- Mock OCR ---
    def fake_ocr(image_bytes, preprocess=True):
        return {
            "success": True,
            "extracted_text": "Hello from comic",
            "panel_count": 1,
            "bubble_count": 1,
            "text_blocks": 1,
            "confidence": 0.9,
            "narration_mode": "llm",
            "tokens_used": 30,
        }

    # --- Mock Translation ---
    def fake_translation(text, src_lang="en", tgt_lang="nl"):
        return {
            "success": True,
            "translated_text": "Hallo van de strip",
            "original_text": text,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
        }

    # --- Mock TTS ---
    def fake_tts(text, language_code, voice_name):
        # Should receive translated text
        assert text == "Hallo van de strip"
        return {
            "success": True,
            "audio_id": "audio-nl-123",
            "audio_url": "/api/audio/audio-nl-123",
            "characters_used": len(text),
        }

    monkeypatch.setattr(tasks, "process_ocr_task", fake_ocr)
    monkeypatch.setattr(tasks, "process_translation_task", fake_translation)
    monkeypatch.setattr(tasks, "process_tts_task", fake_tts)

    result = tasks.process_comic_full_pipeline(
        b"fake-image-data",
        language_code="nl-NL",
        voice_name="nl-NL-Standard-A",
        translate=True,
        target_language="nl",
    )

    assert result["success"] is True
    assert result["translated_text"] == "Hallo van de strip"
    assert result["audio_id"] == "audio-nl-123"
    assert result["translation_enabled"] is True
    assert result["target_language"] == "nl"
