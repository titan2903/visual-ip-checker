import os
import psutil
import torch

def print_mem(tag):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    print(f"{tag}: {mem:.2f} MB")

print_mem("Before loading")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("clip-ViT-B-32", model_kwargs={"torch_dtype": torch.bfloat16})
print_mem("After loading")
