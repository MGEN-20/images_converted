import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .utils import encode_image, save_json, retry_request

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def describe_image_call(base64_image):
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image in detail. Identify if it's a business card, banner, logo, or other graphic design. Describe the visual style, colors, and key elements.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

async def describe_image(image_path: Path) -> dict:
    """Sends an image to OpenAI for description."""
    base64_image = encode_image(image_path)
    filename = image_path.name

    try:
        response = await retry_request(describe_image_call, base64_image, retries=5, delay=2)
        description = response.choices[0].message.content
        return {"filename": filename, "description": description}
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return {"filename": filename, "description": None, "error": str(e)}

async def process_images(input_dir: str, output_file: str):
    """Processes all images in the directory."""
    input_path = Path(input_dir)
    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    images = [
        p for p in input_path.iterdir() 
        if p.suffix.lower() in image_extensions and p.is_file()
    ]

    if not images:
        print(f"No images found in {input_dir}")
        return

    print(f"Found {len(images)} images. Processing...")
    
    # Limit to 2 concurrent requests to avoid rate limits
    semaphore = asyncio.Semaphore(2)

    async def sem_task(img):
        async with semaphore:
            return await describe_image(img)

    tasks = [sem_task(img) for img in images]
    results = await asyncio.gather(*tasks)
    
    # Filter out failed ones or handle them? For now, keep all.
    valid_results = [r for r in results if r.get("description")]
    
    save_json(valid_results, output_file)
    print(f"Saved {len(valid_results)} descriptions to {output_file}")

if __name__ == "__main__":
    # For testing standalone
    asyncio.run(process_images("data/input", "data/output/descriptions.json"))
