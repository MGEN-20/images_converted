import os
import shutil
from pathlib import Path
from .utils import load_json

def organize_files(classified_file: str, source_dir: str, results_dir: str):
    """Copies files to their assigned category folders."""
    data = load_json(classified_file)
    if not data:
        print(f"No classified data found in {classified_file}")
        return

    print(f"Organizing {len(data)} files into {results_dir}...")

    for item in data:
        filename = item.get("filename")
        category = item.get("category", "Uncategorized")
        
        if not filename:
            continue

        # Sanitize category name to be safe for filesystem
        safe_category = "".join(c for c in category if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_category:
            safe_category = "Uncategorized"

        category_dir = Path(results_dir) / safe_category
        category_dir.mkdir(parents=True, exist_ok=True)

        source_path = Path(source_dir) / filename
        dest_path = category_dir / filename

        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
            except Exception as e:
                print(f"Failed to copy {filename}: {e}")
        else:
            print(f"Source file not found: {source_path}")

    print("Organization complete.")
