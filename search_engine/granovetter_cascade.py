"""
Granovetter Threshold Cascade Model for Viral Recommendations
============================================================

This module implements the Granovetter Threshold Cascade Model for simulating
viral product adoption and recommendations. When many users select a product,
it cascades popularity across related items, creating viral recommendation effects.

This embodies the Kintsugi concept by treating viral adoption as a form of
"collective repair" where community behavior enhances product visibility.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import random
import math
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GranovetterCascadeModel:
    """
    Granovetter Threshold Cascade Model for viral recommendations.
    
    This class implements a threshold-based cascade model where products
    become viral when they reach a certain adoption threshold, triggering
    cascades across related products.
    """
    
    def __init__(self, base_threshold: float = 0.3, cascade_strength: float = 0.5):
        """
        Initialize the Granovetter Cascade Model.
        
        Args:
            base_threshold (float): Base threshold for cascade activation (0.0-1.0)
            cascade_strength (float): Strength of cascade effects (0.0-1.0)
        """
        self.base_threshold = base_threshold
        self.cascade_strength = cascade_strength
        
        # Product adoption tracking
        self.product_adoptions = defaultdict(int)  # product_id -> adoption_count
        self.product_thresholds = {}  # product_id -> threshold
        self.product_cascades = defaultdict(list)  # product_id -> list of cascade events
        
        # User behavior tracking
        self.user_adoptions = defaultdict(set)  # user_id -> set of adopted products
        self.user_influence = {}  # user_id -> influence_score
        
        # Network structure
        self.product_network = defaultdict(set)  # product_id -> set of related products
        self.user_network = defaultdict(set)  # user_id -> set of connected users
        
        # Cascade history
        self.cascade_history = []
        
        # Kintsugi metadata
        self.kintsugi_notes = []
    
    def add_product(self, product_id: int, threshold: Optional[float] = None) -> None:
        """
        Add a product to the cascade model.
        
        Args:
            product_id (int): Product identifier
            threshold (Optional[float]): Custom threshold for this product
        """
        if threshold is None:
            # Dynamic threshold based on product characteristics
            threshold = self._calculate_dynamic_threshold(product_id)
        
        self.product_thresholds[product_id] = threshold
        self.product_adoptions[product_id] = 0
        
        self.kintsugi_notes.append(
            f"✨ Added product {product_id} with threshold {threshold:.3f}"
        )
    
    def _calculate_dynamic_threshold(self, product_id: int) -> float:
        """
        Calculate dynamic threshold for a product.
        
        Args:
            product_id (int): Product identifier
            
        Returns:
            float: Calculated threshold
        """
        # Base threshold with some randomness
        base = self.base_threshold
        
        # Add noise to prevent all products from having same threshold
        noise = random.uniform(-0.1, 0.1)
        
        # Adjust based on product ID (simulate different product types)
        product_factor = (product_id % 10) / 10.0 * 0.2
        
        threshold = base + noise + product_factor
        
        # Ensure threshold is within valid range
        return max(0.1, min(0.9, threshold))
    
    def add_user(self, user_id: str, influence_score: float = 1.0) -> None:
        """
        Add a user to the cascade model.
        
        Args:
            user_id (str): User identifier
            influence_score (float): User's influence score
        """
        self.user_influence[user_id] = influence_score
        self.user_adoptions[user_id] = set()
        
        self.kintsugi_notes.append(
            f"👤 Added user {user_id} with influence {influence_score:.3f}"
        )
    
    def add_product_relationship(self, product1: int, product2: int, 
                               strength: float = 0.5) -> None:
        """
        Add a relationship between two products.
        
        Args:
            product1 (int): First product ID
            product2 (int): Second product ID
            strength (float): Relationship strength (0.0-1.0)
        """
        self.product_network[product1].add((product2, strength))
        self.product_network[product2].add((product1, strength))
    
    def add_user_relationship(self, user1: str, user2: str, 
                            strength: float = 0.5) -> None:
        """
        Add a relationship between two users.
        
        Args:
            user1 (str): First user ID
            user2 (str): Second user ID
            strength (float): Relationship strength (0.0-1.0)
        """
        self.user_network[user1].add((user2, strength))
        self.user_network[user2].add((user1, strength))
    
    def record_adoption(self, user_id: str, product_id: int, 
                       timestamp: Optional[float] = None) -> List[int]:
        """
        Record a product adoption and trigger cascades.
        
        Args:
            user_id (str): User who adopted the product
            product_id (int): Product that was adopted
            timestamp (Optional[float]): Adoption timestamp
            
        Returns:
            List[int]: List of products that were cascade-affected
        """
        import time
        
        if timestamp is None:
            timestamp = time.time()
        
        # Add user and product if not present
        if user_id not in self.user_influence:
            self.add_user(user_id)
        if product_id not in self.product_thresholds:
            self.add_product(product_id)
        
        # Record adoption
        self.product_adoptions[product_id] += 1
        self.user_adoptions[user_id].add(product_id)
        
        # Check if this adoption triggers a cascade
        cascade_products = self._check_cascade_trigger(user_id, product_id, timestamp)
        
        # Record cascade event
        if cascade_products:
            cascade_event = {
                'trigger_user': user_id,
                'trigger_product': product_id,
                'cascade_products': cascade_products,
                'timestamp': timestamp
            }
            self.cascade_history.append(cascade_event)
            self.product_cascades[product_id].append(cascade_event)
            
            self.kintsugi_notes.append(
                f"🌊 Cascade triggered: {len(cascade_products)} products affected by {product_id}"
            )
        
        return cascade_products
    
    def _check_cascade_trigger(self, user_id: str, product_id: int, 
                             timestamp: float) -> List[int]:
        """
        Check if an adoption triggers cascades to related products.
        
        Args:
            user_id (str): User who adopted
            product_id (int): Product that was adopted
            timestamp (float): Adoption timestamp
            
        Returns:
            List[int]: List of products affected by cascade
        """
        cascade_products = []
        
        # Get related products
        related_products = self.product_network.get(product_id, set())
        
        for related_product, relationship_strength in related_products:
            if self._should_cascade(user_id, related_product, relationship_strength):
                # Trigger cascade to this product
                cascade_products.append(related_product)
                
                # Boost adoption count for cascade effect
                cascade_boost = int(relationship_strength * self.cascade_strength * 10)
                self.product_adoptions[related_product] += cascade_boost
                
                # Add Kintsugi note
                self.kintsugi_notes.append(
                    f"🔧 Cascade boost: {related_product} +{cascade_boost} adoptions"
                )
        
        return cascade_products
    
    def _should_cascade(self, user_id: str, product_id: int, 
                       relationship_strength: float) -> bool:
        """
        Determine if a cascade should occur to a related product.
        
        Args:
            user_id (str): User who triggered the cascade
            product_id (int): Product to potentially cascade to
            relationship_strength (float): Strength of relationship
            
        Returns:
            bool: Whether cascade should occur
        """
        # Get current adoption rate for the product
        total_users = len(self.user_influence)
        if total_users == 0:
            return False
        
        adoption_rate = self.product_adoptions[product_id] / total_users
        threshold = self.product_thresholds.get(product_id, self.base_threshold)
        
        # Calculate cascade probability
        # Higher relationship strength and user influence increase probability
        user_influence = self.user_influence.get(user_id, 1.0)
        cascade_probability = relationship_strength * user_influence * self.cascade_strength
        
        # Check if adoption rate is close to threshold
        threshold_proximity = 1.0 - abs(adoption_rate - threshold)
        
        # Combine factors
        final_probability = cascade_probability * threshold_proximity
        
        return random.random() < final_probability
    
    def get_viral_products(self, top_k: int = 10) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Get products that have gone viral or are trending.
        
        Args:
            top_k (int): Number of top products to return
            
        Returns:
            List[Tuple[int, float, Dict[str, Any]]]: List of (product_id, viral_score, stats)
        """
        viral_products = []
        
        for product_id in self.product_adoptions.keys():
            adoption_count = self.product_adoptions[product_id]
            threshold = self.product_thresholds.get(product_id, self.base_threshold)
            
            # Calculate viral score
            total_users = len(self.user_influence)
            if total_users > 0:
                adoption_rate = adoption_count / total_users
                viral_score = self._calculate_viral_score(adoption_count, adoption_rate, threshold)
            else:
                adoption_rate = 0.0
                viral_score = 0.0
            
            # Get cascade statistics
            cascade_events = len(self.product_cascades[product_id])
            cascade_triggered = len([c for c in self.cascade_history if c['trigger_product'] == product_id])
            
            stats = {
                'adoption_count': adoption_count,
                'adoption_rate': adoption_rate,
                'threshold': threshold,
                'cascade_events': cascade_events,
                'cascade_triggered': cascade_triggered,
                'is_viral': adoption_rate > threshold
            }
            
            viral_products.append((product_id, viral_score, stats))
        
        # Sort by viral score
        viral_products.sort(key=lambda x: x[1], reverse=True)
        return viral_products[:top_k]
    
    def _calculate_viral_score(self, adoption_count: int, adoption_rate: float, 
                              threshold: float) -> float:
        """
        Calculate viral score for a product.
        
        Args:
            adoption_count (int): Number of adoptions
            adoption_rate (float): Adoption rate
            threshold (float): Product threshold
            
        Returns:
            float: Viral score
        """
        # Base score from adoption count
        base_score = math.log(1 + adoption_count) * 0.5
        
        # Threshold bonus (products that exceed threshold get bonus)
        if adoption_rate > threshold:
            threshold_bonus = (adoption_rate - threshold) * 10
        else:
            threshold_bonus = 0
        
        # Growth rate bonus (recent growth gets bonus)
        growth_bonus = adoption_rate * 2
        
        return base_score + threshold_bonus + growth_bonus
    
    def get_cascade_network(self) -> Dict[str, Any]:
        """
        Get the cascade network structure.
        
        Returns:
            Dict[str, Any]: Network structure and statistics
        """
        total_products = len(self.product_adoptions)
        total_users = len(self.user_influence)
        total_cascades = len(self.cascade_history)
        
        # Calculate network density
        max_connections = total_products * (total_products - 1) // 2
        actual_connections = sum(len(connections) for connections in self.product_network.values()) // 2
        network_density = actual_connections / max_connections if max_connections > 0 else 0
        
        # Calculate cascade frequency
        cascade_frequency = total_cascades / total_products if total_products > 0 else 0
        
        return {
            'total_products': total_products,
            'total_users': total_users,
            'total_cascades': total_cascades,
            'network_density': network_density,
            'cascade_frequency': cascade_frequency,
            'viral_products': len([p for p in self.product_adoptions.values() if p > 0])
        }
    
    def get_kintsugi_insights(self) -> List[str]:
        """
        Get Kintsugi insights about the cascade system.
        
        Returns:
            List[str]: List of insights
        """
        insights = []
        
        if not self.product_adoptions:
            insights.append("Empty cascade system - no products have been adopted yet")
            return insights
        
        # Analyze viral products
        viral_products = self.get_viral_products(5)
        viral_count = len([p for p in viral_products if p[2]['is_viral']])
        
        if viral_count > 0:
            insights.append(f"🌟 {viral_count} products have gone viral!")
        
        # Analyze cascade activity
        total_cascades = len(self.cascade_history)
        if total_cascades > 0:
            insights.append(f"🌊 {total_cascades} cascade events have occurred")
        
        # Analyze network effects
        network_stats = self.get_cascade_network()
        if network_stats['network_density'] > 0.1:
            insights.append("🔗 Strong network connectivity - cascades spread easily")
        elif network_stats['network_density'] > 0.05:
            insights.append("⚖️ Moderate network connectivity - some cascade effects")
        else:
            insights.append("🔀 Sparse network - limited cascade effects")
        
        # Analyze adoption patterns
        total_adoptions = sum(self.product_adoptions.values())
        if total_adoptions > 0:
            avg_adoptions = total_adoptions / len(self.product_adoptions)
            insights.append(f"📈 Average {avg_adoptions:.1f} adoptions per product")
        
        return insights
    
    def simulate_cascade_network(self, num_products: int = 20, 
                                num_users: int = 100) -> None:
        """
        Simulate a cascade network for testing.
        
        Args:
            num_products (int): Number of products to create
            num_users (int): Number of users to create
        """
        # Add products
        for i in range(1, num_products + 1):
            self.add_product(i)
        
        # Add users
        for i in range(1, num_users + 1):
            influence = random.uniform(0.5, 2.0)
            self.add_user(f"user_{i}", influence)
        
        # Create product relationships
        for i in range(1, num_products + 1):
            # Each product connects to 2-5 other products
            num_connections = random.randint(2, 5)
            connected_products = random.sample(
                [j for j in range(1, num_products + 1) if j != i],
                min(num_connections, num_products - 1)
            )
            
            for j in connected_products:
                strength = random.uniform(0.3, 0.8)
                self.add_product_relationship(i, j, strength)
        
        # Create user relationships
        for i in range(1, num_users + 1):
            # Each user connects to 3-8 other users
            num_connections = random.randint(3, 8)
            connected_users = random.sample(
                [f"user_{j}" for j in range(1, num_users + 1) if j != i],
                min(num_connections, num_users - 1)
            )
            
            for j in connected_users:
                strength = random.uniform(0.2, 0.7)
                self.add_user_relationship(f"user_{i}", j, strength)
        
        self.kintsugi_notes.append(
            f"🎭 Simulated network: {num_products} products, {num_users} users"
        )
    
    def save_model(self, filepath: str) -> None:
        """
        Save the cascade model to file.
        
        Args:
            filepath (str): Path to save the model
        """
        data = {
            'product_adoptions': dict(self.product_adoptions),
            'product_thresholds': self.product_thresholds,
            'user_adoptions': {k: list(v) for k, v in self.user_adoptions.items()},
            'user_influence': self.user_influence,
            'product_network': {
                str(k): [(p, s) for p, s in v] 
                for k, v in self.product_network.items()
            },
            'user_network': {
                k: [(u, s) for u, s in v] 
                for k, v in self.user_network.items()
            },
            'cascade_history': self.cascade_history,
            'base_threshold': self.base_threshold,
            'cascade_strength': self.cascade_strength,
            'kintsugi_notes': self.kintsugi_notes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Granovetter Cascade model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load the cascade model from file.
        
        Args:
            filepath (str): Path to load the model from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.product_adoptions = defaultdict(int, data['product_adoptions'])
        self.product_thresholds = data['product_thresholds']
        self.user_adoptions = {
            k: set(v) for k, v in data['user_adoptions'].items()
        }
        self.user_influence = data['user_influence']
        
        # Reconstruct networks
        self.product_network = defaultdict(set)
        for k, v in data['product_network'].items():
            self.product_network[int(k)] = set((p, s) for p, s in v)
        
        self.user_network = defaultdict(set)
        for k, v in data['user_network'].items():
            self.user_network[k] = set((u, s) for u, s in v)
        
        self.cascade_history = data['cascade_history']
        self.base_threshold = data.get('base_threshold', self.base_threshold)
        self.cascade_strength = data.get('cascade_strength', self.cascade_strength)
        self.kintsugi_notes = data.get('kintsugi_notes', [])
        
        logger.info(f"Granovetter Cascade model loaded from {filepath}")


def main():
    """Demo function to test Granovetter Cascade Model."""
    print("=== Granovetter Cascade Model Demo ===")
    
    # Create cascade model
    cascade = GranovetterCascadeModel(base_threshold=0.2, cascade_strength=0.6)
    
    # Simulate network
    cascade.simulate_cascade_network(num_products=10, num_users=50)
    
    # Simulate adoptions
    print("Simulating adoptions...")
    for i in range(100):
        user_id = f"user_{random.randint(1, 50)}"
        product_id = random.randint(1, 10)
        cascade.record_adoption(user_id, product_id)
    
    # Get viral products
    viral = cascade.get_viral_products(5)
    print("\nTop viral products:")
    for product_id, score, stats in viral:
        print(f"  Product {product_id}: score={score:.3f}, adoptions={stats['adoption_count']}, viral={stats['is_viral']}")
    
    # Get insights
    insights = cascade.get_kintsugi_insights()
    print("\nKintsugi insights:")
    for insight in insights:
        print(f"  {insight}")
    
    # Get network stats
    network_stats = cascade.get_cascade_network()
    print(f"\nNetwork stats: {network_stats}")


if __name__ == "__main__":
    main()
