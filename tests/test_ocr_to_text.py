import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import os
from ocr_comic_to_text.comic_ocr_advanced import ComicOCR

def test_ocr_extract_text_from_comic(monkeypatch):
    """
    Test that ComicOCR can process an image and return text (mocked for simplicity).
    """

    # --- Step 1: Setup ---
    sample_path = "comics/sample_page.png"  # Any small test image

    # Skip if no test image exists
    if not os.path.exists(sample_path):
        return

    ocr = ComicOCR()

    # --- Step 2: Monkeypatch (mock) the Google Vision client ---
    class DummyClient:
        def text_detection(self, image):
            class DummyResponse:
                error = type("obj", (), {"message": ""})
                text_annotations = [
                    type("obj", (), {"description": "Hello", "bounding_poly": type("obj", (), {"vertices": []})}),
                    type("obj", (), {"description": "World", "bounding_poly": type("obj", (), {"vertices": []})}),
                ]
            return DummyResponse()

    ocr.client = DummyClient()

    # --- Step 3: Run the OCR process ---
    result = ocr.extract_text_from_comic(sample_path)

    # --- Step 4: Verify Output ---
    assert isinstance(result, str), "OCR output is not a string."
    assert "Hello" in result or "World" in result, "Expected words not found in OCR result."
