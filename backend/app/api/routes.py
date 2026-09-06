import io
import time
import logging
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.app.config import (
    MAX_UPLOAD_SIZE_BYTES,
    ALLOWED_MIME_TYPES,
    ALLOWED_EXTENSIONS,
    DEFAULT_TOP_K,
    DISCLAIMER_TEXT,
    MODEL_NAME,
)
from backend.app.schemas.check import CheckResponse, QueryInfo, HealthResponse
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.search_service import SearchService

logger = logging.getLogger("tarum.api")
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Cek status kesehatan API, model CLIP, dan indeks FAISS.
    """
    embedding_service = EmbeddingService.get_instance()
    search_service = SearchService.get_instance()

    return HealthResponse(
        status="healthy",
        model_name=MODEL_NAME,
        model_loaded=embedding_service.is_loaded(),
        index_loaded=search_service.is_ready(),
        total_indexed_images=search_service.get_total_indexed(),
    )


@router.post("/check", response_model=CheckResponse, tags=["Visual IP Check"])
async def check_visual_similarity(
    file: UploadFile = File(..., description="Foto desain/produk kriya atau fashion (JPEG/PNG/WEBP, max 5MB)")
):
    """
    Endpoint utama screening visual kemiripan desain (PRD Section 6 & 7):
    1. Validasi format file (JPEG/PNG/WEBP) dan ukuran maksimal 5MB.
    2. Ekstraksi visual embedding via CLIP ViT-B/32.
    3. Pencarian kemiripan vektor via FAISS (top-5 paling mirip).
    4. Pengembalian skor (0-100%), gambar pembanding, kategori risiko, dan disclaimer resmi.
    """
    start_time = time.perf_counter()

    # 1. Validasi nama file dan ekstensi
    filename = file.filename or "uploaded_image"
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format file '{file_ext}' tidak didukung. Harap upload gambar berformat JPEG, PNG, atau WEBP.",
        )

    # 2. Validasi MIME type jika tersedia
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe konten '{file.content_type}' tidak diizinkan. Gunakan format JPEG atau PNG.",
        )

    # 3. Baca konten dan validasi ukuran file (max 5MB sesuai PRD Must Have)
    try:
        contents = await file.read()
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gagal membaca file gambar yang diunggah.",
        )

    size_bytes = len(contents)
    if size_bytes > MAX_UPLOAD_SIZE_BYTES:
        http_status_413 = getattr(
            status, "HTTP_413_CONTENT_TOO_LARGE", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
        raise HTTPException(
            status_code=http_status_413,
            detail=f"Ukuran file ({size_bytes / (1024 * 1024):.2f} MB) melebihi batas maksimal 5 MB.",
        )

    if size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File gambar kosong.",
        )

    # 4. Validasi keabsahan data gambar via PIL
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Verifikasi integritas gambar
        # Image.verify() menutup file descriptor internal pada beberapa format, jadi re-open untuk decoding
        image = Image.open(io.BytesIO(contents))
    except (UnidentifiedImageError, OSError) as e:
        logger.warning(f"Invalid image content uploaded: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File yang diunggah bukan format gambar yang valid atau rusak.",
        )

    # 5. Siapkan service
    embedding_service = EmbeddingService.get_instance()
    search_service = SearchService.get_instance()

    if not search_service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Indeks referensi belum siap atau masih kosong. "
                "Harap jalankan script pembangun indeks (scripts/build_index.py) terlebih dahulu."
            ),
        )

    # 6. Komputasi visual embedding (CLIP ViT-B/32)
    try:
        query_vector = embedding_service.encode_image(image)
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kendala saat mengekstrak fitur visual gambar.",
        )

    # 7. Similarity search (FAISS)
    try:
        results, max_score, risk_level, recommendation = search_service.search(
            query_vector, top_k=DEFAULT_TOP_K
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kendala saat melakukan pencarian kemiripan vektor.",
        )

    # 8. Hitung durasi eksekusi end-to-end
    execution_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return CheckResponse(
        status="success",
        query=QueryInfo(
            filename=filename,
            content_type=file.content_type or "image/jpeg",
            size_bytes=size_bytes,
        ),
        max_similarity_score=max_score,
        risk_level=risk_level,
        recommendation=recommendation,
        results=results,
        disclaimer=DISCLAIMER_TEXT,
        execution_time_ms=execution_time_ms,
    )
