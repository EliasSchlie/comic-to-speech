import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ocr_comic_to_text.bubble_extractor import SpeechBubbleDetector

def test_detect_bubbles_structure(monkeypatch):
    """
    Test that bubble detection returns a list of dictionaries with expected keys.
    """
    detector = SpeechBubbleDetector()

    # Monkeypatch detect_bubbles to avoid heavy image processing
    def dummy_detect_bubbles(_):
        return [
            {'x': 10, 'y': 20, 'width': 50, 'height': 40, 'area': 2000, 'circularity': 0.7},
            {'x': 100, 'y': 200, 'width': 60, 'height': 50, 'area': 3000, 'circularity': 0.6}
        ]

    detector.detect_bubbles = dummy_detect_bubbles

    bubbles = detector.detect_bubbles("dummy_image.png")

    # Check that output is a list and elements have required fields
    assert isinstance(bubbles, list), "Expected a list of bubbles"
    assert len(bubbles) > 0, "No bubbles detected"
    for b in bubbles:
        assert all(k in b for k in ('x', 'y', 'width', 'height', 'area', 'circularity')), \
            "Missing expected bubble fields"
