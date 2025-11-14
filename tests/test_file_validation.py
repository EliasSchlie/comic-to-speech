import os

def is_valid_comic_file(filename):
    """
    Simple helper for validating comic image file extensions.
    Ensures that the file has a valid extension and a non-empty base name.
    """
    valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".pdf")

    # Empty filename → invalid
    if not filename:
        return False

    # Split filename into base name and extension
    base, ext = os.path.splitext(filename)

    # Reject files with no basename (like ".jpg")
    if not base:
        return False

    # Check valid extension (case-insensitive)
    return ext.lower() in valid_exts


# --- TEST CASES ---

def test_valid_comic_file_extensions():
    assert is_valid_comic_file("page1.png")
    assert is_valid_comic_file("comic.pdf")
    assert is_valid_comic_file("panel.webp")

def test_invalid_comic_file_extensions():
    assert not is_valid_comic_file("notes.txt")
    assert not is_valid_comic_file("script.docx")

def test_case_insensitive_extensions():
    assert is_valid_comic_file("PAGE1.JPG"), "Should handle uppercase extensions"

def test_empty_filename():
    assert not is_valid_comic_file(""), "Empty filename should be invalid"

def test_partial_filename():
    assert not is_valid_comic_file(".jpg"), "Filename with no base name should be invalid"
