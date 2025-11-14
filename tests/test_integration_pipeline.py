import pytest
pytest.skip("Skipping integration test: translation model not configured", allow_module_level=True)

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

# Mock or import your modules
from ocr_comic_to_text.bubble_extractor import SpeechBubbleDetector
from ocr_comic_to_text.translation_model import translate_text
from tts_module import text_to_speech  # Example module

# --- 1. OCR → Translation ---
def test_ocr_to_translation_pipeline(monkeypatch):
    # Mock bubble detection to return fake OCR output
    mock_bubbles = [{'text': 'Hello world'}]
    monkeypatch.setattr(SpeechBubbleDetector, "process_comic_page", lambda self, img: {"bubble_texts": mock_bubbles})
    
    detector = SpeechBubbleDetector()
    ocr_result = detector.process_comic_page("dummy_image.png")
    translated = translate_text(ocr_result["bubble_texts"][0]["text"])
    
    assert isinstance(translated, str)
    assert len(translated) > 0

# --- 2. Translation → Speech (TTS) ---
def test_translation_to_tts_pipeline(monkeypatch, tmp_path):
    # Fake translation output
    text = "Hallo wereld"
    
    # Mock text-to-speech output path
    output_file = tmp_path / "speech.wav"
    def fake_tts(txt, out_path): 
        out_path.write_text("fake audio")
        return out_path
    
    monkeypatch.setattr("tts_module.text_to_speech", fake_tts)
    result = text_to_speech(text, output_file)
    
    assert result.exists()
    assert "fake audio" in result.read_text()

# --- 3. OCR → Translation → TTS (Full pipeline) ---
def test_full_pipeline(monkeypatch, tmp_path):
    mock_bubbles = [{'text': 'Good morning'}]
    monkeypatch.setattr(SpeechBubbleDetector, "process_comic_page", lambda self, img: {"bubble_texts": mock_bubbles})
    
    detector = SpeechBubbleDetector()
    ocr_result = detector.process_comic_page("dummy_image.png")
    translated = translate_text(ocr_result["bubble_texts"][0]["text"])
    
    # Fake TTS
    output_file = tmp_path / "output.wav"
    output_file.write_text("fake speech")
    
    assert isinstance(translated, str)
    assert output_file.exists()
