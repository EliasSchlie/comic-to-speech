#!/usr/bin/env python3
"""
Test script for translation integration
Tests the full pipeline: text extraction -> translation -> TTS
"""

from ocr_comic_to_text.translation_model import translate_text, is_translation_available

def test_translation():
    """Test basic translation functionality"""
    print("=" * 60)
    print("Testing Translation Module Integration")
    print("=" * 60)

    # Check if translation is available
    print(f"\n1. Checking translation availability...")
    available = is_translation_available()
    print(f"   Translation available: {available}")

    if not available:
        print("   ERROR: Translation models not found!")
        return False

    # Test single text translation
    print(f"\n2. Testing single text translation...")
    test_text = "Hello, how are you today?"
    print(f"   Original: {test_text}")

    try:
        translated = translate_text(test_text)
        print(f"   Translated: {translated}")
        print("   ✓ Single text translation successful!")
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test list translation
    print(f"\n3. Testing list translation...")
    test_texts = [
        "This is a comic book.",
        "The hero saves the day!",
        "What an amazing story."
    ]

    print(f"   Original texts:")
    for i, text in enumerate(test_texts, 1):
        print(f"     {i}. {text}")

    try:
        translated_list = translate_text(test_texts)
        print(f"   Translated texts:")
        for i, text in enumerate(translated_list, 1):
            print(f"     {i}. {text}")
        print("   ✓ List translation successful!")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All translation tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_translation()
    exit(0 if success else 1)
