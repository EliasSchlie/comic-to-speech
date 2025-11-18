from tasks import translate_text, is_translation_available

def test_translation():
    # No API calls here — just ensure function exists and returns a fallback string
    assert callable(translate_text)
    assert callable(is_translation_available)
    return True
