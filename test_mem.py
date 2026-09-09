import os
import psutil
import time

def print_mem(tag):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    print(f"{tag}: {mem:.2f} MB")

print_mem("Before loading")
from backend.app.services.embedding_service import EmbeddingService
service = EmbeddingService.get_instance()
print_mem("After loading")
