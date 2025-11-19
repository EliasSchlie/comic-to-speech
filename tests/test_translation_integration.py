"""
Integration test for translation module

Tests the translation module's pytest-friendly dummy backend.
These tests verify the translation interface works correctly during testing,
ensuring integration with the rest of the pipeline functions properly.
"""
from translation.translator import translate_text, is_translation_available


def test_translation_single_text():
    """
    Test translation with single text input
    Verifies the dummy backend returns expected format: [dummy-{text}]
    """
    result = translate_text("Hello world")
    assert isinstance(result, str)
    assert result == "[dummy-Hello world]"


def test_translation_list_input():
    """
    Test translation with list of texts
    Verifies batch translation returns list with correct length
    """
    texts = ["Hello", "Goodbye", "Thank you"]
    result = translate_text(texts)
    
    assert isinstance(result, list)
    assert len(result) == len(texts)
    assert result == ["[dummy-Hello]", "[dummy-Goodbye]", "[dummy-Thank you]"]


def test_translation_empty_string():
    """
    Test translation handles empty string gracefully
    """
    result = translate_text("")
    assert isinstance(result, str)
    # Empty string should return predictable dummy format
    assert result == "[dummy-]"


def test_translation_with_language_codes():
    """
    Test translation accepts language code parameters
    Verifies the function signature supports src_lang and tgt_lang
    """
    result = translate_text("Hello", src_lang="en", tgt_lang="nl")
    assert isinstance(result, str)
    assert result == "[dummy-Hello]"


def test_translation_availability_returns_true_in_tests():
    """
    Test that is_translation_available returns True during pytest
    The dummy backend should always report as available
    """
    result = is_translation_available()
    assert result is True


def test_translation_preserves_special_characters():
    """
    Test translation handles special characters in text
    """
    text_with_special = "Hello! How are you? I'm fine."
    result = translate_text(text_with_special)
    
    assert isinstance(result, str)
    assert result == f"[dummy-{text_with_special}]"


def test_translation_multiline_text():
    """
    Test translation handles multiline text
    """
    multiline = "First line\nSecond line\nThird line"
    result = translate_text(multiline)
    
    assert isinstance(result, str)
    assert result == f"[dummy-{multiline}]"


def test_translation_integration_with_pipeline_format():
    """
    Integration test: Verify translation output is compatible with TTS pipeline
    Tests that translated text can be passed directly to TTS without errors
    """
    # Simulate OCR output
    ocr_text = "Panel 1: A hero appears.\nPanel 2: The villain strikes."
    
    # Translate
    translated = translate_text(ocr_text, src_lang="en", tgt_lang="nl")
    
    # Verify format is TTS-compatible (non-empty string)
    assert isinstance(translated, str)
    assert len(translated) > 0
    assert translated.startswith("[dummy-")


def test_translation_batch_processing():
    """
    Integration test: Verify batch translation maintains order
    Critical for multi-panel comic processing
    """
    panels = ["Panel 1 text", "Panel 2 text", "Panel 3 text"]
    translated = translate_text(panels)
    
    # Order must be preserved for correct comic panel sequence
    assert len(translated) == 3
    assert translated[0] == "[dummy-Panel 1 text]"
    assert translated[1] == "[dummy-Panel 2 text]"
    assert translated[2] == "[dummy-Panel 3 text]"
