#!/usr/bin/env python3
"""
CLI demo for the semantic search engine.
Loads sample data and answers queries from the command line.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.search_engine import SemanticSearchEngine

def main():
    # Initialize the search engine
    # Using a local ChromaDB path within the project
    db_path = os.path.join(os.path.dirname(__file__), 'chroma_db')
    engine = SemanticSearchEngine(db_path=db_path)

    # Load sample data
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_products.csv')
    print(f"Loading products from {csv_path}...")
    engine.load_products_from_csv(
        csv_path=csv_path,
        description_column='description',
        id_column='id',
        metadata_columns=['title', 'price', 'category']
    )

    # Interactive search loop
    print("\nSemantic Search Demo (type 'exit' to quit)")
    print("-" * 50)
    while True:
        query = input("\nEnter your search query: ").strip()
        if query.lower() in ['exit', 'quit']:
            break
        if not query:
            continue

        results = engine.search(query, n_results=3)
        print(f"\nTop {len(results)} results for: '{query}'")
        print("-" * 50)
        for i, res in enumerate(results, 1):
            print(f"{i}. ID: {res['id']}")
            print(f"   Title: {res['metadata'].get('title', 'N/A')}")
            print(f"   Description: {res['description']}")
            print(f"   Price: ${res['metadata'].get('price', 'N/A')}")
            print(f"   Category: {res['metadata'].get('category', 'N/A')}")
            print(f"   Relevance Score: {res['score']:.4f}")
            print()

if __name__ == "__main__":
    main()