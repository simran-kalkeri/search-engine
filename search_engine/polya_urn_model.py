"""
Polya Urn Model for Click-Based Boosting
========================================

This module implements the Polya Urn Model for boosting product scores based on
user clicks and interactions. The model simulates an urn where each click adds
more balls of the same color (product), making it more likely to be drawn again.

This embodies the Kintsugi concept by treating each click as a "repair" that
makes the product more valuable and visible.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import random
import math
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolyaUrnModel:
    """
    Polya Urn Model for click-based product boosting.
    
    This class implements a probabilistic model where each product click
    increases the likelihood of that product being recommended again,
    simulating the "rich get richer" phenomenon in a controlled way.
    """
    
    def __init__(self, initial_balls: int = 1, boost_factor: float = 1.0):
        """
        Initialize the Polya Urn Model.
        
        Args:
            initial_balls (int): Initial number of balls for each product
            boost_factor (float): Factor by which to boost balls on each click
        """
        self.initial_balls = initial_balls
        self.boost_factor = boost_factor
        self.urn = {}  # product_id -> number of balls
        self.click_history = []  # List of (product_id, timestamp, user_id) tuples
        self.product_stats = defaultdict(lambda: {
            'total_clicks': 0,
            'unique_users': set(),
            'click_timestamps': [],
            'boost_score': 0.0
        })
        
        # Kintsugi metadata
        self.kintsugi_notes = []
    
    def add_product(self, product_id: int) -> None:
        """
        Add a product to the urn.
        
        Args:
            product_id (int): Product identifier
        """
        if product_id not in self.urn:
            self.urn[product_id] = self.initial_balls
            self.kintsugi_notes.append(f"✨ Added product {product_id} to urn with {self.initial_balls} initial balls")
    
    def record_click(self, product_id: int, user_id: Optional[str] = None, 
                    timestamp: Optional[float] = None) -> None:
        """
        Record a click on a product and update the urn.
        
        Args:
            product_id (int): Product that was clicked
            user_id (Optional[str]): User who clicked (for analytics)
            timestamp (Optional[float]): Click timestamp (defaults to current time)
        """
        import time
        
        if timestamp is None:
            timestamp = time.time()
        
        if user_id is None:
            user_id = f"user_{random.randint(1000, 9999)}"
        
        # Add product to urn if not present
        if product_id not in self.urn:
            self.add_product(product_id)
        
        # Add balls to the urn (boost the product)
        balls_to_add = max(1, int(self.boost_factor))
        self.urn[product_id] += balls_to_add
        
        # Record click history
        self.click_history.append((product_id, timestamp, user_id))
        
        # Update product statistics
        stats = self.product_stats[product_id]
        stats['total_clicks'] += 1
        stats['unique_users'].add(user_id)
        stats['click_timestamps'].append(timestamp)
        
        # Calculate boost score (exponential growth with diminishing returns)
        click_count = stats['total_clicks']
        unique_users = len(stats['unique_users'])
        
        # Boost score combines total clicks and unique users
        stats['boost_score'] = self._calculate_boost_score(click_count, unique_users)
        
        # Add Kintsugi note
        self.kintsugi_notes.append(
            f"🔧 Product {product_id} clicked by {user_id} - "
            f"added {balls_to_add} balls (total: {self.urn[product_id]})"
        )
    
    def _calculate_boost_score(self, click_count: int, unique_users: int) -> float:
        """
        Calculate boost score for a product.
        
        Args:
            click_count (int): Total number of clicks
            unique_users (int): Number of unique users who clicked
            
        Returns:
            float: Boost score
        """
        # Logarithmic growth to prevent extreme boosting
        click_boost = math.log(1 + click_count) * 0.5
        
        # Bonus for diverse user base
        diversity_boost = math.log(1 + unique_users) * 0.3
        
        # Combine with diminishing returns
        total_boost = click_boost + diversity_boost
        
        # Cap the boost to prevent one product from dominating
        return min(total_boost, 10.0)
    
    def get_product_probability(self, product_id: int) -> float:
        """
        Get the probability of drawing a product from the urn.
        
        Args:
            product_id (int): Product identifier
            
        Returns:
            float: Probability (0.0 to 1.0)
        """
        if not self.urn:
            return 0.0
        
        total_balls = sum(self.urn.values())
        if total_balls == 0:
            return 0.0
        
        product_balls = self.urn.get(product_id, 0)
        return product_balls / total_balls
    
    def get_boosted_products(self, top_k: int = 10) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Get top products by boost score.
        
        Args:
            top_k (int): Number of top products to return
            
        Returns:
            List[Tuple[int, float, Dict[str, Any]]]: List of (product_id, boost_score, stats)
        """
        # Calculate boost scores for all products
        boosted_products = []
        
        for product_id in self.urn.keys():
            stats = self.product_stats[product_id]
            boost_score = stats['boost_score']
            
            # Add probability as additional factor
            probability = self.get_product_probability(product_id)
            combined_score = boost_score * (1 + probability)
            
            boosted_products.append((
                product_id,
                combined_score,
                {
                    'total_clicks': stats['total_clicks'],
                    'unique_users': len(stats['unique_users']),
                    'probability': probability,
                    'boost_score': boost_score
                }
            ))
        
        # Sort by combined score
        boosted_products.sort(key=lambda x: x[1], reverse=True)
        
        return boosted_products[:top_k]
    
    def get_recommendation_weights(self, product_ids: List[int]) -> Dict[int, float]:
        """
        Get recommendation weights for a list of products.
        
        Args:
            product_ids (List[int]): List of product IDs
            
        Returns:
            Dict[int, float]: Mapping of product_id to weight
        """
        weights = {}
        
        for product_id in product_ids:
            if product_id in self.urn:
                # Get boost score and probability
                stats = self.product_stats[product_id]
                boost_score = stats['boost_score']
                probability = self.get_product_probability(product_id)
                
                # Combine boost score and probability
                weight = boost_score * (1 + probability * 0.5)
                weights[product_id] = weight
            else:
                # Default weight for products not in urn
                weights[product_id] = 0.1
        
        return weights
    
    def simulate_clicks(self, product_id: int, num_clicks: int, 
                       user_ids: Optional[List[str]] = None) -> None:
        """
        Simulate multiple clicks on a product (for testing/demo).
        
        Args:
            product_id (int): Product to click
            num_clicks (int): Number of clicks to simulate
            user_ids (Optional[List[str]]): List of user IDs to use
        """
        if user_ids is None:
            user_ids = [f"user_{i}" for i in range(num_clicks)]
        
        for i in range(num_clicks):
            user_id = user_ids[i % len(user_ids)]
            self.record_click(product_id, user_id)
    
    def get_urn_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the urn state.
        
        Returns:
            Dict[str, Any]: Urn statistics
        """
        total_balls = sum(self.urn.values())
        total_clicks = len(self.click_history)
        unique_products = len(self.urn)
        
        # Calculate entropy (diversity measure)
        if total_balls > 0:
            probabilities = [balls / total_balls for balls in self.urn.values()]
            entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
        else:
            entropy = 0.0
        
        return {
            'total_balls': total_balls,
            'total_clicks': total_clicks,
            'unique_products': unique_products,
            'entropy': entropy,
            'most_clicked': self._get_most_clicked_product(),
            'kintsugi_notes_count': len(self.kintsugi_notes)
        }
    
    def _get_most_clicked_product(self) -> Optional[Tuple[int, int]]:
        """Get the most clicked product."""
        if not self.product_stats:
            return None
        
        most_clicked = max(
            self.product_stats.items(),
            key=lambda x: x[1]['total_clicks']
        )
        
        return (most_clicked[0], most_clicked[1]['total_clicks'])
    
    def get_kintsugi_insights(self) -> List[str]:
        """
        Get Kintsugi insights about the urn state.
        
        Returns:
            List[str]: List of insights
        """
        insights = []
        
        if not self.urn:
            insights.append("Empty urn - no products have been clicked yet")
            return insights
        
        stats = self.get_urn_stats()
        
        # Analyze click patterns
        if stats['total_clicks'] > 0:
            insights.append(f"✨ {stats['total_clicks']} clicks recorded across {stats['unique_products']} products")
        
        # Analyze diversity
        if stats['entropy'] > 2.0:
            insights.append("🌟 High diversity - many products are getting clicks")
        elif stats['entropy'] > 1.0:
            insights.append("⚖️ Moderate diversity - some products are more popular")
        else:
            insights.append("🎯 Low diversity - few products dominate")
        
        # Analyze most clicked
        most_clicked = stats['most_clicked']
        if most_clicked:
            product_id, clicks = most_clicked
            insights.append(f"👑 Product {product_id} leads with {clicks} clicks")
        
        # Analyze recent activity
        recent_clicks = [click for click in self.click_history[-10:]]
        if recent_clicks:
            recent_products = set(click[0] for click in recent_clicks)
            insights.append(f"🔄 Recent activity: {len(recent_products)} products clicked")
        
        return insights
    
    def save_model(self, filepath: str) -> None:
        """
        Save the Polya Urn model to file.
        
        Args:
            filepath (str): Path to save the model
        """
        data = {
            'urn': self.urn,
            'click_history': self.click_history,
            'product_stats': {
                str(k): {
                    'total_clicks': v['total_clicks'],
                    'unique_users': list(v['unique_users']),
                    'click_timestamps': v['click_timestamps'],
                    'boost_score': v['boost_score']
                }
                for k, v in self.product_stats.items()
            },
            'initial_balls': self.initial_balls,
            'boost_factor': self.boost_factor,
            'kintsugi_notes': self.kintsugi_notes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Polya Urn model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load the Polya Urn model from file.
        
        Args:
            filepath (str): Path to load the model from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.urn = {int(k): v for k, v in data['urn'].items()}
        self.click_history = data['click_history']
        
        # Reconstruct product stats
        self.product_stats = defaultdict(lambda: {
            'total_clicks': 0,
            'unique_users': set(),
            'click_timestamps': [],
            'boost_score': 0.0
        })
        
        for k, v in data['product_stats'].items():
            self.product_stats[int(k)] = {
                'total_clicks': v['total_clicks'],
                'unique_users': set(v['unique_users']),
                'click_timestamps': v['click_timestamps'],
                'boost_score': v['boost_score']
            }
        
        self.initial_balls = data.get('initial_balls', self.initial_balls)
        self.boost_factor = data.get('boost_factor', self.boost_factor)
        self.kintsugi_notes = data.get('kintsugi_notes', [])
        
        logger.info(f"Polya Urn model loaded from {filepath}")


class PolyaUrnRecommendationEngine:
    """
    Recommendation engine using Polya Urn Model for click-based boosting.
    
    This class integrates the Polya Urn Model with product recommendations,
    providing personalized suggestions based on click patterns and user behavior.
    """
    
    def __init__(self, polya_urn: PolyaUrnModel):
        """
        Initialize the recommendation engine.
        
        Args:
            polya_urn (PolyaUrnModel): Polya Urn model instance
        """
        self.polya_urn = polya_urn
        self.user_profiles = defaultdict(lambda: {
            'clicked_products': set(),
            'preferred_categories': set(),
            'click_timestamps': []
        })
    
    def record_user_click(self, user_id: str, product_id: int, 
                         product_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a user click and update profiles.
        
        Args:
            user_id (str): User identifier
            product_id (int): Product that was clicked
            product_data (Optional[Dict[str, Any]]): Product data for profile building
        """
        # Record click in Polya Urn
        self.polya_urn.record_click(product_id, user_id)
        
        # Update user profile
        profile = self.user_profiles[user_id]
        profile['clicked_products'].add(product_id)
        profile['click_timestamps'].append(self.polya_urn.click_history[-1][1])
        
        # Extract category information if available
        if product_data and 'Type' in product_data:
            profile['preferred_categories'].add(product_data['Type'])
    
    def get_personalized_recommendations(self, user_id: str, 
                                       candidate_products: List[int],
                                       top_k: int = 10) -> List[Tuple[int, float, str]]:
        """
        Get personalized recommendations for a user.
        
        Args:
            user_id (str): User identifier
            candidate_products (List[int]): List of candidate product IDs
            top_k (int): Number of recommendations to return
            
        Returns:
            List[Tuple[int, float, str]]: List of (product_id, score, reason)
        """
        if user_id not in self.user_profiles:
            # New user - return boosted products
            return self._get_boosted_recommendations(candidate_products, top_k)
        
        profile = self.user_profiles[user_id]
        recommendations = []
        
        for product_id in candidate_products:
            score = 0.0
            reasons = []
            
            # Base score from Polya Urn
            urn_weight = self.polya_urn.get_product_probability(product_id)
            if urn_weight > 0:
                score += urn_weight * 0.3
                reasons.append("popular")
            
            # Personalization score
            if product_id in profile['clicked_products']:
                score += 0.5
                reasons.append("previously_clicked")
            
            # Category preference
            # This would need product data to implement properly
            # For now, we'll use a simple heuristic
            
            if score > 0:
                reason = " + ".join(reasons) if reasons else "recommended"
                recommendations.append((product_id, score, reason))
        
        # Sort by score and return top results
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def _get_boosted_recommendations(self, candidate_products: List[int], 
                                   top_k: int) -> List[Tuple[int, float, str]]:
        """Get boosted recommendations for new users."""
        weights = self.polya_urn.get_recommendation_weights(candidate_products)
        
        recommendations = []
        for product_id in candidate_products:
            weight = weights.get(product_id, 0.1)
            recommendations.append((product_id, weight, "trending"))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def get_trending_products(self, top_k: int = 10) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Get trending products based on recent clicks."""
        return self.polya_urn.get_boosted_products(top_k)
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about a user's behavior."""
        if user_id not in self.user_profiles:
            return {'error': 'User not found'}
        
        profile = self.user_profiles[user_id]
        
        return {
            'total_clicks': len(profile['clicked_products']),
            'unique_products': len(profile['clicked_products']),
            'preferred_categories': list(profile['preferred_categories']),
            'click_frequency': len(profile['click_timestamps']),
            'profile_strength': len(profile['clicked_products']) / 10.0  # Normalized
        }


