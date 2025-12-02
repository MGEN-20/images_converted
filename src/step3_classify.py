import asyncio
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .utils import load_json, save_json, retry_request

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def assign_category_call(description, categories):
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": f"You are a helpful assistant. Assign the most fitting category from the provided list to the description. Categories: {json.dumps(categories)}"
            },
            {
                "role": "user", 
                "content": f"Description: {description}\n\nReturn ONLY the category name."
            }
        ],
        max_tokens=50
    )

async def assign_category(item: dict, categories: list) -> dict:
    """Assigns a category to a single item."""
    description = item.get("description")
    if not description:
        return {**item, "category": "Uncategorized"}

    try:
        response = await retry_request(assign_category_call, description, categories, retries=5, delay=2)
        category = response.choices[0].message.content.strip()
        # Basic cleanup if it returns quotes
        category = category.strip('"').strip("'")
        return {**item, "category": category}
    except Exception as e:
        print(f"Error assigning category for {item.get('filename')}: {e}")
        return {**item, "category": "Error"}

async def assign_categories(descriptions_file: str, categories_file: str, output_file: str):
    """Assigns categories to all descriptions."""
    descriptions = load_json(descriptions_file)
    categories = load_json(categories_file)

    if not descriptions:
        print("No descriptions found.")
        return
    if not categories:
        print("No categories found.")
        return

    print(f"Assigning categories to {len(descriptions)} items using {len(categories)} clusters...")

    # Limit to 2 concurrent requests to avoid rate limits
    semaphore = asyncio.Semaphore(2)

    async def sem_task(item):
        async with semaphore:
            return await assign_category(item, categories)

    tasks = [sem_task(item) for item in descriptions]
    results = await asyncio.gather(*tasks)

    save_json(results, output_file)
    print(f"Saved classified projects to {output_file}")

if __name__ == "__main__":
    asyncio.run(assign_categories("data/output/descriptions.json", "data/output/categories.json", "data/output/classified_projects.json"))
