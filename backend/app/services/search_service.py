import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import faiss

from backend.app.config import (
    FAISS_INDEX_PATH,
    METADATA_PATH,
    DEFAULT_TOP_K,
    RISK_THRESHOLD_LOW,
    RISK_THRESHOLD_HIGH,
)

logger = logging.getLogger("tarum.search")


class SearchService:
    _instance = None

    @classmethod
    def get_instance(cls) -> "SearchService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        index_path: Path = FAISS_INDEX_PATH,
        metadata_path: Path = METADATA_PATH,
    ):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self.reload()

    def reload(self) -> bool:
        """
        Reloads FAISS index and metadata from disk.
        """
        self.index = None
        self.metadata = []

        if not self.index_path.exists():
            logger.warning(f"Index file not found at {self.index_path}")
            return False

        if not self.metadata_path.exists():
            logger.warning(f"Metadata file not found at {self.metadata_path}")
            return False

        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            logger.info(
                f"FAISS index loaded: {self.index.ntotal} vectors, {len(self.metadata)} metadata records"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load index or metadata: {e}")
            return False

    def is_ready(self) -> bool:
        return self.index is not None and self.index.ntotal > 0 and len(self.metadata) > 0

    def get_total_indexed(self) -> int:
        return self.index.ntotal if self.index is not None else 0

    @staticmethod
    def classify_risk(score: float) -> str:
        """
        Classifies risk level based on PRD Section 5 & 8 thresholds.
        """
        if score >= RISK_THRESHOLD_HIGH:
            return "Sangat Mirip"
        elif score >= RISK_THRESHOLD_LOW:
            return "Perlu Ditinjau"
        else:
            return "Cukup Orisinal"

    @staticmethod
    def get_recommendation(risk_level: str) -> str:
        """
        Generates contextual recommendation according to PRD User Flow (Section 5).
        """
        if risk_level == "Sangat Mirip":
            return (
                "Desain memiliki kemiripan visual tinggi dengan karya referensi. "
                "Sangat disarankan untuk merevisi motif atau elemen spesifik dan "
                "berkonsultasi mengenai HKI sebelum produksi massal."
            )
        elif risk_level == "Perlu Ditinjau":
            return (
                "Desain memiliki kemiripan menengah pada beberapa elemen visual. "
                "Disarankan untuk meninjau dan memodifikasi elemen motif yang serupa."
            )
        else:
            return (
                "Desain memiliki tingkat kemiripan rendah dengan database referensi saat ini. "
                "Anda dapat mempertimbangkan untuk lanjut ke pendaftaran HKI resmi."
            )

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = DEFAULT_TOP_K,
        category: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], float, str, str]:
        """
        Performs vector similarity search against the FAISS index.

        Args:
            query_vector: numpy array of shape (1, 512), L2-normalized.
            top_k: Number of nearest neighbors to retrieve.
            category: Optional category filter (e.g. 'batik', 'tenun', or specific motif)

        Returns:
            Tuple of:
            - results: List of top matching items
            - max_similarity_score: highest score in percentage (0-100)
            - overall_risk_level: "Cukup Orisinal" | "Perlu Ditinjau" | "Sangat Mirip"
            - recommendation: Guidance string
        """
        if not self.is_ready():
            raise RuntimeError(
                "Indeks FAISS belum tersedia atau kosong. "
                "Silakan jalankan script build_index.py terlebih dahulu."
            )

        # Retrieve a broader candidate pool if category filter is active
        has_filter = bool(category and category.strip() and category.strip().lower() != "semua")
        k_search = min(self.index.ntotal, max(top_k * 10, 50)) if has_filter else min(top_k, self.index.ntotal)

        distances, indices = self.index.search(query_vector.astype(np.float32), k_search)

        raw_distances = distances[0]
        match_indices = indices[0]

        all_candidates = []
        is_ip_metric = (
            self.index.metric_type == faiss.METRIC_INNER_PRODUCT
            if hasattr(self.index, "metric_type")
            else False
        )

        for dist, idx in zip(raw_distances, match_indices):
            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            # Convert distance/inner product to 0-100% similarity score
            if is_ip_metric:
                # For normalized vectors, Inner Product = Cosine Similarity in [-1, 1]
                cosine_sim = float(dist)
            else:
                # For L2 distance with unit vectors: d^2 = 2 - 2*cos(theta) => cos(theta) = 1 - d^2/2
                d_sq = float(dist)
                cosine_sim = 1.0 - (d_sq / 2.0)

            # Clamp cosine similarity to [0.0, 1.0] and convert to percentage
            percentage_score = max(0.0, min(100.0, cosine_sim * 100.0))
            score_rounded = round(percentage_score, 2)
            item_risk = self.classify_risk(score_rounded)

            filename = meta.get("filename", f"item_{idx}.jpg")
            all_candidates.append(
                {
                    "id": int(idx),
                    "filename": filename,
                    "image_url": f"/static/reference_images/{filename}",
                    "title": meta.get("title", filename),
                    "category": meta.get("category", "kriya"),
                    "similarity_score": score_rounded,
                    "risk_level": item_risk,
                    "metadata": meta.get("metadata", {}),
                }
            )

        # Apply category filter if requested
        if has_filter:
            cat_lower = category.strip().lower()
            filtered_candidates = [
                c for c in all_candidates
                if cat_lower in c["category"].lower()
                or cat_lower in c.get("metadata", {}).get("motif", "").lower()
                or cat_lower in c.get("title", "").lower()
            ]
            selected_items = filtered_candidates if filtered_candidates else all_candidates
        else:
            selected_items = all_candidates

        # Slice to top_k and re-assign rank numbers
        results = []
        for rank, item in enumerate(selected_items[:top_k], start=1):
            item_with_rank = dict(item)
            item_with_rank["rank"] = rank
            results.append(item_with_rank)

        max_score = results[0]["similarity_score"] if results else 0.0
        overall_risk = self.classify_risk(max_score)
        recommendation = self.get_recommendation(overall_risk)

        return results, max_score, overall_risk, recommendation