def main():
    """Demo function to test Polya Urn Model."""
    print("=== Polya Urn Model Demo ===")
    
    # Create Polya Urn model
    urn = PolyaUrnModel(initial_balls=1, boost_factor=1.5)
    
    # Add some products
    for i in range(1, 6):
        urn.add_product(i)
    
    # Simulate clicks
    print("Simulating clicks...")
    urn.simulate_clicks(1, 10)  # Product 1 gets 10 clicks
    urn.simulate_clicks(2, 5)   # Product 2 gets 5 clicks
    urn.simulate_clicks(3, 3)   # Product 3 gets 3 clicks
    
    # Get boosted products
    boosted = urn.get_boosted_products(3)
    print("\nTop boosted products:")
    for product_id, score, stats in boosted:
        print(f"  Product {product_id}: score={score:.3f}, clicks={stats['total_clicks']}")
    
    # Get insights
    insights = urn.get_kintsugi_insights()
    print("\nKintsugi insights:")
    for insight in insights:
        print(f"  {insight}")
    
    # Test recommendation engine
    print("\n=== Recommendation Engine Demo ===")
    rec_engine = PolyaUrnRecommendationEngine(urn)
    
    # Simulate user clicks
    rec_engine.record_user_click("user1", 1)
    rec_engine.record_user_click("user1", 2)
    
    # Get recommendations
    recommendations = rec_engine.get_personalized_recommendations("user1", [1, 2, 3, 4, 5], 3)
    print("Recommendations for user1:")
    for product_id, score, reason in recommendations:
        print(f"  Product {product_id}: score={score:.3f}, reason={reason}")


if __name__ == "__main__":
    main()
