"""
Load Knowledge
--------------

Loads table metadata, validated queries, and business rules into
the data agent's knowledge base (vector DB).

Usage:
    python -m backend.scripts.load_knowledge             # Upsert
    python -m backend.scripts.load_knowledge --recreate   # Drop and reload
"""

import argparse
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
TABLES_DIR = DATA_DIR / "tables"
QUERIES_DIR = DATA_DIR / "queries"
BUSINESS_DIR = DATA_DIR / "business"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load knowledge into vector database")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Drop existing knowledge and reload from scratch",
    )
    args = parser.parse_args()

    from backend.agents.data_agent import data_knowledge

    if args.recreate:
        print("Recreating knowledge base (dropping existing data)...\n")
        if data_knowledge.vector_db:
            data_knowledge.vector_db.drop()
            data_knowledge.vector_db.create()

    print(f"Loading knowledge from: {DATA_DIR}\n")

    for subdir_name, subdir_path in [("tables", TABLES_DIR), ("queries", QUERIES_DIR), ("business", BUSINESS_DIR)]:
        if not subdir_path.exists():
            print(f"  {subdir_name}/: (not found)")
            continue

        files = [f for f in subdir_path.iterdir() if f.is_file() and not f.name.startswith(".")]
        print(f"  {subdir_name}/: {len(files)} files")

        if files:
            data_knowledge.insert(name=f"knowledge-{subdir_name}", path=str(subdir_path))

    print("\nDone!")
