"""
Vector Search Module with Sentence Embeddings
============================================

This module implements semantic search using sentence embeddings (BERT)
for finding products based on meaning rather than exact text matches.
Integrates with the Kintsugi concept by treating semantic similarity
as a form of "repair" for imperfect queries.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import pickle
import json
from pathlib import Path
import math

# Try to import sentence-transformers, fallback to basic implementation
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available. Using basic TF-IDF fallback.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorSearchEngine:
    """
    Vector search engine using sentence embeddings for semantic similarity.
    
    This class implements semantic search that can find products based on
    meaning rather than exact text matches, embodying the Kintsugi concept
    of finding value in imperfect matches.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector search engine.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.embeddings = {}  # doc_id -> embedding
        self.documents = {}  # doc_id -> document
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # Initialize the model
        self._initialize_model()
        
        # Cache for similarity calculations
        self.similarity_cache = {}
    
    def _initialize_model(self) -> None:
        """Initialize the sentence transformer model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading sentence transformer model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer model: {e}")
                logger.info("Falling back to basic TF-IDF implementation")
                self.model = None
        else:
            logger.info("sentence-transformers not available. Using basic TF-IDF implementation")
            self.model = None
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector search index.
        
        Args:
            documents (List[Dict[str, Any]]): List of documents to index
        """
        logger.info(f"Adding {len(documents)} documents to vector search index...")
        
        for i, doc in enumerate(documents):
            doc_id = i
            self.documents[doc_id] = doc
            
            # Create searchable text
            searchable_text = self._create_searchable_text(doc)
            
            # Generate embedding
            embedding = self._generate_embedding(searchable_text)
            self.embeddings[doc_id] = embedding
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Processed {i + 1} documents...")
        
        logger.info(f"Vector search index built with {len(self.embeddings)} documents")
    
    def _create_searchable_text(self, document: Dict[str, Any]) -> str:
        """
        Create searchable text from document fields.
        
        Args:
            document (Dict[str, Any]): Document data
            
        Returns:
            str: Combined searchable text
        """
        # Priority fields for semantic search
        priority_fields = [
            'Brand', 'Type', 'Model Number', 'Features', 'Description',
            'Specifications', 'Key Features', 'Other Features'
        ]
        
        searchable_parts = []
        
        # Add priority fields first
        for field in priority_fields:
            if field in document and document[field] and isinstance(document[field], str):
                searchable_parts.append(document[field])
        
        # Add other text fields
        for key, value in document.items():
            if (key not in priority_fields and 
                isinstance(value, str) and 
                value.strip() and 
                not key.startswith('_')):
                searchable_parts.append(value)
        
        return ' '.join(searchable_parts)
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text (str): Text to embed
            
        Returns:
            np.ndarray: Embedding vector
        """
        if self.model is not None:
            # Use sentence transformer
            return self.model.encode(text, convert_to_numpy=True)
        else:
            # Fallback to basic TF-IDF-like embedding
            return self._basic_embedding(text)
    
    def _basic_embedding(self, text: str) -> np.ndarray:
        """
        Create a basic embedding using TF-IDF-like approach.
        
        Args:
            text (str): Text to embed
            
        Returns:
            np.ndarray: Basic embedding vector
        """
        # Simple word-based embedding
        words = text.lower().split()
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
        
        # Create a simple embedding based on word frequencies
        # This is a simplified approach - in practice, you'd use proper TF-IDF
        embedding = np.zeros(self.embedding_dim)
        
        for i, (word, count) in enumerate(word_counts.items()):
            if i < self.embedding_dim:
                embedding[i] = count
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def search(self, query: str, top_k: int = 10, 
               threshold: float = 0.5) -> List[Tuple[int, float, str]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
            threshold (float): Minimum similarity threshold
            
        Returns:
            List[Tuple[int, float, str]]: List of (doc_id, score, match_type) tuples
        """
        if not query.strip():
            return []
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Calculate similarities
        similarities = []
        for doc_id, doc_embedding in self.embeddings.items():
            similarity = self._calculate_cosine_similarity(query_embedding, doc_embedding)
            
            if similarity >= threshold:
                # Determine match type based on similarity
                if similarity >= 0.9:
                    match_type = "kintsugi_semantic_exact"
                elif similarity >= 0.8:
                    match_type = "kintsugi_semantic_high"
                elif similarity >= 0.7:
                    match_type = "kintsugi_semantic_good"
                elif similarity >= 0.6:
                    match_type = "kintsugi_semantic_fair"
                else:
                    match_type = "kintsugi_semantic_poor"
                
                similarities.append((doc_id, similarity, match_type))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (np.ndarray): First vector
            vec2 (np.ndarray): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        # Ensure vectors are the same length
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_similar_products(self, product_id: int, top_k: int = 5) -> List[Tuple[int, float, str]]:
        """
        Find products similar to a given product.
        
        Args:
            product_id (int): ID of the product to find similar items for
            top_k (int): Number of similar products to return
            
        Returns:
            List[Tuple[int, float, str]]: List of similar products
        """
        if product_id not in self.embeddings:
            return []
        
        product_embedding = self.embeddings[product_id]
        similarities = []
        
        for doc_id, doc_embedding in self.embeddings.items():
            if doc_id == product_id:
                continue  # Skip the same product
            
            similarity = self._calculate_cosine_similarity(product_embedding, doc_embedding)
            
            if similarity >= 0.3:  # Lower threshold for similar products
                match_type = f"kintsugi_similarity_{self._get_similarity_level(similarity)}"
                similarities.append((doc_id, similarity, match_type))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _get_similarity_level(self, similarity: float) -> str:
        """Get similarity level description."""
        if similarity >= 0.9:
            return "exact"
        elif similarity >= 0.8:
            return "high"
        elif similarity >= 0.7:
            return "good"
        elif similarity >= 0.6:
            return "fair"
        else:
            return "low"
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.
        
        Args:
            doc_id (int): Document ID
            
        Returns:
            Optional[Dict[str, Any]]: Document if found
        """
        return self.documents.get(doc_id)
    
    def save_embeddings(self, filepath: str) -> None:
        """
        Save embeddings to file.
        
        Args:
            filepath (str): Path to save embeddings
        """
        data = {
            'embeddings': {str(k): v.tolist() for k, v in self.embeddings.items()},
            'documents': self.documents,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Embeddings saved to {filepath}")
    
    def load_embeddings(self, filepath: str) -> None:
        """
        Load embeddings from file.
        
        Args:
            filepath (str): Path to load embeddings from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct embeddings
        self.embeddings = {
            int(k): np.array(v) for k, v in data['embeddings'].items()
        }
        self.documents = data['documents']
        self.model_name = data.get('model_name', self.model_name)
        self.embedding_dim = data.get('embedding_dim', self.embedding_dim)
        
        logger.info(f"Embeddings loaded from {filepath}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector search engine.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        return {
            'total_documents': len(self.documents),
            'total_embeddings': len(self.embeddings),
            'embedding_dimension': self.embedding_dim,
            'model_name': self.model_name,
            'model_available': self.model is not None,
            'cache_size': len(self.similarity_cache)
        }


