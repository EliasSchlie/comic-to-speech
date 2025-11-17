import pytest
from io import BytesIO
from interface_server import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_no_file_uploaded(client):
    res = client.post("/api/process-comic", data={})
    assert res.status_code == 400
    assert "No image file provided" in res.get_json()["error"]


def test_wrong_file_type(client):
    res = client.post("/api/process-comic",
                      data={"image": (BytesIO(b"hello"), "not_image.txt")},
                      content_type="multipart/form-data")
    assert res.status_code in (400, 415)
