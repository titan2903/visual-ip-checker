from pathlib import Path
import os
from dotenv import load_dotenv

# Base Directories
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Load environment variables from backend/.env or root .env
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")

# Data Directories
DATA_DIR = Path(os.getenv("TARUM_DATA_DIR", str(BACKEND_DIR / "data")))
REFERENCE_IMAGES_DIR = DATA_DIR / "reference_images"
INDEX_DIR = DATA_DIR / "index"

FAISS_INDEX_PATH = INDEX_DIR / "index.faiss"
METADATA_PATH = INDEX_DIR / "metadata.json"

# Ensure directories exist
REFERENCE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Pretrained Model
# Default CLIP ViT-B/32 via sentence-transformers as specified in PRD Section 7
MODEL_NAME = os.getenv("TARUM_MODEL_NAME", "clip-ViT-B-32")
EMBEDDING_DIM = 512

# Server Configuration
HOST = os.getenv("TARUM_HOST", "0.0.0.0")
PORT = int(os.getenv("TARUM_PORT", "8000"))

# CORS Configuration
raw_cors = os.getenv(
    "TARUM_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,*",
)
CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

# Upload Constraints (PRD Section 6 Must Have: JPEG/PNG max 5MB)
MAX_UPLOAD_SIZE_MB = float(os.getenv("TARUM_MAX_UPLOAD_SIZE_MB", "5.0"))
MAX_UPLOAD_SIZE_BYTES = int(MAX_UPLOAD_SIZE_MB * 1024 * 1024)
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Search Parameters
DEFAULT_TOP_K = int(os.getenv("TARUM_DEFAULT_TOP_K", "5"))

# Risk Thresholds (%)
# Skor Rendah (<50%): "Cukup Orisinal"
# Skor Menengah (50% - 74.99%): "Perlu Ditinjau"
# Skor Tinggi (>=75%): "Sangat Mirip"
RISK_THRESHOLD_LOW = float(os.getenv("TARUM_RISK_THRESHOLD_LOW", "50.0"))
RISK_THRESHOLD_HIGH = float(os.getenv("TARUM_RISK_THRESHOLD_HIGH", "75.0"))

# Official Legal Disclaimer (PRD Section 6 & 8)
DISCLAIMER_TEXT = (
    "Ini bukan opini hukum. Hasil ini membantu kamu memutuskan "
    "langkah berikutnya, bukan menggantikan konsultasi HKI resmi."
)
