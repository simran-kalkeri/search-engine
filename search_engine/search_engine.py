"""
Main Search Engine Module with Kintsugi Concept
===============================================

This module implements the main search engine that integrates all components
to provide a comprehensive search experience with Kintsugi-inspired fuzzy
matching and highlighting.

Author: Search Engine Implementation
Date: 2025
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import time

from parser import ECommerceDataParser
from preprocessor import TextPreprocessor
from indexer import InvertedIndex
from fuzzy_matcher import KintsugiFuzzyMatcher
from formatter import KintsugiResultFormatter

# Import new features
try:
    from polya_urn_model import PolyaUrnModel
    POLYA_URN_AVAILABLE = True
except ImportError:
    POLYA_URN_AVAILABLE = False
    print("WARNING: Polya Urn Model not available. Using basic click tracking.")

try:
    from granovetter_cascade import GranovetterCascadeModel
    CASCADE_AVAILABLE = True
except ImportError:
    CASCADE_AVAILABLE = False
    print("WARNING: Granovetter Cascade Model not available. Using basic recommendations.")

try:
    from vector_search import VectorSearchEngine
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    print("WARNING: Vector search not available. Using TF-IDF only.")

try:
    from pagerank_ranker import PageRankRanker
    PAGERANK_AVAILABLE = True
except ImportError:
    PAGERANK_AVAILABLE = False
    print("WARNING: PageRank not available. Using basic ranking.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KintsugiSearchEngine:
    """
    Main search engine implementing the Kintsugi concept.
    
    This class treats "imperfect" queries as valuable, implementing
    fuzzy matching and approximate search to find results even when
    queries are broken, misspelled, or incomplete.
    """
    
    def __init__(self, data_file_path: str, index_file_path: Optional[str] = None):
        """
        Initialize the search engine.
        
        Args:
            data_file_path (str): Path to the JSON data file
            index_file_path (Optional[str]): Path to save/load index file
        """
        self.data_file_path = data_file_path
        self.index_file_path = index_file_path or "search_index.json"
        
        # Initialize components
        self.parser = ECommerceDataParser(data_file_path)
        self.preprocessor = TextPreprocessor()
        self.indexer = InvertedIndex()
        self.fuzzy_matcher = KintsugiFuzzyMatcher()
        self.formatter = KintsugiResultFormatter()
        
        # Initialize new features
        if POLYA_URN_AVAILABLE:
            self.polya_urn = PolyaUrnModel(initial_balls=1, boost_factor=1.5)
            logger.info("✅ Polya Urn Model initialized")
        else:
            self.polya_urn = None
            
        if CASCADE_AVAILABLE:
            self.cascade_model = GranovetterCascadeModel(base_threshold=0.3, cascade_strength=0.6)
            logger.info("✅ Granovetter Cascade Model initialized")
        else:
            self.cascade_model = None
            
        if VECTOR_SEARCH_AVAILABLE:
            self.vector_engine = VectorSearchEngine()
            logger.info("✅ Vector Search Engine initialized")
        else:
            self.vector_engine = None
            
        if PAGERANK_AVAILABLE:
            self.pagerank_ranker = PageRankRanker()
            logger.info("✅ PageRank Ranker initialized")
        else:
            self.pagerank_ranker = None
        
        # Search configuration
        self.search_config = {
            'exact_threshold': 0.9,
            'fuzzy_threshold': 0.8,  # Higher threshold for better quality
            'max_results': 50,
            'enable_highlighting': True,
            'enable_kintsugi_insights': True
        }
        
        # Build or load index
        self._initialize_index()
        
        # Initialize new features with data
        self._initialize_new_features()
    
    def _initialize_index(self) -> None:
        """Initialize the search index."""
        index_path = Path(self.index_file_path)
        
        if index_path.exists():
            logger.info(f"Loading existing index from {self.index_file_path}")
            try:
                self.indexer.load_index(self.index_file_path)
                logger.info("Index loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Building new index...")
                self._build_index()
        else:
            logger.info("Building new search index...")
            self._build_index()
    
    def _initialize_new_features(self) -> None:
        """Initialize new features with loaded data."""
        # Get products from parser
        products = self.parser.get_all_products()
        
        # Add products to Polya Urn Model
        if self.polya_urn:
            for i, product in enumerate(products):
                self.polya_urn.add_product(i)
            logger.info(f"Added {len(products)} products to Polya Urn Model")
        
        # Initialize cascade model with product network
        if self.cascade_model:
            self.cascade_model.simulate_cascade_network(
                num_products=min(1000, len(products)), 
                num_users=200
            )
            logger.info("Cascade model network initialized")
        
        # Add products to vector search engine
        if self.vector_engine:
            vector_docs = []
            for i, product in enumerate(products[:1000]):  # Limit for performance
                vector_docs.append({'id': i, 'content': str(product)})
            self.vector_engine.add_documents(vector_docs)
            logger.info(f"Added {min(1000, len(products))} products to vector search")
        
        # Build PageRank graph
        if self.pagerank_ranker:
            try:
                # Use add_products method (builds graph automatically)
                self.pagerank_ranker.add_products(products[:1000])
                logger.info(f"Built PageRank graph with {min(1000, len(products))} products")
            except Exception as e:
                logger.warning(f"PageRank initialization failed: {e}")
                self.pagerank_ranker = None
    
    def _build_index(self) -> None:
        """Build the search index from the data."""
        products = self.parser.get_all_products()
        
        logger.info(f"Indexing {len(products)} products...")
        
        for i, product in enumerate(products):
            self.indexer.add_document(i, product)
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Indexed {i + 1} products...")
        
        # Save the index
        self.indexer.save_index(self.index_file_path)
        logger.info(f"Index built and saved to {self.index_file_path}")
    
    def search(self, query: str, search_type: str = "auto", 
              max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform a search with Kintsugi-inspired fuzzy matching.
        
        Args:
            query (str): Search query
            search_type (str): Type of search ("exact", "fuzzy", "auto")
            max_results (Optional[int]): Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Search results with Kintsugi metadata
        """
        start_time = time.time()
        
        if not query or not query.strip():
            return self._create_empty_result("Empty query provided")
        
        query = query.strip()
        max_results = max_results or self.search_config['max_results']
        
        # Determine search strategy
        if search_type == "auto":
            search_type = self._determine_search_type(query)
        
        # Perform search
        if search_type == "exact":
            results = self._exact_search(query, max_results)
        elif search_type == "fuzzy":
            results = self._fuzzy_search(query, max_results)
        else:
            # Combined search
            results = self._combined_search(query, max_results)
        
        # Process results with improved ranking
        processed_results = self._process_results_with_improved_ranking(results, query)
        
        # Apply new features for enhanced ranking
        enhanced_results = self._apply_enhanced_ranking(processed_results, query)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Create final result
        # Format results for clean display
        formatted_results = self.formatter.format_results_list(enhanced_results, query)
        
        return {
            'query': query,
            'search_type': search_type,
            'total_results': len(formatted_results),
            'results': formatted_results[:max_results],
            'raw_results': processed_results,  # Keep all raw results for reference
            'search_time': search_time,
            'kintsugi_insights': self._generate_kintsugi_insights(processed_results),
            'search_metadata': {
                'index_stats': self.indexer.get_index_stats(),
                'config': self.search_config
            }
        }
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific product with Kintsugi repairs.
        
        Args:
            product_id (str): Product ID to retrieve details for
            
        Returns:
            Dict[str, Any]: Product details with categorized information
        """
        try:
            # Get product with Kintsugi repairs
            product = self.parser.get_product_by_id(product_id, repaired=True)
            
            if not product:
                return {
                    'error': f'Product with ID {product_id} not found',
                    'product_id': product_id,
                    'success': False
                }
            
            # Organize product data for display
            product_data = {
                'id': product.get('id'),
                'basic_info': {},
                'features': {},
                'specifications': {},
                'kintsugi_notes': product.get('kintsugi_notes', []),
                'all_fields': {}
            }
            
            # Categorize fields for better presentation
            basic_fields = ['Brand', 'Type', 'Model Number', 'Color', 'Price']
            spec_fields = ['Dimensions', 'Weight', 'Warranty', 'Material', 'Power', 'Voltage', 'Battery', 'Display', 'Storage']
            
            for key, value in product.items():
                if key == 'kintsugi_notes' or value is None or str(value).strip() == '':
                    continue
                
                product_data['all_fields'][key] = value
                
                if key in basic_fields:
                    product_data['basic_info'][key] = value
                elif key in spec_fields:
                    product_data['specifications'][key] = value
                else:
                    product_data['features'][key] = value
            
            return {
                'success': True,
                'product': product_data,
                'kintsugi_insights': self._generate_product_insights(product),
                'product_id': product_id
            }
            
        except Exception as e:
            logger.error(f"Error retrieving product details for {product_id}: {e}")
            return {
                'error': f'Error retrieving product details: {str(e)}',
                'product_id': product_id,
                'success': False
            }
    
    def _generate_product_insights(self, product: Dict[str, Any]) -> List[str]:
        """
        Generate Kintsugi insights for a product.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            List[str]: List of insights
        """
        insights = []
        
        # Check for Kintsugi repairs
        kintsugi_notes = product.get('kintsugi_notes', [])
        if kintsugi_notes:
            insights.append(f"✨ {len(kintsugi_notes)} Kintsugi repairs applied to this product")
            insights.extend(kintsugi_notes[:3])  # Show first 3 notes
        
        # Count available fields
        field_count = len([v for v in product.values() if v is not None and str(v).strip()])
        insights.append(f"📋 {field_count} product attributes available")
        
        # Check for completeness
        essential_fields = ['Brand', 'Type', 'Price']
        missing_essential = [f for f in essential_fields if not product.get(f)]
        if missing_essential:
            insights.append(f"🔧 Missing essential info: {', '.join(missing_essential)}")
        else:
            insights.append("✅ All essential product information available")
        
        return insights
    
    def record_interaction(self, user_id: str, product_id: str, interaction_type: str = 'click') -> None:
        """
        Record user interaction with a product for recommendation purposes.
        
        Args:
            user_id (str): User identifier
            product_id (str): Product identifier
            interaction_type (str): Type of interaction (click, view, purchase, etc.)
        """
        # Initialize interaction storage if not exists
        if not hasattr(self, '_user_interactions'):
            self._user_interactions = {}
        
        if user_id not in self._user_interactions:
            self._user_interactions[user_id] = []
        
        # Record the interaction with timestamp
        import time
        interaction = {
            'product_id': str(product_id),
            'interaction_type': interaction_type,
            'timestamp': time.time()
        }
        
        self._user_interactions[user_id].append(interaction)
        
        # Keep only recent interactions (last 100 per user)
        if len(self._user_interactions[user_id]) > 100:
            self._user_interactions[user_id] = self._user_interactions[user_id][-100:]
        
        logger.info(f"Recorded {interaction_type} for user {user_id} on product {product_id}")
    
    def get_recommendations(self, user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get product recommendations for a user based on their interactions.
        
        Args:
            user_id (str): User identifier
            top_k (int): Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of recommended products
        """
        try:
            # Get user's interaction history
            if not hasattr(self, '_user_interactions') or user_id not in self._user_interactions:
                # No interactions yet, return popular/random products
                return self._get_popular_products(top_k)
            
            user_interactions = self._user_interactions[user_id]
            
            # Get products user has interacted with
            interacted_product_ids = set(interaction['product_id'] for interaction in user_interactions)
            
            # Simple content-based recommendations: find similar products
            recommendations = []
            all_products = self.parser.get_all_products(repaired=True)
            
            # Get products user hasn't interacted with yet
            candidate_products = [
                product for product in all_products 
                if product.get('id') not in interacted_product_ids
            ]
            
            # Score products based on similarity to user's interactions
            scored_products = []
            for product in candidate_products[:50]:  # Limit for performance
                score = self._calculate_recommendation_score(product, user_interactions)
                if score > 0:
                    scored_products.append({
                        'product': product,
                        'score': score,
                        'reason': 'Based on your viewing history'
                    })
            
            # Sort by score and return top K
            scored_products.sort(key=lambda x: x['score'], reverse=True)
            
            for item in scored_products[:top_k]:
                recommendations.append({
                    'id': item['product'].get('id'),
                    'product': item['product'],
                    'score': item['score'],
                    'reason': item['reason'],
                    'kintsugi_notes': item['product'].get('kintsugi_notes', [])
                })
            
            # If not enough recommendations, fill with popular products
            if len(recommendations) < top_k:
                popular = self._get_popular_products(top_k - len(recommendations))
                recommendations.extend(popular)
            
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return self._get_popular_products(top_k)
    
    def _calculate_recommendation_score(self, product: Dict[str, Any], user_interactions: List[Dict[str, Any]]) -> float:
        """
        Calculate recommendation score for a product based on user interactions.
        """
        score = 0.0
        
        # Simple scoring based on brand, type, and features similarity
        for interaction in user_interactions[-10:]:  # Consider last 10 interactions
            interacted_product = self.parser.get_product_by_id(interaction['product_id'], repaired=True)
            if not interacted_product:
                continue
            
            # Brand similarity
            if (product.get('Brand') and interacted_product.get('Brand') and 
                product['Brand'].lower() == interacted_product['Brand'].lower()):
                score += 0.3
            
            # Type similarity
            if (product.get('Type') and interacted_product.get('Type') and 
                product['Type'].lower() == interacted_product['Type'].lower()):
                score += 0.2
            
            # Feature similarity (basic text matching)
            if product.get('Features') and interacted_product.get('Features'):
                common_words = set(product['Features'].lower().split()) & set(interacted_product['Features'].lower().split())
                if common_words:
                    score += len(common_words) * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_popular_products(self, top_k: int) -> List[Dict[str, Any]]:
        """
        Get popular products as fallback recommendations.
        """
        all_products = self.parser.get_all_products(repaired=True)
        
        # Simple popularity: products with more complete information
        scored = []
        for product in all_products:
            completeness_score = len([v for v in product.values() if v is not None and str(v).strip()])
            scored.append({
                'id': product.get('id'),
                'product': product,
                'score': completeness_score / 10.0,  # Normalize
                'reason': 'Popular product',
                'kintsugi_notes': product.get('kintsugi_notes', [])
            })
        
        # Sort by completeness and return top K
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]
    
    def _determine_search_type(self, query: str) -> str:
        """
        Automatically determine the best search type for a query.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Recommended search type
        """
        # Analyze query characteristics
        query_lower = query.lower()
        
        # Check for exact match indicators
        if '"' in query:
            return "exact"
        
        # Check for fuzzy indicators
        if any(char in query for char in ['*', '?', '~']) or len(query.split()) > 3:
            return "fuzzy"
        
        # Check for common misspellings or variations
        if any(word in query_lower for word in ['colour', 'centre', 'organise']):
            return "fuzzy"
        
        # For single words, prefer fuzzy search to handle misspellings
        if len(query.split()) == 1:
            return "fuzzy"
        
        # Default to combined search for multi-word queries
        return "combined"
    
    def _exact_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform exact search."""
        exact_results = self.indexer.search_exact(query, field=None)
        
        # Convert to dict format
        results = []
        for doc_id, score in exact_results:
            results.append({
                'doc_id': doc_id,
                'score': score,
                'match_type': 'exact',
                'priority': 1
            })
        
        return results
    
    def _fuzzy_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform fuzzy search."""
        fuzzy_results = self.indexer.search_fuzzy(query, field=None, 
                                                threshold=self.search_config['fuzzy_threshold'])
        
        # Convert to dict format and limit results
        results = []
        for doc_id, score, match_type in fuzzy_results[:max_results * 2]:  # Limit fuzzy results
            results.append({
                'doc_id': doc_id,
                'score': score,
                'match_type': match_type,
                'priority': 2 if 'fuzzy' in match_type else 1
            })
        
        return results
    
    def _combined_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform combined exact and fuzzy search."""
        # Get exact results
        exact_results = self._exact_search(query, max_results)
        
        # Get fuzzy results
        fuzzy_results = self._fuzzy_search(query, max_results)
        
        # Combine and deduplicate
        combined = {}
        
        # Add exact results
        for result in exact_results:
            doc_id = result['doc_id']
            combined[doc_id] = result
        
        # Add fuzzy results (don't override exact matches)
        for result in fuzzy_results:
            doc_id = result['doc_id']
            if doc_id not in combined:
                combined[doc_id] = result
        
        # Sort by priority and score
        sorted_results = sorted(combined.values(), 
                              key=lambda x: (x['priority'], -x['score']))
        
        return sorted_results
    
    def _process_results(self, results: List[Any], query: str) -> List[Dict[str, Any]]:
        """
        Process search results with highlighting and Kintsugi metadata.
        
        Args:
            results: Raw search results
            query (str): Original query
            
        Returns:
            List[Dict[str, Any]]: Processed results
        """
        processed = []
        
        for result in results:
            if isinstance(result, tuple):
                # Handle different result formats
                if len(result) == 2:
                    doc_id, score = result
                    match_type = 'exact'
                else:
                    doc_id, score, match_type = result
            else:
                # Handle dict format
                doc_id = result['doc_id']
                score = result['score']
                match_type = result['match_type']
            
            # Get document
            document = self.indexer.get_document(doc_id)
            if not document:
                continue
            
            # Create searchable text
            searchable_text = self.preprocessor.create_searchable_text(document)
            
            # Find matches for highlighting
            matches = []
            if self.search_config['enable_highlighting']:
                matches = self.fuzzy_matcher.find_matches(query, searchable_text)
            
            # Create highlighted text
            highlighted_text = searchable_text
            if matches and self.search_config['enable_highlighting']:
                highlighted_text = self.fuzzy_matcher.highlight_matches(
                    searchable_text, matches)
            
            # Create result entry
            processed_result = {
                'doc_id': doc_id,
                'score': score,
                'match_type': match_type,
                'document': document,
                'searchable_text': searchable_text,
                'highlighted_text': highlighted_text,
                'matches': matches,
                'kintsugi_quality': self._get_kintsugi_quality(match_type, score)
            }
            
            processed.append(processed_result)
        
        return processed
    
    def _apply_enhanced_ranking(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Apply enhanced ranking using new features.
        
        Args:
            results: Processed search results
            query: Search query
            
        Returns:
            List[Dict[str, Any]]: Enhanced results with new ranking
        """
        enhanced_results = []
        
        for result in results:
            doc_id = result['doc_id']
            original_score = result['score']
            
            # Start with original score
            enhanced_score = original_score
            
            # Apply Polya Urn boosting
            if self.polya_urn:
                polya_score = self.polya_urn.get_product_probability(doc_id)
                if polya_score > 0:
                    enhanced_score *= (1 + polya_score * 0.1)  # 10% boost max
                    result['polya_boost'] = polya_score
            
            # Apply vector search enhancement
            if self.vector_engine:
                try:
                    vector_results = self.vector_engine.search(query, top_k=1)
                    if vector_results and vector_results[0]['doc_id'] == doc_id:
                        vector_score = vector_results[0]['score']
                        enhanced_score *= (1 + vector_score * 0.05)  # 5% boost max
                        result['vector_boost'] = vector_score
                except Exception as e:
                    logger.debug(f"Vector search failed: {e}")
            
            # Apply cascade boosting
            if self.cascade_model:
                try:
                    viral_products = self.cascade_model.get_viral_products(1000)  # Get all viral products
                    cascade_score = 0
                    for product_id, score, stats in viral_products:
                        if product_id == doc_id:
                            cascade_score = score
                            break
                    if cascade_score > 0:
                        enhanced_score *= (1 + cascade_score * 0.08)  # 8% boost max
                        result['cascade_boost'] = cascade_score
                except Exception as e:
                    logger.debug(f"Cascade scoring failed: {e}")
            
            # Apply PageRank boosting
            if self.pagerank_ranker:
                try:
                    pagerank_score = self.pagerank_ranker.get_product_rank(doc_id)
                    if pagerank_score > 0:
                        enhanced_score *= (1 + pagerank_score * 0.06)  # 6% boost max
                        result['pagerank_boost'] = pagerank_score
                except Exception as e:
                    logger.debug(f"PageRank scoring failed: {e}")
            
            # Update the result with enhanced score
            result['enhanced_score'] = enhanced_score
            result['original_score'] = original_score
            
            enhanced_results.append(result)
        
        # Sort by enhanced score
        enhanced_results.sort(key=lambda x: x['enhanced_score'], reverse=True)
        
        return enhanced_results
    
    def _process_results_with_improved_ranking(self, results: List[Any], query: str) -> List[Dict[str, Any]]:
        """
        Process search results with improved ranking logic that prioritizes:
        1. Exact phrase matches
        2. Products with highest match count
        3. All other scoring factors
        
        Args:
            results: Raw search results
            query (str): Original query
            
        Returns:
            List[Dict[str, Any]]: Processed results with improved ranking
        """
        processed = []
        query_tokens = self.preprocessor.tokenize(query)
        
        for result in results:
            if isinstance(result, tuple):
                # Handle different result formats
                if len(result) == 2:
                    doc_id, score = result
                    match_type = 'exact'
                else:
                    doc_id, score, match_type = result
            else:
                # Handle dict format
                doc_id = result['doc_id']
                score = result['score']
                match_type = result['match_type']
            
            # Get document
            document = self.indexer.get_document(doc_id)
            if not document:
                continue
            
            # Create searchable text
            searchable_text = self.preprocessor.create_searchable_text(document)
            
            # Apply improved ranking logic
            improved_score, match_count, has_exact_phrase = self._calculate_improved_score(
                query, query_tokens, document, searchable_text, score, match_type)
            
            # Enforce zero score for no matches
            if match_count == 0:
                improved_score = 0.0
            
            # Find matches for highlighting
            matches = []
            if self.search_config['enable_highlighting']:
                matches = self.fuzzy_matcher.find_matches(query, searchable_text)
            
            # Create highlighted text
            highlighted_text = searchable_text
            if matches and self.search_config['enable_highlighting']:
                highlighted_text = self.fuzzy_matcher.highlight_matches(
                    searchable_text, matches)
            
            # Create result entry
            processed_result = {
                'doc_id': doc_id,
                'score': improved_score,
                'original_score': score,
                'match_type': match_type,
                'match_count': match_count,
                'has_exact_phrase': has_exact_phrase,
                'document': document,
                'searchable_text': searchable_text,
                'highlighted_text': highlighted_text,
                'matches': matches,
                'kintsugi_quality': self._get_kintsugi_quality(match_type, improved_score)
            }
            
            processed.append(processed_result)
        
        # Filter: Remove any products with zero relevance score
        filtered_results = [result for result in processed if result['score'] > 0]
        
        # Sort: Sort the filtered list in descending order based on score
        filtered_results.sort(key=lambda x: -x['score'])
        
        return filtered_results
    
    def _calculate_improved_score(self, query: str, query_tokens: List[str], 
                                document: Dict[str, Any], searchable_text: str, 
                                original_score: float, match_type: str) -> Tuple[float, int, bool]:
        """
        Calculate improved score with exact phrase bonus and match count boost.
        
        Args:
            query (str): Original query
            query_tokens (List[str]): Tokenized query
            document (Dict[str, Any]): Document data
            searchable_text (str): Searchable text from document
            original_score (float): Original score from indexer
            match_type (str): Type of match
            
        Returns:
            Tuple[float, int, bool]: (improved_score, match_count, has_exact_phrase)
        """
        searchable_lower = searchable_text.lower()
        query_lower = query.lower()
        
        # 1. Check for exact phrase match (before tokenizing)
        has_exact_phrase = query_lower in searchable_lower
        exact_phrase_bonus = 0.0
        if has_exact_phrase:
            # Large bonus for exact phrase matches
            exact_phrase_bonus = 1000.0  # Very large bonus to ensure top ranking
        
        # 2. Count how many query terms are matched (including fuzzy matches)
        exact_match_count = 0
        fuzzy_match_count = 0
        
        for token in query_tokens:
            if token.lower() in searchable_lower:
                exact_match_count += 1
            else:
                # Check for fuzzy matches using the fuzzy matcher
                fuzzy_matches = self.fuzzy_matcher.find_matches(token, searchable_text, threshold=0.6)
                if fuzzy_matches:
                    fuzzy_match_count += 1
        
        total_match_count = exact_match_count + fuzzy_match_count
        
        # 3. Apply match count boost
        match_count_boost = 0.0
        if total_match_count > 0:
            # Exponential boost based on match count
            match_ratio = total_match_count / len(query_tokens)
            match_count_boost = original_score * (match_ratio ** 2) * 10  # Quadratic boost
        
        # 4. Calculate final improved score
        improved_score = original_score + exact_phrase_bonus + match_count_boost
        
        return improved_score, total_match_count, has_exact_phrase
    
    def _get_kintsugi_quality(self, match_type: str, score: float) -> str:
        """
        Determine Kintsugi quality based on match type and score.
        
        Args:
            match_type (str): Type of match
            score (float): Match score
            
        Returns:
            str: Kintsugi quality level
        """
        if match_type == 'exact' and score >= 0.9:
            return 'perfect'
        elif 'kintsugi_exact' in match_type and score >= 0.8:
            return 'excellent'
        elif 'kintsugi_near' in match_type and score >= 0.7:
            return 'good'
        elif 'kintsugi_fuzzy' in match_type and score >= 0.6:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_kintsugi_insights(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate Kintsugi-inspired insights about the search results.
        
        Args:
            results: List of search results
            
        Returns:
            str: Kintsugi insights
        """
        if not results:
            return "No results found - sometimes the most beautiful things are hidden in the cracks"
        
        # Analyze result types
        match_types = [r['match_type'] for r in results]
        qualities = [r['kintsugi_quality'] for r in results]
        
        insights = []
        
        if 'exact' in match_types:
            insights.append("Found perfect matches - no repair needed!")
        
        if any('kintsugi' in mt for mt in match_types):
            kintsugi_count = sum(1 for mt in match_types if 'kintsugi' in mt)
            insights.append(f"Found {kintsugi_count} Kintsugi matches - "
                          "imperfect queries reveal hidden treasures!")
        
        if 'excellent' in qualities or 'good' in qualities:
            insights.append("High-quality matches found - the golden seams are strong!")
        
        if 'fair' in qualities or 'poor' in qualities:
            insights.append("Some matches need more repair - but every crack tells a story!")
        
        if not insights:
            insights.append("Results found - every search is a journey of discovery!")
        
        return " | ".join(insights)
    
    def _create_empty_result(self, message: str) -> Dict[str, Any]:
        """Create an empty result with a message."""
        return {
            'query': '',
            'search_type': 'none',
            'total_results': 0,
            'results': [],
            'search_time': 0,
            'kintsugi_insights': message,
            'search_metadata': {
                'index_stats': self.indexer.get_index_stats(),
                'config': self.search_config
            }
        }
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific product by its ID.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            Optional[Dict[str, Any]]: Product data if found
        """
        return self.parser.get_product_by_id(product_id)
    
    def get_field_suggestions(self, field_name: str, limit: int = 10) -> List[str]:
        """
        Get suggestions for a specific field.
        
        Args:
            field_name (str): Field name
            limit (int): Maximum number of suggestions
            
        Returns:
            List[str]: List of field values
        """
        values = list(self.parser.get_field_values(field_name))
        return sorted(values)[:limit]
    
    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query.
        
        Args:
            partial_query (str): Partial search query
            limit (int): Maximum number of suggestions
            
        Returns:
            List[str]: List of suggestions
        """
        if not partial_query or len(partial_query) < 2:
            return []
        
        # Get all terms from the index
        all_terms = set(self.indexer.term_to_docs.keys())
        
        # Find similar terms
        similar_terms = self.fuzzy_matcher.find_similar_terms(
            [partial_query], all_terms, threshold=0.6)
        
        # Sort by similarity and return top suggestions
        suggestions = [term for term, _ in similar_terms[:limit]]
        return suggestions
    
    def update_config(self, **kwargs) -> None:
        """
        Update search configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        self.search_config.update(kwargs)
        logger.info(f"Updated search config: {kwargs}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get search engine statistics.
        
        Returns:
            Dict[str, Any]: Statistics about the search engine
        """
        parser_stats = self.parser.get_stats()
        index_stats = self.indexer.get_index_stats()
        
        return {
            'parser_stats': parser_stats,
            'index_stats': index_stats,
            'search_config': self.search_config,
            'components': {
                'parser': 'ECommerceDataParser',
                'preprocessor': 'TextPreprocessor',
                'indexer': 'InvertedIndex',
                'fuzzy_matcher': 'KintsugiFuzzyMatcher',
                'formatter': 'KintsugiResultFormatter'
            }
        }
    
    def get_recommendations(self, user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get recommendations for a user using enhanced features.
        
        Args:
            user_id (str): User identifier
            top_k (int): Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of recommended products
        """
        recommendations = []
        
        # Get products from parser
        products = self.parser.get_all_products()
        
        # Get Polya Urn boosted products
        if self.polya_urn:
            try:
                boosted_products = self.polya_urn.get_boosted_products(top_k)
                for product_id, score, stats in boosted_products:
                    if product_id < len(products):
                        product = products[product_id]
                        # Extract available fields from product data
                        brand = product.get('Brand', '')
                        product_type = product.get('Type', '')
                        model_name = product.get('Model Name', '')
                        model_number = product.get('Model Number', '')
                        price = product.get('Price', product.get('Weight', 'N/A'))
                        
                        # Create concise title from available fields
                        title_parts = []
                        if brand:
                            title_parts.append(brand)
                        elif model_name and len(model_name) < 50:  # Use model name if not too long
                            title_parts.append(model_name)
                        elif model_number:
                            title_parts.append(model_number)
                        
                        if product_type:
                            title_parts.append(product_type)
                        
                        title = ' '.join(title_parts).strip()
                        if not title:
                            title = f"Product {product.get('id', product_id)}"
                        
                        recommendations.append({
                            'id': product.get('id', str(product_id)),
                            'product_id': product.get('id', str(product_id)),
                            'title': title,
                            'brand': brand,
                            'type': product_type,
                            'price': price,
                            'features': product.get('Features', product.get('Other Features', '')),
                            'recommendation_score': score,
                            'recommendation_reason': f'Trending (clicks: {stats.get("total_clicks", 0)})',
                            'kintsugi_quality': 'excellent'
                        })
            except Exception as e:
                logger.debug(f"Polya Urn recommendations failed: {e}")
        
        # Get viral products from cascade
        if self.cascade_model and len(recommendations) < top_k:
            try:
                viral_products = self.cascade_model.get_viral_products(top_k - len(recommendations))
                for product_id, score, stats in viral_products:
                    if product_id < len(products):
                        product = products[product_id]
                        # Extract available fields from product data
                        brand = product.get('Brand', '')
                        product_type = product.get('Type', '')
                        model_name = product.get('Model Name', '')
                        model_number = product.get('Model Number', '')
                        price = product.get('Price', product.get('Weight', 'N/A'))
                        
                        # Create concise title from available fields
                        title_parts = []
                        if brand:
                            title_parts.append(brand)
                        elif model_name and len(model_name) < 50:  # Use model name if not too long
                            title_parts.append(model_name)
                        elif model_number:
                            title_parts.append(model_number)
                        
                        if product_type:
                            title_parts.append(product_type)
                        
                        title = ' '.join(title_parts).strip()
                        if not title:
                            title = f"Product {product.get('id', product_id)}"
                        
                        recommendations.append({
                            'id': product.get('id', str(product_id)),
                            'product_id': product.get('id', str(product_id)),
                            'title': title,
                            'brand': brand,
                            'type': product_type,
                            'price': price,
                            'features': product.get('Features', product.get('Other Features', '')),
                            'recommendation_score': score,
                            'recommendation_reason': f'Viral (adoptions: {stats.get("adoption_count", 0)})',
                            'kintsugi_quality': 'excellent'
                        })
            except Exception as e:
                logger.debug(f"Cascade recommendations failed: {e}")
        
        # Fill remaining with popular products if needed
        if len(recommendations) < top_k:
            for product in products[:top_k * 2]:
                if len(recommendations) >= top_k:
                    break
                # Check if product has any meaningful data
                if product.get('Brand') or product.get('Type') or product.get('Model Name') or product.get('Model Number'):
                    # Extract available fields from product data
                    brand = product.get('Brand', product.get('Model Name', product.get('Model Number', '')))
                    product_type = product.get('Type', product.get('Model Name', product.get('Model Number', '')))
                    price = product.get('Price', product.get('Weight', 'N/A'))
                    
                    # Create title from available fields
                    title_parts = [brand, product_type]
                    title = ' '.join([part for part in title_parts if part]).strip()
                    if not title:
                        title = f"Product {product.get('id', i)}"
                    
                    recommendations.append({
                        'id': product.get('id', str(i)),
                        'product_id': product.get('id', ''),
                        'title': title,
                        'brand': brand,
                        'type': product_type,
                        'price': price,
                        'features': product.get('Features', product.get('Other Features', '')),
                        'recommendation_score': 0.8,
                        'recommendation_reason': 'Popular product',
                        'kintsugi_quality': 'good'
                    })
        
        return recommendations[:top_k]
    
    def record_interaction(self, user_id: str, product_id: str, interaction_type: str) -> None:
        """
        Record user interaction with a product.
        
        Args:
            user_id (str): User identifier
            product_id (str): Product identifier
            interaction_type (str): Type of interaction (click, view, etc.)
        """
        # Simple interaction tracking
        logger.info(f"User {user_id} {interaction_type}ed product {product_id}")
        
        # Record in Polya Urn Model
        if self.polya_urn and interaction_type == 'click':
            try:
                product_id_int = int(product_id) if product_id.isdigit() else hash(product_id) % 10000
                self.polya_urn.record_click(product_id_int, user_id)
                logger.debug(f"Recorded click in Polya Urn: product {product_id_int}")
            except Exception as e:
                logger.debug(f"Polya Urn recording failed: {e}")
        
        # Record in Cascade Model
        if self.cascade_model and interaction_type in ['click', 'purchase']:
            try:
                product_id_int = int(product_id) if product_id.isdigit() else hash(product_id) % 10000
                self.cascade_model.record_adoption(user_id, product_id_int)
                logger.debug(f"Recorded adoption in Cascade: product {product_id_int}")
            except Exception as e:
                logger.debug(f"Cascade recording failed: {e}")
    
    def search_and_display(self, query: str, search_type: str = "auto", 
                          max_results: int = 20) -> None:
        """
        Perform a search and display results in a clean, formatted way.
        
        Args:
            query (str): Search query
            search_type (str): Type of search ("exact", "fuzzy", "auto")
            max_results (int): Maximum number of results to display
        """
        results = self.search(query, search_type=search_type, max_results=max_results)
        
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 60)
        print(f"📊 Found {results['total_results']} unique results in {results['search_time']:.3f}s")
        print(f"🎨 {results['kintsugi_insights']}")
        
        # Display formatted results
        self.formatter.print_formatted_results(results['raw_results'], query, max_results)


def main():
    """
    Demo function to test the search engine.
    """
    try:
        # Initialize search engine
        print("=== Kintsugi Search Engine Demo ===")
        print("Initializing search engine...")
        
        search_engine = KintsugiSearchEngine('../data-set.json')
        
        # Get basic stats
        stats = search_engine.get_stats()
        print(f"Loaded {stats['parser_stats']['total_products']} products")
        print(f"Indexed {stats['index_stats']['total_terms']} terms")
        
        # Test searches
        test_queries = [
            "iPhone",
            "samsng galaxy",  # Misspelled
            "noise cancelling headphones",
            "laptop i7 16gb",
            "nike shoes size 10"
        ]
        
        print("\n=== Testing Search Queries ===")
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = search_engine.search(query, max_results=3)
            
            print(f"Found {results['total_results']} results in {results['search_time']:.3f}s")
            print(f"Insights: {results['kintsugi_insights']}")
            
            for i, result in enumerate(results['results'][:2]):  # Show top 2
                print(f"  {i+1}. Score: {result['score']:.2f}, Type: {result['match_type']}")
                print(f"     Quality: {result['kintsugi_quality']}")
                if result['highlighted_text']:
                    print(f"     Text: {result['highlighted_text'][:100]}...")
        
    except Exception as e:
        print(f"Error in search engine demo: {e}")


if __name__ == "__main__":
    main()
