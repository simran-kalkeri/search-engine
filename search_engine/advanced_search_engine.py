"""
Advanced Search Engine with TF-IDF + Cosine Similarity and Vector Search
========================================================================

This module implements an advanced search engine that combines:
- TF-IDF with cosine similarity for text-based search
- Vector search using sentence embeddings for semantic similarity
- Fuzzy matching and approximate search
- Phrase matching and proximity search
- Integration with all recommendation components

This embodies the Kintsugi concept by treating different search methods
as complementary "repair" techniques for finding the best results.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import math
import re
import time
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

# Import our custom modules
from vector_search import VectorSearchEngine, SemanticSearchEnhancer
from recommendation_engine import KintsugiRecommendationEngine
from polya_urn_model import PolyaUrnModel
from granovetter_cascade import GranovetterCascadeModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TFIDFSearchEngine:
    """
    TF-IDF based search engine with cosine similarity.
    
    This class implements traditional text-based search using TF-IDF
    (Term Frequency-Inverse Document Frequency) and cosine similarity
    for ranking search results.
    """
    
    def __init__(self):
        """Initialize the TF-IDF search engine."""
        self.documents = {}  # doc_id -> document
        self.term_frequencies = defaultdict(dict)  # doc_id -> {term: frequency}
        self.document_frequencies = defaultdict(int)  # term -> document_count
        self.document_lengths = {}  # doc_id -> length
        self.vocabulary = set()  # All unique terms
        self.total_documents = 0
        
        # Kintsugi metadata
        self.kintsugi_notes = []
    
    def add_document(self, doc_id: int, document: Dict[str, Any]) -> None:
        """
        Add a document to the search index.
        
        Args:
            doc_id (int): Document identifier
            document (Dict[str, Any]): Document data
        """
        self.documents[doc_id] = document
        
        # Create searchable text
        searchable_text = self._create_searchable_text(document)
        
        # Tokenize and process text
        terms = self._tokenize_text(searchable_text)
        
        # Calculate term frequencies
        term_counts = Counter(terms)
        self.term_frequencies[doc_id] = dict(term_counts)
        
        # Update document frequencies
        for term in term_counts.keys():
            self.document_frequencies[term] += 1
        
        # Update vocabulary
        self.vocabulary.update(term_counts.keys())
        
        # Store document length
        self.document_lengths[doc_id] = len(terms)
        
        self.total_documents = len(self.documents)
        
        self.kintsugi_notes.append(f"✨ Added document {doc_id} to TF-IDF index")
    
    def _create_searchable_text(self, document: Dict[str, Any]) -> str:
        """Create searchable text from document fields."""
        # Priority fields for search
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
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Convert to lowercase and split
        text = text.lower()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into terms
        terms = text.split()
        
        # Filter out very short terms
        terms = [term for term in terms if len(term) > 2]
        
        return terms
    
    def calculate_tf_idf(self, term: str, doc_id: int) -> float:
        """
        Calculate TF-IDF score for a term in a document.
        
        Args:
            term (str): Term to calculate score for
            doc_id (int): Document identifier
            
        Returns:
            float: TF-IDF score
        """
        if doc_id not in self.term_frequencies:
            return 0.0
        
        # Term frequency
        tf = self.term_frequencies[doc_id].get(term, 0)
        if tf == 0:
            return 0.0
        
        # Document frequency
        df = self.document_frequencies.get(term, 0)
        if df == 0:
            return 0.0
        
        # Inverse document frequency
        idf = math.log(self.total_documents / df)
        
        # TF-IDF score
        return tf * idf
    
    def search(self, query: str, top_k: int = 10, 
              use_cosine_similarity: bool = True) -> List[Tuple[int, float, str]]:
        """
        Search for documents using TF-IDF.
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
            use_cosine_similarity (bool): Whether to use cosine similarity
            
        Returns:
            List[Tuple[int, float, str]]: List of (doc_id, score, match_type)
        """
        if not query.strip():
            return []
        
        # Tokenize query
        query_terms = self._tokenize_text(query)
        if not query_terms:
            return []
        
        # Calculate query vector
        query_vector = {}
        for term in query_terms:
            if term in self.vocabulary:
                # Calculate IDF for query term
                df = self.document_frequencies.get(term, 0)
                if df > 0:
                    idf = math.log(self.total_documents / df)
                    query_vector[term] = idf
        
        if not query_vector:
            return []
        
        # Search documents
        results = []
        for doc_id in self.documents.keys():
            score = self._calculate_document_score(query_vector, doc_id, use_cosine_similarity)
            
            if score > 0:
                # Determine match type
                match_type = self._determine_match_type(query_terms, doc_id)
                results.append((doc_id, score, match_type))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _calculate_document_score(self, query_vector: Dict[str, float], 
                                doc_id: int, use_cosine_similarity: bool) -> float:
        """Calculate document score for a query."""
        if use_cosine_similarity:
            return self._calculate_cosine_similarity(query_vector, doc_id)
        else:
            return self._calculate_dot_product(query_vector, doc_id)
    
    def _calculate_cosine_similarity(self, query_vector: Dict[str, float], 
                                   doc_id: int) -> float:
        """Calculate cosine similarity between query and document."""
        # Get document vector
        doc_vector = {}
        for term in query_vector.keys():
            tf_idf = self.calculate_tf_idf(term, doc_id)
            if tf_idf > 0:
                doc_vector[term] = tf_idf
        
        if not doc_vector:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = sum(query_vector[term] * doc_vector[term] for term in query_vector.keys() if term in doc_vector)
        
        query_norm = math.sqrt(sum(score ** 2 for score in query_vector.values()))
        doc_norm = math.sqrt(sum(score ** 2 for score in doc_vector.values()))
        
        if query_norm == 0 or doc_norm == 0:
            return 0.0
        
        return dot_product / (query_norm * doc_norm)
    
    def _calculate_dot_product(self, query_vector: Dict[str, float], 
                             doc_id: int) -> float:
        """Calculate dot product between query and document."""
        score = 0.0
        for term in query_vector.keys():
            tf_idf = self.calculate_tf_idf(term, doc_id)
            score += query_vector[term] * tf_idf
        
        return score
    
    def _determine_match_type(self, query_terms: List[str], doc_id: int) -> str:
        """Determine the type of match for a document."""
        doc_terms = set(self.term_frequencies[doc_id].keys())
        query_terms_set = set(query_terms)
        
        # Check for exact matches
        exact_matches = query_terms_set & doc_terms
        match_ratio = len(exact_matches) / len(query_terms_set)
        
        if match_ratio >= 0.8:
            return "kintsugi_exact"
        elif match_ratio >= 0.6:
            return "kintsugi_good"
        elif match_ratio >= 0.4:
            return "kintsugi_fair"
        else:
            return "kintsugi_poor"
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        return self.documents.get(doc_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return {
            'total_documents': self.total_documents,
            'vocabulary_size': len(self.vocabulary),
            'average_doc_length': sum(self.document_lengths.values()) / len(self.document_lengths) if self.document_lengths else 0,
            'kintsugi_notes_count': len(self.kintsugi_notes)
        }


class PhraseSearchEngine:
    """
    Phrase search engine for exact phrase matching.
    
    This class implements phrase search that looks for exact phrase
    matches in documents, providing higher precision for specific queries.
    """
    
    def __init__(self):
        """Initialize the phrase search engine."""
        self.documents = {}  # doc_id -> document
        self.phrase_index = defaultdict(set)  # phrase -> set of doc_ids
        self.kintsugi_notes = []
    
    def add_document(self, doc_id: int, document: Dict[str, Any]) -> None:
        """Add a document to the phrase index."""
        self.documents[doc_id] = document
        
        # Extract phrases from document
        phrases = self._extract_phrases(document)
        
        # Index phrases
        for phrase in phrases:
            self.phrase_index[phrase].add(doc_id)
        
        self.kintsugi_notes.append(f"✨ Added document {doc_id} to phrase index")
    
    def _extract_phrases(self, document: Dict[str, Any]) -> List[str]:
        """Extract phrases from document."""
        phrases = []
        
        # Get text fields
        text_fields = ['Brand', 'Type', 'Model Number', 'Features', 'Description']
        
        for field in text_fields:
            if field in document and document[field] and isinstance(document[field], str):
                text = document[field].lower()
                
                # Extract 2-gram and 3-gram phrases
                words = text.split()
                
                # 2-grams
                for i in range(len(words) - 1):
                    phrase = f"{words[i]} {words[i+1]}"
                    phrases.append(phrase)
                
                # 3-grams
                for i in range(len(words) - 2):
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    phrases.append(phrase)
        
        return phrases
    
    def search_phrases(self, query: str, top_k: int = 10) -> List[Tuple[int, float, str]]:
        """Search for exact phrase matches."""
        if not query.strip():
            return []
        
        query_lower = query.lower()
        results = []
        
        # Find documents containing the exact phrase
        for phrase, doc_ids in self.phrase_index.items():
            if query_lower in phrase:
                for doc_id in doc_ids:
                    # Calculate phrase match score
                    score = self._calculate_phrase_score(query_lower, phrase)
                    results.append((doc_id, score, "kintsugi_phrase_exact"))
        
        # Remove duplicates and sort
        unique_results = {}
        for doc_id, score, match_type in results:
            if doc_id not in unique_results or unique_results[doc_id][1] < score:
                unique_results[doc_id] = (doc_id, score, match_type)
        
        results = list(unique_results.values())
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def _calculate_phrase_score(self, query: str, phrase: str) -> float:
        """Calculate score for phrase match."""
        # Exact match gets highest score
        if query == phrase:
            return 1.0
        
        # Partial match gets lower score
        if query in phrase:
            return 0.8
        
        # Fuzzy match gets even lower score
        return 0.5


class AdvancedSearchEngine:
    """
    Advanced search engine integrating all search methods.
    
    This class combines TF-IDF search, vector search, phrase search,
    and recommendation components to provide comprehensive search results
    with Kintsugi-inspired repair and enhancement.
    """
    
    def __init__(self, data_file_path: str):
        """
        Initialize the advanced search engine.
        
        Args:
            data_file_path (str): Path to the data file
        """
        self.data_file_path = data_file_path
        
        # Initialize search components
        self.tfidf_engine = TFIDFSearchEngine()
        self.vector_engine = VectorSearchEngine()
        self.phrase_engine = PhraseSearchEngine()
        self.semantic_enhancer = SemanticSearchEnhancer(self.vector_engine)
        
        # Initialize recommendation components
        self.recommendation_engine = KintsugiRecommendationEngine(self.vector_engine)
        
        # Search configuration
        self.search_config = {
            'tfidf_weight': 0.4,
            'vector_weight': 0.3,
            'phrase_weight': 0.2,
            'recommendation_weight': 0.1,
            'enable_fuzzy_matching': True,
            'enable_semantic_search': True,
            'enable_phrase_search': True,
            'enable_recommendations': True
        }
        
        # Kintsugi metadata
        self.kintsugi_notes = []
        self.repair_history = []
        
        # Load data and build indices
        self._load_data_and_build_indices()
    
    def _load_data_and_build_indices(self) -> None:
        """Load data and build all search indices."""
        logger.info("Loading data and building search indices...")
        
        # Load data
        with open(self.data_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        logger.info(f"Loaded {len(products)} products")
        
        # Build indices
        for i, product in enumerate(products):
            # Add to TF-IDF engine
            self.tfidf_engine.add_document(i, product)
            
            # Add to vector engine
            self.vector_engine.add_documents([product])
            
            # Add to phrase engine
            self.phrase_engine.add_document(i, product)
            
            # Add to recommendation engine
            self.recommendation_engine.add_product(i, product)
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Processed {i + 1} products...")
        
        logger.info("All search indices built successfully")
        self.kintsugi_notes.append(f"✨ Built search indices for {len(products)} products")
    
    def search(self, query: str, user_id: Optional[str] = None, 
               top_k: int = 20, search_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Perform comprehensive search using all available methods.
        
        Args:
            query (str): Search query
            user_id (Optional[str]): User identifier for personalized results
            top_k (int): Number of results to return
            search_type (str): Type of search to perform
            
        Returns:
            Dict[str, Any]: Search results with metadata
        """
        start_time = time.time()
        
        if not query.strip():
            return self._create_empty_result("Empty query provided")
        
        # Perform different types of search
        if search_type == "comprehensive":
            results = self._comprehensive_search(query, user_id, top_k)
        elif search_type == "tfidf":
            results = self._tfidf_search(query, top_k)
        elif search_type == "vector":
            results = self._vector_search(query, top_k)
        elif search_type == "phrase":
            results = self._phrase_search(query, top_k)
        else:
            results = self._comprehensive_search(query, user_id, top_k)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Generate Kintsugi insights
        kintsugi_insights = self._generate_kintsugi_insights(query, results)
        
        return {
            'query': query,
            'search_type': search_type,
            'total_results': len(results),
            'results': results,
            'search_time': search_time,
            'kintsugi_insights': kintsugi_insights,
            'search_metadata': {
                'tfidf_stats': self.tfidf_engine.get_stats(),
                'vector_stats': self.vector_engine.get_stats(),
                'config': self.search_config
            }
        }
    
    def _comprehensive_search(self, query: str, user_id: Optional[str], 
                            top_k: int) -> List[Dict[str, Any]]:
        """Perform comprehensive search using all methods."""
        # Get results from each method
        tfidf_results = self._tfidf_search(query, top_k * 2)
        vector_results = self._vector_search(query, top_k * 2)
        phrase_results = self._phrase_search(query, top_k * 2)
        
        # Get recommendations if user_id provided
        recommendation_results = []
        if user_id and self.search_config['enable_recommendations']:
            recommendation_results = self._get_recommendation_results(user_id, top_k)
        
        # Blend results
        blended_results = self._blend_search_results(
            tfidf_results, vector_results, phrase_results, 
            recommendation_results, query
        )
        
        return blended_results[:top_k]
    
    def _tfidf_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform TF-IDF search."""
        results = self.tfidf_engine.search(query, top_k, use_cosine_similarity=True)
        
        formatted_results = []
        for doc_id, score, match_type in results:
            document = self.tfidf_engine.get_document(doc_id)
            if document:
                formatted_results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'match_type': match_type,
                    'method': 'tfidf',
                    'document': document,
                    'kintsugi_quality': self._get_kintsugi_quality(score, match_type)
                })
        
        return formatted_results
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform vector search."""
        results = self.vector_engine.search(query, top_k, threshold=0.3)
        
        formatted_results = []
        for doc_id, score, match_type in results:
            document = self.vector_engine.get_document(doc_id)
            if document:
                formatted_results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'match_type': match_type,
                    'method': 'vector',
                    'document': document,
                    'kintsugi_quality': self._get_kintsugi_quality(score, match_type)
                })
        
        return formatted_results
    
    def _phrase_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform phrase search."""
        results = self.phrase_engine.search_phrases(query, top_k)
        
        formatted_results = []
        for doc_id, score, match_type in results:
            document = self.phrase_engine.documents.get(doc_id)
            if document:
                formatted_results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'match_type': match_type,
                    'method': 'phrase',
                    'document': document,
                    'kintsugi_quality': self._get_kintsugi_quality(score, match_type)
                })
        
        return formatted_results
    
    def _get_recommendation_results(self, user_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Get recommendation results for a user."""
        recommendations = self.recommendation_engine.get_recommendations(user_id, top_k)
        
        formatted_results = []
        for rec in recommendations:
            formatted_results.append({
                'doc_id': rec['product_id'],
                'score': rec['blended_score'],
                'match_type': 'recommendation',
                'method': 'recommendation',
                'document': rec['product'],
                'kintsugi_quality': rec['kintsugi_metadata']['quality'],
                'recommendation_metadata': rec['kintsugi_metadata']
            })
        
        return formatted_results
    
    def _blend_search_results(self, tfidf_results: List[Dict[str, Any]], 
                            vector_results: List[Dict[str, Any]],
                            phrase_results: List[Dict[str, Any]],
                            recommendation_results: List[Dict[str, Any]],
                            query: str) -> List[Dict[str, Any]]:
        """Blend results from different search methods."""
        # Create a mapping of doc_id to result
        result_map = {}
        
        # Add TF-IDF results
        for result in tfidf_results:
            doc_id = result['doc_id']
            if doc_id not in result_map:
                result_map[doc_id] = result.copy()
                result_map[doc_id]['blended_score'] = 0.0
                result_map[doc_id]['methods_used'] = []
            
            result_map[doc_id]['blended_score'] += result['score'] * self.search_config['tfidf_weight']
            result_map[doc_id]['methods_used'].append('tfidf')
        
        # Add vector results
        for result in vector_results:
            doc_id = result['doc_id']
            if doc_id not in result_map:
                result_map[doc_id] = result.copy()
                result_map[doc_id]['blended_score'] = 0.0
                result_map[doc_id]['methods_used'] = []
            
            result_map[doc_id]['blended_score'] += result['score'] * self.search_config['vector_weight']
            result_map[doc_id]['methods_used'].append('vector')
        
        # Add phrase results
        for result in phrase_results:
            doc_id = result['doc_id']
            if doc_id not in result_map:
                result_map[doc_id] = result.copy()
                result_map[doc_id]['blended_score'] = 0.0
                result_map[doc_id]['methods_used'] = []
            
            result_map[doc_id]['blended_score'] += result['score'] * self.search_config['phrase_weight']
            result_map[doc_id]['methods_used'].append('phrase')
        
        # Add recommendation results
        for result in recommendation_results:
            doc_id = result['doc_id']
            if doc_id not in result_map:
                result_map[doc_id] = result.copy()
                result_map[doc_id]['blended_score'] = 0.0
                result_map[doc_id]['methods_used'] = []
            
            result_map[doc_id]['blended_score'] += result['score'] * self.search_config['recommendation_weight']
            result_map[doc_id]['methods_used'].append('recommendation')
        
        # Convert to list and sort by blended score
        blended_results = list(result_map.values())
        blended_results.sort(key=lambda x: x['blended_score'], reverse=True)
        
        return blended_results
    
    def _get_kintsugi_quality(self, score: float, match_type: str) -> str:
        """Determine Kintsugi quality based on score and match type."""
        if score >= 0.9:
            return 'perfect'
        elif score >= 0.7:
            return 'excellent'
        elif score >= 0.5:
            return 'good'
        elif score >= 0.3:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_kintsugi_insights(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """Generate Kintsugi insights about the search results."""
        insights = []
        
        if not results:
            insights.append("No results found - sometimes the most beautiful things are hidden in the cracks")
            return insights
        
        # Analyze result methods
        methods_used = set()
        for result in results:
            methods_used.update(result.get('methods_used', []))
        
        if 'tfidf' in methods_used:
            insights.append("Found text-based matches - precision in words")
        
        if 'vector' in methods_used:
            insights.append("Found semantic matches - understanding meaning")
        
        if 'phrase' in methods_used:
            insights.append("Found exact phrase matches - perfect precision")
        
        if 'recommendation' in methods_used:
            insights.append("Found personalized recommendations - tailored for you")
        
        # Analyze quality distribution
        qualities = [result.get('kintsugi_quality', 'poor') for result in results]
        quality_counts = Counter(qualities)
        
        if quality_counts.get('perfect', 0) > 0:
            insights.append(f"Found {quality_counts['perfect']} perfect matches - no repair needed!")
        
        if quality_counts.get('excellent', 0) > 0:
            insights.append(f"Found {quality_counts['excellent']} excellent matches - strong golden seams!")
        
        # Analyze blended scores
        scores = [result.get('blended_score', 0) for result in results]
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score > 0.7:
                insights.append("High overall quality - the repair work is strong!")
            elif avg_score > 0.5:
                insights.append("Good overall quality - some repairs needed but functional")
            else:
                insights.append("Mixed quality - every crack tells a story!")
        
        return insights
    
    def _create_empty_result(self, message: str) -> Dict[str, Any]:
        """Create an empty result with a message."""
        return {
            'query': '',
            'search_type': 'none',
            'total_results': 0,
            'results': [],
            'search_time': 0,
            'kintsugi_insights': [message],
            'search_metadata': {
                'tfidf_stats': self.tfidf_engine.get_stats(),
                'vector_stats': self.vector_engine.get_stats(),
                'config': self.search_config
            }
        }
    
    def record_interaction(self, user_id: str, product_id: int, 
                          interaction_type: str = "click") -> None:
        """Record a user interaction with a product."""
        self.recommendation_engine.record_interaction(user_id, product_id, interaction_type)
        self.kintsugi_notes.append(f"🔧 Recorded {interaction_type} for user {user_id} on product {product_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the search engine."""
        return {
            'tfidf_stats': self.tfidf_engine.get_stats(),
            'vector_stats': self.vector_engine.get_stats(),
            'recommendation_stats': self.recommendation_engine.get_kintsugi_insights(),
            'search_config': self.search_config,
            'kintsugi_notes_count': len(self.kintsugi_notes)
        }


def main():
    """Demo function to test the advanced search engine."""
    print("=== Advanced Search Engine Demo ===")
    
    # Initialize search engine
    search_engine = AdvancedSearchEngine('data-set.json')
    
    # Test different search types
    test_queries = [
        "iPhone 14 Pro",
        "noise cancelling headphones",
        "gaming laptop",
        "wireless bluetooth"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = search_engine.search(query, top_k=3)
        
        print(f"Found {results['total_results']} results in {results['search_time']:.3f}s")
        print(f"Insights: {results['kintsugi_insights']}")
        
        for i, result in enumerate(results['results'][:2]):
            print(f"  {i+1}. {result['document'].get('Brand', 'Unknown')} {result['document'].get('Type', 'Unknown')}")
            print(f"     Score: {result['blended_score']:.3f}, Methods: {result['methods_used']}")
            print(f"     Quality: {result['kintsugi_quality']}")


if __name__ == "__main__":
    main()
