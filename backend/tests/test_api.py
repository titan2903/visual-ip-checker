import io
import sys
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient

# Bootstrap sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.main import app
from backend.app.config import DISCLAIMER_TEXT, MAX_UPLOAD_SIZE_BYTES


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_test_image_bytes(format="JPEG", size=(100, 100), color=(200, 100, 50)) -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "docs_url" in data


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_name" in data


def test_static_reference_image(client: TestClient):
    from backend.app.services.search_service import SearchService
    search_service = SearchService.get_instance()
    filename = "batik_parang_01.jpg"
    if search_service.metadata and len(search_service.metadata) > 0:
        filename = search_service.metadata[0].get("filename", filename)

    response = client.get(f"/static/reference_images/{filename}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")


def test_check_with_category_filter(client: TestClient):
    img_bytes = create_test_image_bytes(format="JPEG", color=(120, 65, 30))
    files = {"file": ("query_filter_test.jpg", img_bytes, "image/jpeg")}
    data = {"category": "batik"}
    response = client.post("/check", files=files, data=data)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert len(res_data["results"]) > 0


def test_check_valid_image(client: TestClient):
    img_bytes = create_test_image_bytes(format="JPEG", color=(120, 65, 30))
    files = {"file": ("query_test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/check", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "query" in data
    assert data["query"]["filename"] == "query_test.jpg"
    assert 0.0 <= data["max_similarity_score"] <= 100.0
    assert data["risk_level"] in ["Cukup Orisinal", "Perlu Ditinjau", "Sangat Mirip"]
    assert data["disclaimer"] == DISCLAIMER_TEXT
    assert len(data["results"]) > 0
    assert len(data["results"]) <= 5

    # Verifikasi elemen hasil top-1
    top1 = data["results"][0]
    assert top1["rank"] == 1
    assert "similarity_score" in top1
    assert 0.0 <= top1["similarity_score"] <= 100.0
    assert top1["image_url"].startswith("/static/reference_images/")
    assert top1["risk_level"] in ["Cukup Orisinal", "Perlu Ditinjau", "Sangat Mirip"]


def test_check_invalid_extension(client: TestClient):
    files = {"file": ("test.pdf", b"%PDF-1.4 dummy content", "application/pdf")}
    response = client.post("/check", files=files)
    assert response.status_code == 400
    assert "tidak didukung" in response.json()["detail"].lower()


def test_check_corrupted_image(client: TestClient):
    files = {"file": ("corrupted.jpg", b"not a real jpeg binary data", "image/jpeg")}
    response = client.post("/check", files=files)
    assert response.status_code == 400
    assert "bukan format gambar" in response.json()["detail"].lower()


def test_check_file_too_large(client: TestClient):
    # Buat dummy bytes melebihi 5MB
    large_bytes = b"0" * (MAX_UPLOAD_SIZE_BYTES + 1024)
    files = {"file": ("large.jpg", large_bytes, "image/jpeg")}
    response = client.post("/check", files=files)
    assert response.status_code == 413
    assert "melebihi batas maksimal" in response.json()["detail"].lower()