class SemanticSearchEnhancer:
    """
    Enhances search results with semantic similarity.
    
    This class integrates vector search with traditional search to provide
    better results by combining exact matches with semantic understanding.
    """
    
    def __init__(self, vector_engine: VectorSearchEngine):
        """
        Initialize the semantic search enhancer.
        
        Args:
            vector_engine (VectorSearchEngine): Vector search engine instance
        """
        self.vector_engine = vector_engine
    
    def enhance_search_results(self, query: str, 
                             traditional_results: List[Tuple[int, float, str]],
                             semantic_weight: float = 0.3) -> List[Tuple[int, float, str]]:
        """
        Enhance traditional search results with semantic similarity.
        
        Args:
            query (str): Search query
            traditional_results: Results from traditional search
            semantic_weight (float): Weight for semantic similarity (0.0-1.0)
            
        Returns:
            List[Tuple[int, float, str]]: Enhanced results
        """
        if not traditional_results:
            return []
        
        # Get semantic results
        semantic_results = self.vector_engine.search(query, top_k=50, threshold=0.3)
        
        # Create a mapping of doc_id to semantic score
        semantic_scores = {doc_id: score for doc_id, score, _ in semantic_results}
        
        # Enhance traditional results
        enhanced_results = []
        for doc_id, traditional_score, match_type in traditional_results:
            # Get semantic score for this document
            semantic_score = semantic_scores.get(doc_id, 0.0)
            
            # Combine scores
            combined_score = (1 - semantic_weight) * traditional_score + semantic_weight * semantic_score
            
            # Update match type if semantic similarity is high
            if semantic_score > 0.7:
                match_type = f"kintsugi_hybrid_{match_type}"
            
            enhanced_results.append((doc_id, combined_score, match_type))
        
        # Add high-scoring semantic results that weren't in traditional results
        traditional_doc_ids = {doc_id for doc_id, _, _ in traditional_results}
        for doc_id, semantic_score, match_type in semantic_results:
            if doc_id not in traditional_doc_ids and semantic_score > 0.6:
                enhanced_results.append((doc_id, semantic_score * semantic_weight, match_type))
        
        # Sort by combined score
        enhanced_results.sort(key=lambda x: x[1], reverse=True)
        
        return enhanced_results
    
    def generate_semantic_insights(self, query: str, results: List[Tuple[int, float, str]]) -> str:
        """
        Generate insights about semantic search results.
        
        Args:
            query (str): Search query
            results: Search results
            
        Returns:
            str: Semantic insights
        """
        if not results:
            return "No semantic matches found"
        
        # Analyze result types
        semantic_count = sum(1 for _, _, match_type in results if 'semantic' in match_type)
        hybrid_count = sum(1 for _, _, match_type in results if 'hybrid' in match_type)
        
        insights = []
        
        if semantic_count > 0:
            insights.append(f"Found {semantic_count} semantic matches - meaning matters!")
        
        if hybrid_count > 0:
            insights.append(f"Found {hybrid_count} hybrid matches - best of both worlds!")
        
        if semantic_count == 0 and hybrid_count == 0:
            insights.append("Traditional matches found - precision over meaning")
        
        return " | ".join(insights)


def main():
    """Demo function to test vector search."""
    # This would be used with actual data in the full implementation
    print("=== Vector Search Engine Demo ===")
    print("This module provides semantic search capabilities.")
    print("Use it with the main search engine for enhanced results.")


if __name__ == "__main__":
    main()
