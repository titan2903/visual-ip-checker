import os
import sys
import logging
from pathlib import Path
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
import onnxruntime
from onnxruntime.quantization import quantize_dynamic, QuantType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tarum.export_onnx")


class CLIPVisionEncoder(nn.Module):
    def __init__(self, clip_model):
        super().__init__()
        self.clip_model = clip_model

    def forward(self, pixel_values):
        # Extract 512-dim visual features
        return self.clip_model.get_image_features(pixel_values=pixel_values)


def export_and_quantize():
    project_root = Path(__file__).resolve().parent.parent.parent
    models_dir = project_root / "backend" / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    fp32_path = models_dir / "clip_vision_fp32.onnx"
    int8_path = models_dir / "clip_vision_int8.onnx"

    logger.info("Loading SentenceTransformer clip-ViT-B-32...")
    st_model = SentenceTransformer("clip-ViT-B-32")
    clip_model = st_model[0].model.eval()

    vision_encoder = CLIPVisionEncoder(clip_model).eval()

    logger.info("Exporting Vision Model to ONNX FP32...")
    dummy_input = torch.randn(1, 3, 224, 224, dtype=torch.float32)

    torch.onnx.export(
        vision_encoder,
        dummy_input,
        str(fp32_path),
        input_names=["pixel_values"],
        output_names=["embedding"],
        dynamic_axes={
            "pixel_values": {0: "batch_size"},
            "embedding": {0: "batch_size"},
        },
        opset_version=14,
        do_constant_folding=True,
    )

    fp32_size_mb = fp32_path.stat().st_size / (1024 * 1024)
    logger.info(f"ONNX FP32 exported successfully: {fp32_path} ({fp32_size_mb:.2f} MB)")

    logger.info("Quantizing to INT8 using onnxruntime.quantization...")
    quantize_dynamic(
        model_input=str(fp32_path),
        model_output=str(int8_path),
        weight_type=QuantType.QInt8,
    )

    int8_size_mb = int8_path.stat().st_size / (1024 * 1024)
    logger.info(f"ONNX INT8 quantized successfully: {int8_path} ({int8_size_mb:.2f} MB)")

    # Remove the large FP32 file and external data to save disk space
    if fp32_path.exists():
        fp32_path.unlink()
        fp32_data = Path(str(fp32_path) + ".data")
        if fp32_data.exists():
            fp32_data.unlink()
        logger.info(f"Removed temporary FP32 model {fp32_path}")

    # Verify loading and running session
    logger.info("Verifying ONNX INT8 session inference...")
    session = onnxruntime.InferenceSession(str(int8_path), providers=["CPUExecutionProvider"])
    import numpy as np
    dummy_np = np.random.randn(1, 3, 224, 224).astype(np.float32)
    outputs = session.run(["embedding"], {"pixel_values": dummy_np})
    output_vec = outputs[0]
    logger.info(f"Inference test succeeded! Output shape: {output_vec.shape}")
    assert output_vec.shape == (1, 512), f"Expected shape (1, 512), got {output_vec.shape}"
    logger.info("ONNX INT8 model is ready and verified!")


if __name__ == "__main__":
    export_and_quantize()
