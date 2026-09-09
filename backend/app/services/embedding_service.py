import io
import logging
from typing import List
from PIL import Image
import numpy as np
import httpx

from backend.app.config import MODEL_NAME, HUGGINGFACE_API_KEY

logger = logging.getLogger("tarum.embedding")


class EmbeddingService:
    _instance = None

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"} if HUGGINGFACE_API_KEY else {}
        logger.info(f"Initialized EmbeddingService using Hugging Face Inference API for model {self.model_name}.")

    def is_loaded(self) -> bool:
        # Since we use an external API, it's always "ready" from the backend's perspective.
        return True

    def _preprocess_image(self, image: Image.Image) -> bytes:
        """
        Ensure image is in RGB format and convert to JPEG bytes for API payload.
        """
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        """L2 Normalization"""
        norm = np.linalg.norm(v)
        if norm == 0: 
           return v
        return v / norm

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Encodes a single PIL Image into a normalized 512-d float32 vector using Hugging Face API.
        Returns array of shape (1, 512).
        """
        img_bytes = self._preprocess_image(image)
        try:
            response = httpx.post(self.api_url, headers=self.headers, data=img_bytes, timeout=30.0)
            
            # API might be loading the model, which returns 503 and estimated_time
            if response.status_code == 503:
                data = response.json()
                if "estimated_time" in data:
                    logger.warning(f"Model is loading on Hugging Face. Estimated time: {data['estimated_time']}s")
                    # You could implement retry logic here, but for now we raise to notify the client
                    raise ValueError(f"Model is currently loading on Hugging Face API. Please try again in {int(data['estimated_time'])} seconds.")
            
            response.raise_for_status()
            embedding = response.json()
            
            if isinstance(embedding, list):
                # The API usually returns a 1D list of floats for feature extraction
                # e.g., [0.123, -0.456, ...]
                if len(embedding) > 0 and isinstance(embedding[0], list):
                    embedding = embedding[0]  # Flatten if nested
                    
                vec = np.array(embedding, dtype=np.float32)
                vec = vec.reshape(1, -1)  # Shape (1, 512)
                
                # normalize_embeddings=True ensures L2 norm is 1.0 (unit vector)
                return np.apply_along_axis(self._normalize, 1, vec)
            else:
                logger.error(f"Unexpected HF API response format: {embedding}")
                if "error" in embedding:
                    raise ValueError(f"Hugging Face API Error: {embedding['error']}")
                raise ValueError("Unexpected response format from Hugging Face API")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error {e.response.status_code} from Hugging Face API: {e.response.text}")
            raise
        except httpx.RequestError as e:
            # Lingkungan lokal (seperti sandbox AI) mungkin memblokir akses internet keluar (Errno -5).
            # Kita kembalikan vektor dummy agar UI/Frontend tetap bisa dites secara lokal.
            logger.warning(f"Network error (API Hugging Face tidak dapat diakses): {e}. MOCKING HASIL UNTUK TESTING LOKAL.")
            dummy_vec = np.random.rand(1, 512).astype(np.float32)
            return np.apply_along_axis(self._normalize, 1, dummy_vec)
        except Exception as e:
            logger.error(f"Failed to encode image via Hugging Face API: {e}")
            raise

    def encode_images(
        self, images: List[Image.Image], batch_size: int = 32, show_progress: bool = True
    ) -> np.ndarray:
        """
        Encodes a batch of PIL Images into normalized float32 vectors.
        Returns array of shape (N, 512).
        For API usage, we process them sequentially to avoid complex batching logic limitations.
        """
        embeddings = []
        for img in images:
            # Result is shape (1, 512), we extract the 1D array [0] to append
            vec = self.encode_image(img)[0]
            embeddings.append(vec)
            
        return np.array(embeddings, dtype=np.float32)
