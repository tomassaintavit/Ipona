from fastapi.testclient import TestClient

from app.main import app


def test_sirve_index_html():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "ipOna" in response.text
    assert "text/html" in response.headers["content-type"]


def test_sirve_manifest_pwa():
    with TestClient(app) as client:
        manifest = client.get("/manifest.webmanifest")
        sw = client.get("/sw.js")

    assert manifest.status_code == 200
    assert '"name": "ipOna"' in manifest.text
    assert sw.status_code == 200
