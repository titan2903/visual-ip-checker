import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image
import numpy as np
import onnxruntime as ort

from backend.app.config import MODEL_NAME, ONNX_MODEL_PATH

logger = logging.getLogger("tarum.embedding")

# Standard CLIP normalization constants (ImageNet mean & std used by OpenAI CLIP)
CLIP_MEAN = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
CLIP_STD = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)


class EmbeddingService:
    """
    Service to extract 512-dimensional visual embeddings using an offline-quantized
    ONNX INT8 model of CLIP ViT-B/32.

    Runs entirely locally using ONNX Runtime (C++ engine) with pure NumPy/Pillow
    preprocessing. Requires NO PyTorch or GPU, running comfortably under 200MB RAM.
    """
    _instance: Optional["EmbeddingService"] = None

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, model_path: Optional[Path] = None):
        self.model_name = MODEL_NAME
        self.model_path = model_path or ONNX_MODEL_PATH
        self.session: Optional[ort.InferenceSession] = None
        self._load_model()

    def _load_model(self):
        """Loads the ONNX Runtime inference session with CPU execution provider."""
        if not self.model_path.exists():
            logger.error(
                f"ONNX model not found at {self.model_path}. "
                "Run 'python backend/scripts/export_onnx.py' to generate the INT8 model."
            )
            return

        try:
            logger.info(f"Loading ONNX INT8 model from {self.model_path}...")
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.inter_op_num_threads = 1
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            logger.info(f"ONNX INT8 model successfully loaded (providers={self.session.get_providers()}).")
        except Exception as e:
            logger.error(f"Failed to load ONNX model from {self.model_path}: {e}")
            self.session = None

    def is_loaded(self) -> bool:
        """Returns True if the ONNX inference session is initialized and ready."""
        return self.session is not None

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess a PIL Image according to standard CLIP ViT-B/32 vision requirements:
        1. Convert mode to RGB
        2. Resize shorter edge to 224 with BICUBIC resampling
        3. Center crop to 224x224
        4. Rescale pixels to [0.0, 1.0]
        5. Normalize with CLIP mean and std
        6. Transpose to CHW shape: (3, 224, 224)
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        w, h = image.size
        scale = 224.0 / min(w, h)
        new_w = max(224, int(round(w * scale)))
        new_h = max(224, int(round(h * scale)))

        resized = image.resize((new_w, new_h), Image.Resampling.BICUBIC)

        left = (new_w - 224) // 2
        top = (new_h - 224) // 2
        cropped = resized.crop((left, top, left + 224, top + 224))

        arr = np.array(cropped, dtype=np.float32) / 255.0
        arr = (arr - CLIP_MEAN) / CLIP_STD
        arr = np.transpose(arr, (2, 0, 1))  # (H, W, C) -> (C, H, W)
        return arr

    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Applies L2 normalization across the embedding vectors (axis=-1)."""
        norms = np.linalg.norm(embeddings, axis=-1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return (embeddings / norms).astype(np.float32)

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Encodes a single PIL Image into a normalized 512-d float32 vector.
        Returns array of shape (1, 512).
        """
        if not self.is_loaded():
            raise RuntimeError(
                f"EmbeddingService ONNX model is not loaded. Expected path: {self.model_path}"
            )

        processed = self._preprocess_image(image)
        input_tensor = np.expand_dims(processed, axis=0)  # Shape (1, 3, 224, 224)

        raw_outputs = self.session.run(["embedding"], {"pixel_values": input_tensor})[0]
        return self._normalize_embeddings(raw_outputs)

    def encode_images(
        self, images: List[Image.Image], batch_size: int = 32, show_progress: bool = True
    ) -> np.ndarray:
        """
        Encodes a list of PIL Images into normalized float32 vectors.
        Processes in batches of size `batch_size`.
        Returns array of shape (N, 512).
        """
        if not self.is_loaded():
            raise RuntimeError(
                f"EmbeddingService ONNX model is not loaded. Expected path: {self.model_path}"
            )

        if not images:
            return np.empty((0, 512), dtype=np.float32)

        all_embeddings = []
        total = len(images)

        for i in range(0, total, batch_size):
            batch_images = images[i : i + batch_size]
            preprocessed_list = [self._preprocess_image(img) for img in batch_images]
            batch_tensor = np.stack(preprocessed_list, axis=0)  # Shape (B, 3, 224, 224)

            outputs = self.session.run(["embedding"], {"pixel_values": batch_tensor})[0]
            normalized = self._normalize_embeddings(outputs)
            all_embeddings.append(normalized)

            if show_progress and total > batch_size:
                logger.info(f"Encoded {min(i + batch_size, total)}/{total} images...")

        return np.concatenate(all_embeddings, axis=0)
