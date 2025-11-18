import pytest
from interface_server import validate_image_upload

def test_no_file_uploaded():
    ok, error = validate_image_upload(None)
    assert ok is False
    assert "no file" in error.lower()

def test_wrong_file_type():
    class FakeFile:
        filename = "test.txt"

    ok, error = validate_image_upload(FakeFile())
    assert ok is False
    assert "image" in error.lower()
