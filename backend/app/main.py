import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import REFERENCE_IMAGES_DIR, MODEL_NAME, CORS_ORIGINS
from backend.app.api.routes import router as api_router
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.search_service import SearchService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tarum.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for warm-up and resource management.
    Pre-loads CLIP embedding model and checks FAISS index status on startup.
    """
    logger.info("Initializing Tarum Backend services...")
    try:
        # Pre-warm embedding model
        embedding_service = EmbeddingService.get_instance()
        logger.info(f"Embedding model '{MODEL_NAME}' is ready.")
    except Exception as e:
        logger.error(f"Failed to initialize embedding service during startup: {e}")

    try:
        # Check FAISS index
        search_service = SearchService.get_instance()
        if search_service.is_ready():
            logger.info(
                f"FAISS index loaded successfully with {search_service.get_total_indexed()} items."
            )
        else:
            logger.warning(
                "FAISS index is not yet built or empty. Run 'python backend/scripts/build_index.py' to index reference images."
            )
    except Exception as e:
        logger.error(f"Failed to check search service during startup: {e}")

    yield

    logger.info("Tarum Backend services shutting down.")


app = FastAPI(
    title="Tarum — Visual IP Checker API",
    description=(
        "API screening awal kemiripan visual desain kriya & fashion "
        "menggunakan Sentence-Transformers (CLIP ViT-B/32) dan FAISS Vector Search."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Configuration (configurable via TARUM_CORS_ORIGINS in .env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for reference image thumbnails
REFERENCE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    "/static/reference_images",
    StaticFiles(directory=str(REFERENCE_IMAGES_DIR)),
    name="reference_images",
)

# Include API routes
app.include_router(api_router)


@app.get("/", tags=["System"])
def root():
    return {
        "app": "Tarum Visual IP Checker API",
        "version": "0.1.0",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health",
        "check_url": "/check",
    }
