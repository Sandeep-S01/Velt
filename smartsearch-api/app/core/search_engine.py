import pandas as pd
import chromadb
from typing import List, Dict, Any, Optional
import os
import requests
import time

class SemanticSearchEngine:
    def __init__(self,
                 model_name: str = 'all-MiniLM-L6-v2',
                 db_path: str = './chroma_db',
                 collection_name: str = 'products'):
        """
        Initialize the semantic search engine.

        Args:
            model_name: The sentence-transformers model to use for embeddings.
            db_path: Path to persist ChromaDB.
            collection_name: Name of the ChromaDB collection.
        """
        self.model_name = model_name
        self.use_hf_inference = os.getenv("USE_HF_INFERENCE", "false").lower() == "true"
        
        if self.use_hf_inference:
            self.model = None
            token = os.getenv("HF_TOKEN")
            self.hf_token = token.strip() if token else None
            if not self.hf_token:
                self.hf_token = None
        else:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            
        self.db_path = db_path
        self.collection_name = collection_name

        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=self.db_path)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def _get_huggingface_embeddings(self, texts: List[str]) -> List[List[float]]:
        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
            
        payload = {"inputs": texts}
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    # Ensure it's a list of lists (embeddings)
                    if isinstance(result, list):
                        if len(result) > 0 and not isinstance(result[0], list):
                            # Single list returned (if HF API returned 1D list instead of 2D for a single element)
                            return [result]
                        return result
                    raise ValueError(f"Unexpected response format from Hugging Face API: {result}")
                
                elif response.status_code == 503:
                    # Model is loading, retry after waiting
                    err_data = response.json()
                    wait_time = err_data.get("estimated_time", 10.0)
                    # Cap the wait time at 20 seconds per retry to avoid blocking indefinitely
                    wait_time = min(float(wait_time), 20.0)
                    print(f"Hugging Face model is loading. Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    response.raise_for_status()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Error calling Hugging Face API (attempt {attempt + 1}/{max_retries}): {e}. Retrying in 5 seconds...")
                time.sleep(5)
                
        raise RuntimeError("Failed to generate embeddings from Hugging Face Inference API after multiple retries.")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.use_hf_inference:
            return self._get_huggingface_embeddings(texts)
        else:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            if hasattr(embeddings, "tolist"):
                return embeddings.tolist()
            return embeddings

    def load_products_from_csv(self, csv_path: str,
                               description_column: str = 'description',
                               id_column: Optional[str] = None,
                               metadata_columns: Optional[List[str]] = None) -> None:
        """
        Load products from a CSV file, embed descriptions, and store in ChromaDB.

        Args:
            csv_path: Path to the CSV file.
            description_column: Column name containing product descriptions.
            id_column: Column name for unique IDs. If None, uses index.
            metadata_columns: List of column names to store as metadata.
        """
        df = pd.read_csv(csv_path)

        # Prepare data
        if id_column is None:
            ids = [str(i) for i in df.index]
        else:
            ids = df[id_column].astype(str).tolist()

        documents = df[description_column].fillna("").tolist()

        # Prepare metadata
        metadatas = []
        if metadata_columns:
            for _, row in df.iterrows():
                metadata = {col: row[col] for col in metadata_columns if col in row}
                metadatas.append(metadata)
        else:
            metadatas = [{} for _ in range(len(df))]

        # Generate embeddings
        print(f"Generating embeddings for {len(documents)} products...")
        embeddings = self.get_embeddings(documents)

        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Stored {len(documents)} products in ChromaDB collection '{self.collection_name}'.")

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for products similar to the query.

        Args:
            query: Natural language query string.
            n_results: Number of results to return.

        Returns:
            List of dictionaries containing id, document (description), metadata, and distance score.
        """
        # Embed the query
        query_embedding = self.get_embeddings([query])

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'description': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity score (0-1)
            })

        return formatted_results

    def _get_store_collection(self, store_id: str):
        """Get or create a store-specific ChromaDB collection with specifications from 05_Backend_Schema.md."""
        collection_name = f"products_store_{store_id}"
        metadata = {
            "store_id": store_id,
            "hnsw:space": "cosine",
            "hnsw:construction_ef": 128,
            "hnsw:search_ef": 64,
            "hnsw:M": 16,
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": 384,
            "chunk_size": 500,
            "chunk_overlap": 100,
            "version": "1.0"
        }
        return self.client.get_or_create_collection(name=collection_name, metadata=metadata)

    def index_store_products(self, store_id: str, products: List[Dict[str, Any]]) -> None:
        """
        Index a list of products into a store-specific ChromaDB collection.
        Each product should be a dictionary with id, title, description, and other optional metadata.
        """
        if not products:
            return

        collection = self._get_store_collection(store_id)

        ids = []
        documents = []
        metadatas = []

        for prod in products:
            prod_id = str(prod.get("id"))
            ids.append(prod_id)

            # Build document text
            title = prod.get("title", "")
            desc = prod.get("description", "")
            # Combine title and description for richer semantic context
            doc_text = f"{title}. {desc}" if desc else title
            documents.append(doc_text)

            # Prepare metadata according to 05_Backend_Schema.md
            metadata = {
                "product_id": prod_id,
                "external_id": str(prod.get("external_id", "")) or prod_id,
                "store_id": store_id,
                "title": title,
                "price": float(prod.get("price")) if prod.get("price") is not None else 0.0,
                "category": prod.get("category", "") or "",
                "brand": prod.get("brand", "") or "",
                "image_url": prod.get("image_url", "") or "",
                "product_url": prod.get("product_url", "") or "",
                "is_active": bool(prod.get("is_active", True)),
                "is_searchable": bool(prod.get("is_searchable", True)),
                "availability": prod.get("availability", "in_stock") or "in_stock"
            }
            metadatas.append(metadata)

        # Generate embeddings in batch
        embeddings = self.get_embeddings(documents)

        # Upsert into ChromaDB to overwrite if the ID already exists
        collection.upsert(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def delete_store_products(self, store_id: str, ids: List[str]) -> None:
        """Delete products by ID from the store-specific collection."""
        if not ids:
            return
        collection = self._get_store_collection(store_id)
        collection.delete(ids=ids)

    def search_store(self, store_id: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for products in a store-specific collection."""
        collection = self._get_store_collection(store_id)
        
        # Check if collection is empty
        total_count = collection.count()
        if total_count == 0:
            return []

        # Embed the query
        query_embedding = self.get_embeddings([query])

        # Ensure n_results does not exceed total items in collection
        actual_n = min(n_results, total_count)
        if actual_n <= 0:
            return []

        # Search in ChromaDB
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=actual_n,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i]
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'description': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': distance,
                    'score': float(1 - distance)  # Convert distance to similarity score
                })

        return formatted_results

# Example usage (for testing)
if __name__ == "__main__":
    # This block runs only when the script is executed directly
    engine = SemanticSearchEngine()
    # Example: load products from a CSV (you need to provide the path)
    # engine.load_products_from_csv('data/products.csv')
    # results = engine.search("example query")
    # print(results)
    pass