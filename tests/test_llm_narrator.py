import pytest
from unittest.mock import MagicMock, patch
from llm_narrator import ComicNarrator, get_comic_narrator, _narrator_instance

def make_fake_openai_response(text="Narrated text", tokens=42):
    resp = MagicMock()
    msg = MagicMock()
    msg.content = text
    resp.choices = [MagicMock(message=msg)]
    usage = MagicMock()
    usage.total_tokens = tokens
    resp.usage = usage
    return resp

@patch("llm_narrator.OpenAI")
def test_narrate_panel_success(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value = make_fake_openai_response(
        text="Panel narration"
    )

    narrator = ComicNarrator(api_key="test-key")
    result = narrator.narrate_panel(b"fake-image", panel_number=1, total_panels=3)

    assert result["success"] is True
    assert result["narration"] == "Panel narration"
    assert result["tokens_used"] == 42
    mock_client.chat.completions.create.assert_called_once()

@patch("llm_narrator.OpenAI")
def test_narrate_panel_error(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = RuntimeError("boom")

    narrator = ComicNarrator(api_key="test-key")
    result = narrator.narrate_panel(b"fake-image")

    assert result["success"] is False
    assert result["narration"] == ""
    assert "boom" in result["error"]

def test_narrate_comic_combines_results(monkeypatch):
    narrator = ComicNarrator.__new__(ComicNarrator)  # bypass __init__
    # fake client so nothing is created
    narrator.client = None

    calls = []
    def fake_panel(img, panel_number=None, total_panels=None, max_tokens=500):
        calls.append(panel_number)
        return {
            "narration": f"panel-{panel_number}",
            "success": True,
            "error": None,
            "raw_response": None,
            "tokens_used": 10,
        }

    monkeypatch.setattr(narrator, "narrate_panel", fake_panel)

    result = narrator.narrate_comic([b"a", b"b", b"c"])

    assert result["success"] is True
    assert result["panel_count"] == 3
    assert result["total_tokens"] == 30
    assert result["full_narration"] == "panel-1\n\npanel-2\n\npanel-3"
    assert calls == [1, 2, 3]

@patch("llm_narrator.OpenAI")
def test_narrate_single_image_success(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value = make_fake_openai_response(
        text="Full page narration", tokens=100
    )

    narrator = ComicNarrator(api_key="test-key")
    result = narrator.narrate_single_image(b"fake-image")

    assert result["success"] is True
    assert result["text"] == "Full page narration"
    assert result["narration"] == "Full page narration"
    assert result["tokens_used"] == 100

def test_get_comic_narrator_singleton(monkeypatch):
    # reset global singleton
    from llm_narrator import _narrator_instance as global_inst
    import llm_narrator as ln
    ln._narrator_instance = None

    class FakeNarrator:
        def __init__(self, api_key=None):
            self.api_key = api_key

    monkeypatch.setattr(ln, "ComicNarrator", FakeNarrator)

    inst1 = ln.get_comic_narrator(api_key="k1")
    inst2 = ln.get_comic_narrator(api_key="k2")

    assert isinstance(inst1, FakeNarrator)
    assert inst1 is inst2  # same instance
