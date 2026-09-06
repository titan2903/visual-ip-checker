import argparse
import json
import logging
import sys
import time
from pathlib import Path
from PIL import Image
import numpy as np
import faiss

# Ensure backend package is in python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.config import (
    REFERENCE_IMAGES_DIR,
    INDEX_DIR,
    FAISS_INDEX_PATH,
    METADATA_PATH,
    MODEL_NAME,
    ALLOWED_EXTENSIONS,
)
from backend.app.services.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("tarum.build_index")


def load_raw_metadata(images_dir: Path) -> dict:
    """Load optional raw_metadata.json if present to enrich indexed items."""
    meta_path = images_dir / "raw_metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
                return {item["filename"]: item for item in raw_list if "filename" in item}
        except Exception as e:
            logger.warning(f"Could not read raw_metadata.json: {e}")
    return {}


def build_faiss_index(
    data_dir: Path = REFERENCE_IMAGES_DIR,
    output_dir: Path = INDEX_DIR,
    metric: str = "ip",
    batch_size: int = 32,
):
    """
    Scans data_dir for reference images, extracts visual embeddings with CLIP,
    and builds a FAISS vector index with metadata mapping.
    """
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    faiss_out = output_dir / "index.faiss"
    metadata_out = output_dir / "metadata.json"

    logger.info(f"Scanning images from: {data_dir}")
    image_paths = sorted(
        [
            p
            for p in data_dir.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
        ]
    )

    if not image_paths:
        logger.error(
            f"No valid images found in {data_dir}. "
            "Please add images or run 'python backend/scripts/create_dummy_data.py' first."
        )
        return False

    logger.info(f"Found {len(image_paths)} images to index.")
    raw_meta_lookup = load_raw_metadata(data_dir)

    # 1. Load images into memory
    loaded_images = []
    valid_records = []

    for path in image_paths:
        try:
            with Image.open(path) as img:
                rgb_img = img.convert("RGB")
                loaded_images.append(rgb_img.copy())

            filename = path.name
            raw_item = raw_meta_lookup.get(filename, {})
            title = raw_item.get("title", path.stem.replace("_", " ").title())
            category = raw_item.get("category", "kriya")

            valid_records.append(
                {
                    "id": len(valid_records),
                    "filename": filename,
                    "title": title,
                    "category": category,
                    "metadata": {
                        "path": str(path),
                        "width": loaded_images[-1].width,
                        "height": loaded_images[-1].height,
                        "description": raw_item.get("description", ""),
                        "source": raw_item.get("source", "local_file"),
                    },
                }
            )
        except Exception as e:
            logger.warning(f"Skipping corrupted image {path}: {e}")

    if not loaded_images:
        logger.error("No valid images could be loaded.")
        return False

    # 2. Extract CLIP Embeddings
    logger.info(f"Loading CLIP model: {MODEL_NAME}...")
    embedder = EmbeddingService.get_instance()

    start_t = time.perf_counter()
    logger.info(f"Encoding {len(loaded_images)} images (batch_size={batch_size})...")
    embeddings = embedder.encode_images(
        loaded_images, batch_size=batch_size, show_progress=True
    )
    duration = time.perf_counter() - start_t
    logger.info(
        f"Encoding completed in {duration:.2f}s (avg: {duration / len(loaded_images) * 1000:.1f}ms/image)"
    )

    dim = embeddings.shape[1]
    logger.info(f"Embeddings shape: {embeddings.shape} (dim={dim})")

    # 3. Create FAISS Index
    # With normalized embeddings:
    # - IndexFlatIP gives Inner Product = Cosine Similarity
    # - IndexFlatL2 gives Euclidean distance d^2 = 2 - 2*cos(theta)
    if metric == "ip":
        logger.info("Building FAISS IndexFlatIP (Cosine Similarity)...")
        index = faiss.IndexFlatIP(dim)
    else:
        logger.info("Building FAISS IndexFlatL2 (Euclidean Distance)...")
        index = faiss.IndexFlatL2(dim)

    index.add(embeddings.astype(np.float32))
    logger.info(f"FAISS index built with {index.ntotal} vectors.")

    # 4. Save Index and Metadata
    faiss.write_index(index, str(faiss_out))
    logger.info(f"Index saved to: {faiss_out} ({faiss_out.stat().st_size / 1024:.1f} KB)")

    with open(metadata_out, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)
    logger.info(f"Metadata saved to: {metadata_out}")

    print("\n" + "=" * 50)
    print("✓ INDEKS FAISS BERHASIL DIBUAT")
    print(f"  - Total Gambar Diindeks : {index.ntotal}")
    print(f"  - Dimensi Vektor        : {dim}")
    print(f"  - File Indeks           : {faiss_out}")
    print(f"  - File Metadata         : {metadata_out}")
    print("=" * 50 + "\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bangun indeks FAISS dari dataset referensi kriya/fashion Tarum."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(REFERENCE_IMAGES_DIR),
        help=f"Folder berisi gambar referensi (default: {REFERENCE_IMAGES_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(INDEX_DIR),
        help=f"Folder output untuk index.faiss & metadata.json (default: {INDEX_DIR})",
    )
    parser.add_argument(
        "--metric",
        choices=["ip", "l2"],
        default="ip",
        help="Metrik pencarian FAISS: 'ip' (Cosine Similarity) atau 'l2' (L2 distance)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size untuk inferensi embedding CLIP (default: 32)",
    )

    args = parser.parse_args()
    build_faiss_index(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        metric=args.metric,
        batch_size=args.batch_size,
    )
