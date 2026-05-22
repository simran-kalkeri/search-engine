"""
Comprehensive Recommendation Engine
==================================

This module implements a comprehensive recommendation system that combines:
- Content-based filtering using product features and embeddings
- Collaborative filtering using user behavior patterns
- Polya Urn Model for click-based boosting
- Granovetter Threshold Cascade for viral recommendations
- Kintsugi-inspired repair and enhancement

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import random
import math
import time
import re
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

# Import our custom modules
from polya_urn_model import PolyaUrnModel, PolyaUrnRecommendationEngine
from granovetter_cascade import GranovetterCascadeModel
from vector_search import VectorSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """
    Content-based recommendation system using product features and embeddings.
    
    This class implements content-based filtering by analyzing product features,
    descriptions, and specifications to find similar products.
    """
    
    def __init__(self, vector_engine: VectorSearchEngine):
        """
        Initialize the content-based recommender.
        
        Args:
            vector_engine (VectorSearchEngine): Vector search engine for embeddings
        """
        self.vector_engine = vector_engine
        self.product_features = {}  # product_id -> feature_vector
        self.feature_weights = {}  # feature -> weight
        
    def extract_features(self, product: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from a product for content-based filtering.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            Dict[str, float]: Feature vector
        """
        features = {}
        
        # Brand features
        brand = product.get('Brand', '').lower().strip()
        if brand:
            features[f'brand_{brand}'] = 1.0
        
        # Type/Category features
        product_type = product.get('Type', '').lower().strip()
        if product_type:
            features[f'type_{product_type}'] = 1.0
        
        # Price features
        price = self._extract_price(product)
        if price is not None:
            price_range = self._get_price_range(price)
            features[f'price_{price_range}'] = 1.0
            features['price_value'] = price / 1000.0  # Normalized price
        
        # Feature keywords
        feature_text = self._extract_feature_text(product)
        if feature_text:
            # Use vector engine to get embeddings
            embedding = self.vector_engine._generate_embedding(feature_text)
            # Convert embedding to feature dict
            for i, val in enumerate(embedding[:50]):  # Use first 50 dimensions
                features[f'embedding_{i}'] = float(val)
        
        # Technical specifications
        specs = self._extract_specifications(product)
        for spec in specs:
            features[f'spec_{spec}'] = 1.0
        
        return features
    
    def _extract_price(self, product: Dict[str, Any]) -> Optional[float]:
        """Extract price from product data."""
        price_field = product.get('Price', '')
        if not price_field:
            return None
        
        # Extract numeric value from price string
        import re
        price_match = re.search(r'[\d,]+\.?\d*', str(price_field))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                return None
        
        return None
    
    def _get_price_range(self, price: float) -> str:
        """Get price range category."""
        if price < 100:
            return 'budget'
        elif price < 500:
            return 'mid'
        elif price < 1000:
            return 'premium'
        else:
            return 'luxury'
    
    def _extract_feature_text(self, product: Dict[str, Any]) -> str:
        """Extract feature text from product."""
        feature_fields = ['Features', 'Key Features', 'Other Features', 'Description']
        texts = []
        
        for field in feature_fields:
            if field in product and product[field]:
                texts.append(str(product[field]))
        
        return ' '.join(texts)
    
    def _extract_specifications(self, product: Dict[str, Any]) -> List[str]:
        """Extract technical specifications."""
        specs = []
        
        # Look for common specification patterns
        spec_patterns = [
            r'(\d+)\s*gb',  # Storage
            r'(\d+)\s*inch',  # Screen size
            r'(\d+)\s*mah',  # Battery
            r'(\d+)\s*mp',  # Camera
            r'(\d+)\s*ghz',  # Processor speed
            r'(\d+)\s*gb\s*ram',  # RAM
        ]
        
        text = ' '.join(str(v) for v in product.values() if isinstance(v, str)).lower()
        
        for pattern in spec_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                specs.append(f"{match} {pattern.split('(')[1].split(')')[0]}")
        
        return specs
    
    def get_similar_products(self, product_id: int, top_k: int = 10) -> List[Tuple[int, float, str]]:
        """
        Get products similar to a given product.
        
        Args:
            product_id (int): Product ID to find similar items for
            top_k (int): Number of similar products to return
            
        Returns:
            List[Tuple[int, float, str]]: List of (product_id, similarity, reason)
        """
        if product_id not in self.product_features:
            return []
        
        target_features = self.product_features[product_id]
        similarities = []
        
        for other_id, other_features in self.product_features.items():
            if other_id == product_id:
                continue
            
            similarity = self._calculate_similarity(target_features, other_features)
            if similarity > 0.1:  # Minimum similarity threshold
                similarities.append((other_id, similarity, "content_similar"))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _calculate_similarity(self, features1: Dict[str, float], 
                            features2: Dict[str, float]) -> float:
        """Calculate cosine similarity between feature vectors."""
        # Get common features
        common_features = set(features1.keys()) & set(features2.keys())
        
        if not common_features:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = sum(features1[f] * features2[f] for f in common_features)
        norm1 = math.sqrt(sum(f**2 for f in features1.values()))
        norm2 = math.sqrt(sum(f**2 for f in features2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def add_product(self, product_id: int, product: Dict[str, Any]) -> None:
        """Add a product to the content-based system."""
        features = self.extract_features(product)
        self.product_features[product_id] = features


class CollaborativeFilteringRecommender:
    """
    Collaborative filtering recommendation system.
    
    This class implements user-based collaborative filtering by finding
    users with similar preferences and recommending products they liked.
    """
    
    def __init__(self):
        """Initialize the collaborative filtering recommender."""
        self.user_item_matrix = defaultdict(dict)  # user_id -> {product_id: rating}
        self.item_user_matrix = defaultdict(set)  # product_id -> set of user_ids
        self.user_similarities = {}  # (user1, user2) -> similarity
        self.item_similarities = {}  # (item1, item2) -> similarity
    
    def add_rating(self, user_id: str, product_id: int, rating: float) -> None:
        """
        Add a user rating for a product.
        
        Args:
            user_id (str): User identifier
            product_id (int): Product identifier
            rating (float): Rating (0.0-5.0)
        """
        self.user_item_matrix[user_id][product_id] = rating
        self.item_user_matrix[product_id].add(user_id)
        
        # Clear cached similarities
        self._clear_user_similarities(user_id)
        self._clear_item_similarities(product_id)
    
    def _clear_user_similarities(self, user_id: str) -> None:
        """Clear cached similarities for a user."""
        keys_to_remove = [k for k in self.user_similarities.keys() if user_id in k]
        for key in keys_to_remove:
            del self.user_similarities[key]
    
    def _clear_item_similarities(self, product_id: int) -> None:
        """Clear cached similarities for an item."""
        keys_to_remove = [k for k in self.item_similarities.keys() if product_id in k]
        for key in keys_to_remove:
            del self.item_similarities[key]
    
    def get_user_similarity(self, user1: str, user2: str) -> float:
        """
        Calculate similarity between two users.
        
        Args:
            user1 (str): First user ID
            user2 (str): Second user ID
            
        Returns:
            float: Similarity score (0.0-1.0)
        """
        if user1 == user2:
            return 1.0
        
        # Check cache
        cache_key = tuple(sorted([user1, user2]))
        if cache_key in self.user_similarities:
            return self.user_similarities[cache_key]
        
        # Calculate similarity
        user1_items = set(self.user_item_matrix[user1].keys())
        user2_items = set(self.user_item_matrix[user2].keys())
        
        common_items = user1_items & user2_items
        
        if len(common_items) < 2:
            similarity = 0.0
        else:
            # Calculate Pearson correlation
            ratings1 = [self.user_item_matrix[user1][item] for item in common_items]
            ratings2 = [self.user_item_matrix[user2][item] for item in common_items]
            
            similarity = self._pearson_correlation(ratings1, ratings2)
            similarity = max(0.0, similarity)  # Ensure non-negative
        
        # Cache result
        self.user_similarities[cache_key] = similarity
        return similarity
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def get_recommendations(self, user_id: str, top_k: int = 10) -> List[Tuple[int, float, str]]:
        """
        Get recommendations for a user using collaborative filtering.
        
        Args:
            user_id (str): User ID
            top_k (int): Number of recommendations to return
            
        Returns:
            List[Tuple[int, float, str]]: List of (product_id, score, reason)
        """
        if user_id not in self.user_item_matrix:
            return []
        
        user_items = set(self.user_item_matrix[user_id].keys())
        recommendations = []
        
        # Find similar users
        similar_users = self._find_similar_users(user_id, min_similarity=0.1)
        
        for similar_user, similarity in similar_users:
            similar_user_items = self.user_item_matrix[similar_user]
            
            for product_id, rating in similar_user_items.items():
                if product_id not in user_items:
                    # Predict rating for this product
                    predicted_rating = self._predict_rating(user_id, product_id, similar_users)
                    
                    if predicted_rating > 0:
                        recommendations.append((
                            product_id, 
                            predicted_rating, 
                            f"collaborative_{similarity:.2f}"
                        ))
        
        # Sort by predicted rating
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def _find_similar_users(self, user_id: str, min_similarity: float = 0.1) -> List[Tuple[str, float]]:
        """Find users similar to the given user."""
        similar_users = []
        
        for other_user in self.user_item_matrix.keys():
            if other_user != user_id:
                similarity = self.get_user_similarity(user_id, other_user)
                if similarity >= min_similarity:
                    similar_users.append((other_user, similarity))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:20]  # Limit to top 20 similar users
    
    def _predict_rating(self, user_id: str, product_id: int, 
                       similar_users: List[Tuple[str, float]]) -> float:
        """Predict rating for a product based on similar users."""
        if not similar_users:
            return 0.0
        
        # Calculate weighted average rating
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for similar_user, similarity in similar_users:
            if product_id in self.user_item_matrix[similar_user]:
                rating = self.user_item_matrix[similar_user][product_id]
                weighted_sum += similarity * rating
                weight_sum += similarity
        
        if weight_sum == 0:
            return 0.0
        
        return weighted_sum / weight_sum


class KintsugiRecommendationEngine:
    """
    Comprehensive recommendation engine integrating all components.
    
    This class combines content-based filtering, collaborative filtering,
    Polya Urn Model, and Granovetter Cascade Model to provide comprehensive
    recommendations with Kintsugi-inspired repair and enhancement.
    """
    
    def __init__(self, vector_engine: VectorSearchEngine):
        """
        Initialize the comprehensive recommendation engine.
        
        Args:
            vector_engine (VectorSearchEngine): Vector search engine
        """
        self.vector_engine = vector_engine
        
        # Initialize components
        self.content_recommender = ContentBasedRecommender(vector_engine)
        self.collaborative_recommender = CollaborativeFilteringRecommender()
        self.polya_urn = PolyaUrnModel()
        self.cascade_model = GranovetterCascadeModel()
        
        # Product database
        self.products = {}  # product_id -> product_data
        self.user_profiles = defaultdict(dict)  # user_id -> profile
        
        # Kintsugi metadata
        self.kintsugi_notes = []
        self.repair_history = []
    
    def add_product(self, product_id: int, product: Dict[str, Any]) -> None:
        """
        Add a product to the recommendation system.
        
        Args:
            product_id (int): Product identifier
            product (Dict[str, Any]): Product data
        """
        self.products[product_id] = product
        
        # Add to content-based system
        self.content_recommender.add_product(product_id, product)
        
        # Add to Polya Urn
        self.polya_urn.add_product(product_id)
        
        # Add to cascade model
        self.cascade_model.add_product(product_id)
        
        self.kintsugi_notes.append(f"✨ Added product {product_id} to recommendation system")
    
    def add_user(self, user_id: str, profile: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a user to the recommendation system.
        
        Args:
            user_id (str): User identifier
            profile (Optional[Dict[str, Any]]): User profile data
        """
        if profile is None:
            profile = {}
        
        self.user_profiles[user_id] = profile
        self.cascade_model.add_user(user_id)
        
        self.kintsugi_notes.append(f"👤 Added user {user_id} to recommendation system")
    
    def record_interaction(self, user_id: str, product_id: int, 
                          interaction_type: str = "click", 
                          rating: Optional[float] = None) -> None:
        """
        Record a user interaction with a product.
        
        Args:
            user_id (str): User identifier
            product_id (int): Product identifier
            interaction_type (str): Type of interaction (click, view, purchase, etc.)
            rating (Optional[float]): User rating (0.0-5.0)
        """
        # Add user if not present
        if user_id not in self.user_profiles:
            self.add_user(user_id)
        
        # Record in Polya Urn
        if interaction_type in ["click", "purchase"]:
            self.polya_urn.record_click(product_id, user_id)
        
        # Record in cascade model
        if interaction_type in ["purchase", "adoption"]:
            self.cascade_model.record_adoption(user_id, product_id)
        
        # Record rating for collaborative filtering
        if rating is not None:
            self.collaborative_recommender.add_rating(user_id, product_id, rating)
        
        # Update user profile
        if 'interactions' not in self.user_profiles[user_id]:
            self.user_profiles[user_id]['interactions'] = []
        
        self.user_profiles[user_id]['interactions'].append({
            'product_id': product_id,
            'type': interaction_type,
            'rating': rating,
            'timestamp': time.time()
        })
        
        # Add Kintsugi note
        self.kintsugi_notes.append(
            f"🔧 User {user_id} {interaction_type}ed product {product_id}"
        )
    
    def get_recommendations(self, user_id: str, top_k: int = 10, 
                          blend_weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Get comprehensive recommendations for a user.
        
        Args:
            user_id (str): User identifier
            top_k (int): Number of recommendations to return
            blend_weights (Optional[Dict[str, float]]): Weights for blending different methods
            
        Returns:
            List[Dict[str, Any]]: List of recommendation dictionaries
        """
        if blend_weights is None:
            blend_weights = {
                'content': 0.3,
                'collaborative': 0.2,
                'polya_urn': 0.2,
                'cascade': 0.2,
                'trending': 0.1
            }
        
        # Get recommendations from each method
        content_recs = self._get_content_recommendations(user_id, top_k * 2)
        collaborative_recs = self._get_collaborative_recommendations(user_id, top_k * 2)
        polya_recs = self._get_polya_recommendations(user_id, top_k * 2)
        cascade_recs = self._get_cascade_recommendations(user_id, top_k * 2)
        trending_recs = self._get_trending_recommendations(top_k * 2)
        
        # Blend recommendations
        blended_recs = self._blend_recommendations(
            content_recs, collaborative_recs, polya_recs, 
            cascade_recs, trending_recs, blend_weights
        )
        
        # Add Kintsugi metadata
        for rec in blended_recs:
            rec['kintsugi_metadata'] = self._generate_kintsugi_metadata(rec)
        
        return blended_recs[:top_k]
    
    def _get_content_recommendations(self, user_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Get content-based recommendations."""
        # Get user's interaction history
        user_interactions = self.user_profiles.get(user_id, {}).get('interactions', [])
        
        if not user_interactions:
            return []
        
        # Get similar products to recently interacted items
        similar_products = set()
        for interaction in user_interactions[-5:]:  # Last 5 interactions
            product_id = interaction['product_id']
            similar = self.content_recommender.get_similar_products(product_id, 5)
            similar_products.update(similar)
        
        # Convert to recommendation format
        recommendations = []
        for product_id, similarity, reason in similar_products:
            if product_id in self.products:
                recommendations.append({
                    'product_id': product_id,
                    'score': similarity,
                    'method': 'content',
                    'reason': reason,
                    'product': self.products[product_id]
                })
        
        return recommendations[:top_k]
    
    def _get_collaborative_recommendations(self, user_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations."""
        recs = self.collaborative_recommender.get_recommendations(user_id, top_k)
        
        recommendations = []
        for product_id, score, reason in recs:
            if product_id in self.products:
                recommendations.append({
                    'product_id': product_id,
                    'score': score,
                    'method': 'collaborative',
                    'reason': reason,
                    'product': self.products[product_id]
                })
        
        return recommendations
    
    def _get_polya_recommendations(self, user_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Get Polya Urn recommendations."""
        # Get all product IDs
        all_products = list(self.products.keys())
        
        # Get personalized recommendations
        recs = self.polya_urn.get_recommendation_weights(all_products)
        
        # Convert to recommendation format
        recommendations = []
        for product_id, weight in recs.items():
            if weight > 0 and product_id in self.products:
                recommendations.append({
                    'product_id': product_id,
                    'score': weight,
                    'method': 'polya_urn',
                    'reason': 'click_boosted',
                    'product': self.products[product_id]
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_k]
    
    def _get_cascade_recommendations(self, user_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Get cascade-based recommendations."""
        viral_products = self.cascade_model.get_viral_products(top_k)
        
        recommendations = []
        for product_id, score, stats in viral_products:
            if product_id in self.products:
                recommendations.append({
                    'product_id': product_id,
                    'score': score,
                    'method': 'cascade',
                    'reason': 'viral' if stats['is_viral'] else 'trending',
                    'product': self.products[product_id],
                    'cascade_stats': stats
                })
        
        return recommendations
    
    def _get_trending_recommendations(self, top_k: int) -> List[Dict[str, Any]]:
        """Get trending recommendations."""
        # Get most clicked products
        boosted_products = self.polya_urn.get_boosted_products(top_k)
        
        recommendations = []
        for product_id, score, stats in boosted_products:
            if product_id in self.products:
                recommendations.append({
                    'product_id': product_id,
                    'score': score,
                    'method': 'trending',
                    'reason': 'popular',
                    'product': self.products[product_id],
                    'trending_stats': stats
                })
        
        return recommendations
    
    def _blend_recommendations(self, content_recs: List[Dict[str, Any]], 
                             collaborative_recs: List[Dict[str, Any]],
                             polya_recs: List[Dict[str, Any]],
                             cascade_recs: List[Dict[str, Any]],
                             trending_recs: List[Dict[str, Any]],
                             weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Blend recommendations from different methods."""
        # Create a mapping of product_id to recommendation
        product_recs = {}
        
        # Add recommendations from each method
        for rec in content_recs:
            product_id = rec['product_id']
            if product_id not in product_recs:
                product_recs[product_id] = rec.copy()
                product_recs[product_id]['blended_score'] = 0.0
                product_recs[product_id]['methods'] = []
            
            product_recs[product_id]['blended_score'] += rec['score'] * weights['content']
            product_recs[product_id]['methods'].append('content')
        
        for rec in collaborative_recs:
            product_id = rec['product_id']
            if product_id not in product_recs:
                product_recs[product_id] = rec.copy()
                product_recs[product_id]['blended_score'] = 0.0
                product_recs[product_id]['methods'] = []
            
            product_recs[product_id]['blended_score'] += rec['score'] * weights['collaborative']
            product_recs[product_id]['methods'].append('collaborative')
        
        for rec in polya_recs:
            product_id = rec['product_id']
            if product_id not in product_recs:
                product_recs[product_id] = rec.copy()
                product_recs[product_id]['blended_score'] = 0.0
                product_recs[product_id]['methods'] = []
            
            product_recs[product_id]['blended_score'] += rec['score'] * weights['polya_urn']
            product_recs[product_id]['methods'].append('polya_urn')
        
        for rec in cascade_recs:
            product_id = rec['product_id']
            if product_id not in product_recs:
                product_recs[product_id] = rec.copy()
                product_recs[product_id]['blended_score'] = 0.0
                product_recs[product_id]['methods'] = []
            
            product_recs[product_id]['blended_score'] += rec['score'] * weights['cascade']
            product_recs[product_id]['methods'].append('cascade')
        
        for rec in trending_recs:
            product_id = rec['product_id']
            if product_id not in product_recs:
                product_recs[product_id] = rec.copy()
                product_recs[product_id]['blended_score'] = 0.0
                product_recs[product_id]['methods'] = []
            
            product_recs[product_id]['blended_score'] += rec['score'] * weights['trending']
            product_recs[product_id]['methods'].append('trending')
        
        # Convert to list and sort by blended score
        blended_recs = list(product_recs.values())
        blended_recs.sort(key=lambda x: x['blended_score'], reverse=True)
        
        return blended_recs
    
    def _generate_kintsugi_metadata(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Kintsugi metadata for a recommendation."""
        methods = recommendation.get('methods', [])
        score = recommendation.get('blended_score', 0.0)
        
        # Determine Kintsugi quality
        if score > 0.8:
            quality = 'excellent'
        elif score > 0.6:
            quality = 'good'
        elif score > 0.4:
            quality = 'fair'
        else:
            quality = 'poor'
        
        # Generate repair notes
        repair_notes = []
        if 'content' in methods:
            repair_notes.append("✨ Content similarity detected")
        if 'collaborative' in methods:
            repair_notes.append("👥 User behavior pattern matched")
        if 'polya_urn' in methods:
            repair_notes.append("🎯 Click-boosted popularity")
        if 'cascade' in methods:
            repair_notes.append("🌊 Viral cascade effect")
        if 'trending' in methods:
            repair_notes.append("📈 Trending popularity")
        
        return {
            'quality': quality,
            'repair_notes': repair_notes,
            'methods_used': methods,
            'blended_score': score
        }
    
    def get_kintsugi_insights(self) -> List[str]:
        """Get Kintsugi insights about the recommendation system."""
        insights = []
        
        total_products = len(self.products)
        total_users = len(self.user_profiles)
        
        if total_products > 0:
            insights.append(f"📦 {total_products} products in recommendation system")
        
        if total_users > 0:
            insights.append(f"👥 {total_users} users with profiles")
        
        # Get insights from components
        polya_insights = self.polya_urn.get_kintsugi_insights()
        cascade_insights = self.cascade_model.get_kintsugi_insights()
        
        insights.extend(polya_insights)
        insights.extend(cascade_insights)
        
        return insights
    
    def save_model(self, filepath: str) -> None:
        """Save the recommendation model to file."""
        data = {
            'products': self.products,
            'user_profiles': dict(self.user_profiles),
            'kintsugi_notes': self.kintsugi_notes,
            'repair_history': self.repair_history
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save component models
        self.polya_urn.save_model(filepath.replace('.json', '_polya_urn.json'))
        self.cascade_model.save_model(filepath.replace('.json', '_cascade.json'))
        
        logger.info(f"Recommendation model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load the recommendation model from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.products = data['products']
        self.user_profiles = defaultdict(dict, data['user_profiles'])
        self.kintsugi_notes = data.get('kintsugi_notes', [])
        self.repair_history = data.get('repair_history', [])
        
        # Load component models
        try:
            self.polya_urn.load_model(filepath.replace('.json', '_polya_urn.json'))
            self.cascade_model.load_model(filepath.replace('.json', '_cascade.json'))
        except FileNotFoundError:
            logger.warning("Component model files not found, using empty models")
        
        logger.info(f"Recommendation model loaded from {filepath}")


def main():
    """Demo function to test the recommendation engine."""
    print("=== Kintsugi Recommendation Engine Demo ===")
    
    # Create vector engine
    vector_engine = VectorSearchEngine()
    
    # Create recommendation engine
    rec_engine = KintsugiRecommendationEngine(vector_engine)
    
    # Add some sample products
    sample_products = [
        {'id': 1, 'Brand': 'Apple', 'Type': 'Smartphone', 'Price': '999', 'Features': 'iPhone 14 Pro'},
        {'id': 2, 'Brand': 'Samsung', 'Type': 'Smartphone', 'Price': '899', 'Features': 'Galaxy S23'},
        {'id': 3, 'Brand': 'Sony', 'Type': 'Headphones', 'Price': '299', 'Features': 'Noise Cancelling'},
        {'id': 4, 'Brand': 'Apple', 'Type': 'Laptop', 'Price': '1299', 'Features': 'MacBook Pro'},
        {'id': 5, 'Brand': 'Dell', 'Type': 'Laptop', 'Price': '799', 'Features': 'Gaming Laptop'}
    ]
    
    for product in sample_products:
        rec_engine.add_product(product['id'], product)
    
    # Add users and simulate interactions
    for i in range(1, 6):
        user_id = f"user_{i}"
        rec_engine.add_user(user_id)
        
        # Simulate some interactions
        for j in range(3):
            product_id = random.randint(1, 5)
            rec_engine.record_interaction(user_id, product_id, "click")
    
    # Get recommendations for a user
    recommendations = rec_engine.get_recommendations("user_1", top_k=3)
    
    print("\nRecommendations for user_1:")
    for rec in recommendations:
        print(f"  Product {rec['product_id']}: {rec['product']['Brand']} {rec['product']['Type']}")
        print(f"    Score: {rec['blended_score']:.3f}, Methods: {rec['methods']}")
        print(f"    Kintsugi: {rec['kintsugi_metadata']['quality']}")
    
    # Get insights
    insights = rec_engine.get_kintsugi_insights()
    print("\nKintsugi insights:")
    for insight in insights:
        print(f"  {insight}")


if __name__ == "__main__":
    main()
