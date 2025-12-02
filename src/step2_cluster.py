import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .utils import load_json, save_json, retry_request

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_clusters_call(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that categorizes design projects."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

def generate_clusters(descriptions_file: str, output_file: str):
    """Generates categories based on image descriptions."""
    data = load_json(descriptions_file)
    if not data:
        print(f"No data found in {descriptions_file}")
        return

    # Extract just the description texts
    descriptions = [item['description'] for item in data if item.get('description')]
    
    if not descriptions:
        print("No descriptions to analyze.")
        return

    # If too many descriptions, maybe sample? For now, let's try to fit them.
    # Truncate if necessary or just take first 50 for discovery if list is huge.
    sample_descriptions = descriptions[:50] 
    
    prompt = f"""
    Analyze the following list of image descriptions from a graphic design portfolio.
    Identify distinct logical categories or clusters that these projects fall into (e.g., "Minimalist Business Cards", "Restaurant Menus", "Tech Logos").
    
    Return a JSON object with a single key "categories" containing a list of strings.
    Example: {{ "categories": ["Category 1", "Category 2"] }}
    
    Descriptions:
    {json.dumps(sample_descriptions)}
    """

    try:
        # Note: generate_clusters is synchronous, but retry_request is async. 
        # We should probably make this async or just use a sync retry loop here since it's one call.
        # For simplicity, let's just do a simple sync retry loop here or make the whole function async?
        # The original code was sync. Let's keep it sync but add a simple loop.
        
        response = None
        for i in range(3):
            try:
                response = generate_clusters_call(prompt)
                break
            except Exception as e:
                print(f"Error in clustering (attempt {i+1}): {e}")
                if i == 2: raise e
        
        if not response:
            return

        content = response.choices[0].message.content
        result = json.loads(content)
        
        categories = result.get("categories", [])
            
        save_json(categories, output_file)
        print(f"Generated {len(categories)} categories: {categories}")
        
    except Exception as e:
        print(f"Error generating clusters: {e}")

if __name__ == "__main__":
    generate_clusters("data/output/descriptions.json", "data/output/categories.json")
