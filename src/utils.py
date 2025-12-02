import base64
import json
import os
import asyncio
from pathlib import Path

def encode_image(image_path: str | Path) -> str:
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def save_json(data: any, file_path: str | Path):
    """Saves data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_json(file_path: str | Path) -> any:
    """Loads data from a JSON file."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def retry_request(func, *args, retries=3, delay=1, **kwargs):
    """Retries an async function with exponential backoff."""
    for i in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                if i == retries - 1:
                    raise e
                wait_time = delay * (2 ** i)
                print(f"Rate limit hit. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise e
