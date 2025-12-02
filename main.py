import asyncio
import argparse
import sys
import os
from pathlib import Path
from src.step1_describe import process_images
from src.step2_cluster import generate_clusters
from src.step3_classify import assign_categories
from src.organize import organize_files

def main():
    parser = argparse.ArgumentParser(description="AI Image Categorization Pipeline")
    parser.add_argument("input_dir", nargs="?", help="Path to the directory containing images")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4], help="Run a specific step (1-4)")
    parser.add_argument("--all", action="store_true", help="Run all steps sequentially")
    
    args = parser.parse_args()

    if not args.input_dir:
        # Fallback for dev/testing if not provided, or show help
        # But user requested "podaje ścieżkę", so let's require it or default to current dir?
        # Let's default to 'data/input' if not provided to keep backward compat for now, 
        # but print a message.
        print("No input directory specified, defaulting to 'data/input'")
        input_dir = "data/input"
    else:
        input_dir = args.input_dir

    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    # Setup results directory structure
    results_dir = input_path / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Define file paths inside results dir
    desc_file = results_dir / "descriptions.json"
    cats_file = results_dir / "categories.json"
    final_file = results_dir / "classified_projects.json"

    # Step 1: Describe
    if args.step == 1 or args.all:
        print(f"\n--- Step 1: Image Description (Input: {input_dir}) ---")
        asyncio.run(process_images(str(input_path), str(desc_file)))
    
    # Step 2: Cluster
    if args.step == 2 or args.all:
        print("\n--- Step 2: Clustering ---")
        generate_clusters(str(desc_file), str(cats_file))

    # Step 3: Classify
    if args.step == 3 or args.all:
        print("\n--- Step 3: Classification ---")
        asyncio.run(assign_categories(str(desc_file), str(cats_file), str(final_file)))

    # Step 4: Organize
    if args.step == 4 or args.all:
        print("\n--- Step 4: Organization ---")
        organize_files(str(final_file), str(input_path), str(results_dir))

    if not args.step and not args.all:
        parser.print_help()

if __name__ == "__main__":
    main()
