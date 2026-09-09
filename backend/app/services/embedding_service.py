import logging
from typing import List, Union
from PIL import Image
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.app.config import MODEL_NAME

logger = logging.getLogger("tarum.embedding")


class EmbeddingService:
    _instance = None
    _model = None

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, model_name: str = MODEL_NAME):
        if EmbeddingService._model is None:
            logger.info(f"Loading CLIP model: {model_name}...")
            # SentenceTransformer clip-ViT-B-32 handles both text and images
            import torch
            model = SentenceTransformer(model_name)
            # Apply dynamic quantization to reduce memory footprint on CPU (Heroku)
            EmbeddingService._model = torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear}, dtype=torch.qint8
            )
            logger.info(f"CLIP model {model_name} loaded successfully.")
        self.model = EmbeddingService._model

    def is_loaded(self) -> bool:
        return self.model is not None

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Ensure image is in RGB format for CLIP model input.
        Handles RGBA, Grayscale (L), CMYK, and palette images.
        """
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Encodes a single PIL Image into a normalized 512-d float32 vector.
        Returns array of shape (1, 512).
        """
        rgb_image = self._preprocess_image(image)
        # normalize_embeddings=True ensures L2 norm is 1.0 (unit vector)
        embedding = self.model.encode(
            [rgb_image],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.astype(np.float32)

    def encode_images(
        self, images: List[Image.Image], batch_size: int = 32, show_progress: bool = True
    ) -> np.ndarray:
        """
        Encodes a batch of PIL Images into normalized float32 vectors.
        Returns array of shape (N, 512).
        """
        rgb_images = [self._preprocess_image(img) for img in images]
        embeddings = self.model.encode(
            rgb_images,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
        )
        return embeddings.astype(np.float32)
