import pytest
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from interface_server import validate_image_upload

def test_no_file_uploaded():
    """Test that validation fails when no file is provided"""
    ok, error = validate_image_upload(None)
    assert ok is False
    assert "no file" in error.lower()

def test_wrong_file_type():
    """Test that validation fails for non-image file types"""
    class FakeFile:
        filename = "test.txt"

    ok, error = validate_image_upload(FakeFile())
    assert ok is False
    assert "unsupported" in error.lower() or "type" in error.lower()


def test_file_too_large():
    """
    EDGE CASE: Test file size limit validation
    This tests the actual business logic in validate_image_upload (line 72-77)
    """
    class FakeFile:
        filename = "huge_comic.jpg"

        def seek(self, position, whence=0):
            pass

        def tell(self):
            # Return size larger than 10MB limit
            return 11 * 1024 * 1024

    ok, error = validate_image_upload(FakeFile())
    assert ok is False
    assert "large" in error.lower() or "size" in error.lower()


def test_valid_image_file():
    """Test that validation passes for valid image files"""
    class FakeFile:
        filename = "comic.png"

        def seek(self, position, whence=0):
            pass

        def tell(self):
            # Return size within 10MB limit
            return 5 * 1024 * 1024

    ok, error = validate_image_upload(FakeFile())
    assert ok is True
    assert error is None


def test_various_image_extensions():
    """Test that all supported image extensions are accepted"""
    supported_extensions = ["comic.jpg", "comic.jpeg", "comic.png", "comic.gif", "comic.webp"]

    for filename in supported_extensions:
        class FakeFile:
            def __init__(self, name):
                self.filename = name

            def seek(self, position, whence=0):
                pass

            def tell(self):
                return 1024  # 1KB file

        ok, error = validate_image_upload(FakeFile(filename))
        assert ok is True, f"Extension {filename} should be valid"
