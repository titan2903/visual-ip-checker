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
    import os
    from backend.app.config import REFERENCE_IMAGES_DIR

    # Cari file referensi yang benar-benar ada di disk runner CI
    filename = "batik_parang_01.jpg"
    filepath = REFERENCE_IMAGES_DIR / filename

    if not filepath.exists():
        existing_images = [
            f for f in os.listdir(REFERENCE_IMAGES_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]
        if existing_images:
            filename = existing_images[0]
        else:
            # Fallback aman jika direktori kosong pada runner CI/CD
            from PIL import Image
            fallback_img = Image.new("RGB", (64, 64), color=(100, 150, 200))
            fallback_img.save(REFERENCE_IMAGES_DIR / "sample_test.jpg", format="JPEG")
            filename = "sample_test.jpg"

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


def test_check_accuracy_on_reference_image(client: TestClient):
    """
    Verifikasi akurasi ONNX Runtime INT8: gambar motif referensi yang ada di dataset
    harus menghasilkan kemiripan tinggi (>90%) dan status 'Sangat Mirip',
    bukan skor di bawah 10%.
    """
    from backend.app.config import REFERENCE_IMAGES_DIR
    test_img_path = REFERENCE_IMAGES_DIR / "hf_batik_0002_aceh.jpg"
    if not test_img_path.exists():
        # Cari gambar apa saja yang berawalan hf_batik_
        images = list(REFERENCE_IMAGES_DIR.glob("hf_batik_*.jpg"))
        if not images:
            pytest.skip("No reference batik images found to verify accuracy")
        test_img_path = images[0]

    with open(test_img_path, "rb") as f:
        img_bytes = f.read()

    files = {"file": (test_img_path.name, img_bytes, "image/jpeg")}
    response = client.post("/check", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Memastikan skor kemiripan > 90% (menguji akurasi tinggi ONNX INT8)
    assert data["max_similarity_score"] >= 90.0, f"Expected >= 90%, got {data['max_similarity_score']}%"
    assert data["risk_level"] == "Sangat Mirip"



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
