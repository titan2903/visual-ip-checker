import os
import httpx
import base64

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/clip-ViT-B-32"
# Note: we need an API token if we have one. Without one, rate limits apply.
headers = {}
if "HF_TOKEN" in os.environ:
    headers["Authorization"] = f"Bearer {os.environ['HF_TOKEN']}"

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = httpx.post(API_URL, headers=headers, data=data)
    return response.json()

if __name__ == "__main__":
    # Create a dummy image
    from PIL import Image
    img = Image.new('RGB', (224, 224), color = 'red')
    img.save('dummy.jpg')
    
    result = query("dummy.jpg")
    if isinstance(result, list):
        print(f"Success! Vector length: {len(result)}")
        print(f"First 5 elements: {result[:5]}")
    else:
        print(f"Response: {result}")
