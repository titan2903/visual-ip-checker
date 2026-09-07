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
    HF_DATASET_NAME,
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


def load_images_from_hf(
    dataset_name: str = HF_DATASET_NAME,
    output_images_dir: Path = REFERENCE_IMAGES_DIR,
    limit: int = None,
    split: str = "train",
):
    """
    Loads dataset from Hugging Face (PRD Section 7 & 7.1),
    resizes/saves thumbnails locally for static web serving,
    and prepares image objects & metadata for embedding.
    """
    from datasets import load_dataset

    logger.info(f"Loading Hugging Face dataset '{dataset_name}' (split='{split}')...")
    ds = load_dataset(dataset_name, split=split)
    total_in_split = len(ds)
    logger.info(f"Dataset loaded. Total available samples: {total_in_split}")

    # Resolve class labels
    class_names = []
    if hasattr(ds.features.get("label"), "names"):
        class_names = ds.features["label"].names

    max_samples = min(limit, total_in_split) if limit else total_in_split
    logger.info(f"Processing {max_samples} samples from Hugging Face dataset...")

    output_images_dir.mkdir(parents=True, exist_ok=True)
    loaded_images = []
    valid_records = []

    for idx in range(max_samples):
        try:
            row = ds[idx]
            raw_img = row["image"]
            label_val = row.get("label")

            # Resolve label name
            if isinstance(label_val, int) and label_val < len(class_names):
                label_name = class_names[label_val]
            else:
                label_name = str(label_val or "batik")

            clean_label = label_name.replace("_", " ").title()
            slug = label_name.lower().replace(" ", "_")

            # Convert to RGB PIL Image
            rgb_img = raw_img.convert("RGB")
            
            # Save web-friendly thumbnail for static file serving
            filename = f"hf_batik_{idx:04d}_{slug}.jpg"
            img_file_path = output_images_dir / filename

            # Only save to disk if not already existing
            if not img_file_path.exists():
                thumb_img = rgb_img.copy()
                thumb_img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                thumb_img.save(img_file_path, format="JPEG", quality=85, optimize=True)

            loaded_images.append(rgb_img)
            valid_records.append(
                {
                    "id": idx,
                    "filename": filename,
                    "title": f"Batik {clean_label} #{idx+1}",
                    "category": "batik",
                    "label": label_name,
                    "metadata": {
                        "path": str(img_file_path),
                        "width": rgb_img.width,
                        "height": rgb_img.height,
                        "motif": clean_label,
                        "source": dataset_name,
                        "split": split,
                        "license_notice": "Riset non-komersial / Proof of Concept (PRD Sec 7.1)",
                        "description": (
                            f"Motif batik tradisional {clean_label} dari koleksi dataset Batik Indonesia."
                        ),
                    },
                }
            )

            if (idx + 1) % 100 == 0 or (idx + 1) == max_samples:
                logger.info(f"Prepared {idx + 1}/{max_samples} images...")

        except Exception as e:
            logger.warning(f"Error processing sample index {idx}: {e}")

    return loaded_images, valid_records


def load_images_from_local(
    data_dir: Path = REFERENCE_IMAGES_DIR,
    limit: int = None,
):
    """
    Loads images from local folder (fallback).
    """
    data_dir = Path(data_dir)
    logger.info(f"Scanning local images from: {data_dir}")
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
            "Run with '--source hf' or 'python backend/scripts/create_dummy_data.py' first."
        )
        return [], []

    if limit:
        image_paths = image_paths[:limit]

    logger.info(f"Found {len(image_paths)} local images to index.")
    raw_meta_lookup = load_raw_metadata(data_dir)

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

    return loaded_images, valid_records


def build_faiss_index(
    source: str = "hf",
    dataset_name: str = HF_DATASET_NAME,
    data_dir: Path = REFERENCE_IMAGES_DIR,
    output_dir: Path = INDEX_DIR,
    limit: int = None,
    metric: str = "ip",
    batch_size: int = 32,
):
    """
    Scans reference images (from Hugging Face or local files),
    extracts visual embeddings with CLIP ViT-B/32, and builds a FAISS vector index.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    faiss_out = output_dir / "index.faiss"
    metadata_out = output_dir / "metadata.json"

    # 1. Load Images & Metadata
    if source == "hf":
        loaded_images, valid_records = load_images_from_hf(
            dataset_name=dataset_name,
            output_images_dir=Path(data_dir),
            limit=limit,
        )
    else:
        loaded_images, valid_records = load_images_from_local(
            data_dir=Path(data_dir),
            limit=limit,
        )

    if not loaded_images:
        logger.error("No valid images could be loaded for indexing.")
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
    # - IndexFlatIP gives Inner Product = Cosine Similarity in [-1, 1]
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
    print(f"  - Sumber Data           : {source.upper()} ({dataset_name if source == 'hf' else data_dir})")
    print(f"  - Total Gambar Diindeks : {index.ntotal}")
    print(f"  - Dimensi Vektor        : {dim}")
    print(f"  - File Indeks           : {faiss_out}")
    print(f"  - File Metadata         : {metadata_out}")
    print("=" * 50 + "\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bangun indeks FAISS dari dataset referensi batik/kriya Tarum."
    )
    parser.add_argument(
        "--source",
        choices=["hf", "local"],
        default="hf",
        help="Sumber dataset: 'hf' (Hugging Face) atau 'local' (folder lokal). Default: hf",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default=HF_DATASET_NAME,
        help=f"Nama dataset Hugging Face (default: {HF_DATASET_NAME})",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(REFERENCE_IMAGES_DIR),
        help=f"Folder penyimpan gambar referensi (default: {REFERENCE_IMAGES_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(INDEX_DIR),
        help=f"Folder output untuk index.faiss & metadata.json (default: {INDEX_DIR})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Batas maksimal jumlah gambar yang diindeks (default: semua)",
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
        source=args.source,
        dataset_name=args.dataset_name,
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        limit=args.limit,
        metric=args.metric,
        batch_size=args.batch_size,
    )
