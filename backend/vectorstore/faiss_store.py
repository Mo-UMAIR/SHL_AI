import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class FAISSRetriever:
    def __init__(self, catalog_path: str, model_name: str = 'all-MiniLM-L6-v2'):
        self.catalog_path = catalog_path
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.load_and_index()

    def _prepare_text(self, item):
        # Create a rich text representation for embedding
        text = f"Name: {item.get('name', '')}\n"
        text += f"Test Type: {item.get('test_type', '')} ({item.get('keys_full', '')})\n"
        text += f"Category/Level: {item.get('category', '')}\n"
        text += f"Description: {item.get('description', '')}\n"
        text += f"Duration: {item.get('duration', '')}\n"
        return text

    def load_and_index(self):
        if not os.path.exists(self.catalog_path):
            print(f"Warning: {self.catalog_path} not found.")
            return

        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)

        print(f"Loaded {len(self.documents)} documents. Building index...")
        
        texts = [self._prepare_text(doc) for doc in self.documents]
        
        # In a real scenario with very long descriptions, we would chunk. 
        # But SHL descriptions are usually short paragraphs, so we can embed the whole item.
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        print("FAISS index built successfully.")

    def search(self, query: str, top_k: int = 15, keyword_filters: list = None):
        """
        Hybrid retrieval: semantic search + naive keyword matching & filtering.
        """
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k * 2) # Fetch more for reranking/filtering
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            doc = self.documents[idx]
            
            # Simple keyword matching (boost score if keywords match)
            # A real hybrid would use BM25. This is a simplified version.
            score = 1.0 / (1.0 + distances[0][i]) # Normalize distance to score
            
            if keyword_filters:
                # E.g., if user wants "Java", boost items with "Java" in name or description
                text_content = (doc.get("name", "") + " " + doc.get("description", "")).lower()
                for kw in keyword_filters:
                    if kw.lower() in text_content:
                        score += 0.5 # Boost score
            
            results.append((score, doc))
        
        # Sort by boosted score
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k docs
        return [doc for score, doc in results[:top_k]]
