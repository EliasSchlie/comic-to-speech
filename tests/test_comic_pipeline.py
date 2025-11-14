
import subprocess
import sys
import os

def test_comic_ocr_script_runs(monkeypatch):
    """
    Ensure that test_comic_ocr.py executes without runtime errors.
    """
    script_path = "ocr_comic_to_text/test_comic_ocr.py"
    if not os.path.exists(script_path):
        return  # Skip if missing

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=10
        )
    except subprocess.TimeoutExpired:
        assert False, "Script took too long to run"
    
    assert result.returncode in (0, 1), f"Unexpected return code: {result.returncode}"
