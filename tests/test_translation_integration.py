"""
Integration test for translation module

This test verifies that the translation functions exist and are importable.
It does NOT test actual translation (which requires the OpenNMT model),
but ensures the interface is correct.
"""
from translation.translator import translate_text, is_translation_available

def test_translation_functions_exist():
    """
    Basic smoke test: Verify translation functions are importable
    This is an integration test ensuring the translation module API exists
    """
    # Verify functions are callable
    assert callable(translate_text)
    assert callable(is_translation_available)


def test_translation_availability_check():
    """
    Test that is_translation_available returns a boolean
    """
    result = is_translation_available()
    assert isinstance(result, bool)
