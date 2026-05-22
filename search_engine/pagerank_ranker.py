"""
PageRank-Inspired Ranking System
===============================

This module implements a PageRank-inspired ranking algorithm for e-commerce
products using product relationships and graph structure. It creates a graph
where products are nodes and relationships (brand, category, features) are edges.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import numpy as np
import re
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict, Counter
import json
import math
from pathlib import Path

# Try to import NetworkX for graph operations
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logging.warning("NetworkX not available. Using basic graph implementation.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductGraph:
    """
    Graph structure for products with relationships as edges.
    
    This class builds a graph where products are nodes and various
    relationships (brand, category, features) create edges between them.
    """
    
    def __init__(self):
        """Initialize the product graph."""
        self.products = {}  # product_id -> product_data
        self.graph = {}  # product_id -> set of connected product_ids
        self.edge_weights = {}  # (product_id1, product_id2) -> weight
        self.node_weights = {}  # product_id -> node weight
        
        if NETWORKX_AVAILABLE:
            self.nx_graph = nx.DiGraph()
        else:
            self.nx_graph = None
    
    def add_product(self, product_id: int, product: Dict[str, Any]) -> None:
        """
        Add a product to the graph.
        
        Args:
            product_id (int): Unique product identifier
            product (Dict[str, Any]): Product data
        """
        self.products[product_id] = product
        self.graph[product_id] = set()
        self.node_weights[product_id] = self._calculate_node_weight(product)
        
        if self.nx_graph is not None:
            self.nx_graph.add_node(product_id, **product)
    
    def build_relationships(self) -> None:
        """Build relationships between products based on various criteria."""
        logger.info("Building product relationships...")
        
        # Build relationships based on different criteria
        self._build_brand_relationships()
        self._build_category_relationships()
        self._build_feature_relationships()
        self._build_price_relationships()
        self._build_specification_relationships()
        
        # Update NetworkX graph
        if self.nx_graph is not None:
            for product_id, connections in self.graph.items():
                for connected_id in connections:
                    weight = self.edge_weights.get((product_id, connected_id), 1.0)
                    self.nx_graph.add_edge(product_id, connected_id, weight=weight)
        
        logger.info(f"Built relationships for {len(self.products)} products")
        logger.info(f"Total edges: {sum(len(connections) for connections in self.graph.values())}")
    
    def _build_brand_relationships(self) -> None:
        """Build relationships based on brand similarity."""
        brand_products = defaultdict(list)
        
        # Group products by brand
        for product_id, product in self.products.items():
            brand = product.get('Brand', '').strip().lower()
            if brand:
                brand_products[brand].append(product_id)
        
        # Create relationships within brands
        for brand, product_ids in brand_products.items():
            if len(product_ids) > 1:
                for i, product_id1 in enumerate(product_ids):
                    for product_id2 in product_ids[i+1:]:
                        self._add_relationship(product_id1, product_id2, 0.8, 'brand')
    
    def _build_category_relationships(self) -> None:
        """Build relationships based on product category/type."""
        category_products = defaultdict(list)
        
        # Group products by type/category
        for product_id, product in self.products.items():
            product_type = product.get('Type', '').strip().lower()
            if product_type:
                category_products[product_type].append(product_id)
        
        # Create relationships within categories
        for category, product_ids in category_products.items():
            if len(product_ids) > 1:
                for i, product_id1 in enumerate(product_ids):
                    for product_id2 in product_ids[i+1:]:
                        self._add_relationship(product_id1, product_id2, 0.6, 'category')
    
    def _build_feature_relationships(self) -> None:
        """Build relationships based on shared features."""
        feature_products = defaultdict(list)
        
        # Extract features from products
        for product_id, product in self.products.items():
            features = self._extract_features(product)
            for feature in features:
                feature_products[feature].append(product_id)
        
        # Create relationships based on shared features
        for feature, product_ids in feature_products.items():
            if len(product_ids) > 1:
                for i, product_id1 in enumerate(product_ids):
                    for product_id2 in product_ids[i+1:]:
                        self._add_relationship(product_id1, product_id2, 0.4, 'feature')
    
    def _build_price_relationships(self) -> None:
        """Build relationships based on price similarity."""
        price_ranges = {
            'budget': (0, 100),
            'mid': (100, 500),
            'premium': (500, 1000),
            'luxury': (1000, float('inf'))
        }
        
        range_products = defaultdict(list)
        
        # Group products by price range
        for product_id, product in self.products.items():
            price = self._extract_price(product)
            if price is not None:
                for range_name, (min_price, max_price) in price_ranges.items():
                    if min_price <= price < max_price:
                        range_products[range_name].append(product_id)
                        break
        
        # Create relationships within price ranges
        for range_name, product_ids in range_products.items():
            if len(product_ids) > 1:
                for i, product_id1 in enumerate(product_ids):
                    for product_id2 in product_ids[i+1:]:
                        self._add_relationship(product_id1, product_id2, 0.3, 'price')
    
    def _build_specification_relationships(self) -> None:
        """Build relationships based on technical specifications."""
        spec_products = defaultdict(list)
        
        # Extract specifications
        for product_id, product in self.products.items():
            specs = self._extract_specifications(product)
            for spec in specs:
                spec_products[spec].append(product_id)
        
        # Create relationships based on shared specifications
        for spec, product_ids in spec_products.items():
            if len(product_ids) > 1:
                for i, product_id1 in enumerate(product_ids):
                    for product_id2 in product_ids[i+1:]:
                        self._add_relationship(product_id1, product_id2, 0.5, 'specification')
    
    def _add_relationship(self, product_id1: int, product_id2: int, 
                         weight: float, relationship_type: str) -> None:
        """
        Add a relationship between two products.
        
        Args:
            product_id1 (int): First product ID
            product_id2 (int): Second product ID
            weight (float): Relationship weight
            relationship_type (str): Type of relationship
        """
        # Add bidirectional relationship
        self.graph[product_id1].add(product_id2)
        self.graph[product_id2].add(product_id1)
        
        # Store edge weights
        self.edge_weights[(product_id1, product_id2)] = weight
        self.edge_weights[(product_id2, product_id1)] = weight
    
    def _extract_features(self, product: Dict[str, Any]) -> List[str]:
        """Extract features from product data."""
        features = []
        
        # Extract from various feature fields
        feature_fields = ['Features', 'Key Features', 'Other Features', 'Specifications']
        
        for field in feature_fields:
            if field in product and product[field]:
                value = str(product[field]).lower()
                # Split by common separators
                parts = re.split(r'[,;]\s*|\n', value)
                for part in parts:
                    part = part.strip()
                    if len(part) > 3 and len(part) < 50:
                        features.append(part)
        
        return features
    
    def _extract_specifications(self, product: Dict[str, Any]) -> List[str]:
        """Extract technical specifications from product data."""
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
    
    def _extract_price(self, product: Dict[str, Any]) -> Optional[float]:
        """Extract price from product data."""
        price_field = product.get('Price', '')
        if not price_field:
            return None
        
        # Extract numeric value from price string
        price_match = re.search(r'[\d,]+\.?\d*', str(price_field))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                return None
        
        return None
    
    def _calculate_node_weight(self, product: Dict[str, Any]) -> float:
        """Calculate initial weight for a product node."""
        weight = 1.0
        
        # Boost weight for products with more information
        info_fields = ['Brand', 'Type', 'Features', 'Description', 'Specifications']
        info_count = sum(1 for field in info_fields if field in product and product[field])
        weight += info_count * 0.1
        
        # Boost weight for products with higher prices (premium products)
        price = self._extract_price(product)
        if price is not None:
            weight += min(price / 1000, 1.0) * 0.5
        
        return weight


class PageRankRanker:
    """
    PageRank-inspired ranking system for e-commerce products.
    
    This class implements a PageRank algorithm adapted for product ranking,
    where products are nodes and relationships are edges in a graph.
    """
    
    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 100):
        """
        Initialize the PageRank ranker.
        
        Args:
            damping_factor (float): Damping factor for PageRank (0.85 is standard)
            max_iterations (int): Maximum iterations for convergence
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.graph = ProductGraph()
        self.pagerank_scores = {}
        self.convergence_threshold = 1e-6
    
    def add_products(self, products: List[Dict[str, Any]]) -> None:
        """
        Add products to the ranking system.
        
        Args:
            products (List[Dict[str, Any]]): List of products to rank
        """
        logger.info(f"Adding {len(products)} products to PageRank system...")
        
        for i, product in enumerate(products):
            self.graph.add_product(i, product)
        
        # Build relationships
        self.graph.build_relationships()
        
        # Calculate PageRank scores
        self._calculate_pagerank()
    
    def _calculate_pagerank(self) -> None:
        """Calculate PageRank scores for all products."""
        logger.info("Calculating PageRank scores...")
        
        if self.graph.nx_graph is not None and NETWORKX_AVAILABLE:
            # Use NetworkX PageRank if available
            self.pagerank_scores = nx.pagerank(
                self.graph.nx_graph, 
                alpha=self.damping_factor,
                max_iter=self.max_iterations
            )
        else:
            # Use custom PageRank implementation
            self.pagerank_scores = self._custom_pagerank()
        
        logger.info(f"PageRank calculation completed for {len(self.pagerank_scores)} products")
    
    def _custom_pagerank(self) -> Dict[int, float]:
        """Custom PageRank implementation."""
        num_products = len(self.graph.products)
        if num_products == 0:
            return {}
        
        # Initialize PageRank scores
        pagerank = {product_id: 1.0 / num_products for product_id in self.graph.products.keys()}
        
        for iteration in range(self.max_iterations):
            new_pagerank = {}
            
            for product_id in self.graph.products.keys():
                # Calculate new PageRank score
                score = (1 - self.damping_factor) / num_products
                
                # Add contribution from incoming links
                for source_id, connections in self.graph.graph.items():
                    if product_id in connections:
                        # Calculate weight for this connection
                        weight = self.graph.edge_weights.get((source_id, product_id), 1.0)
                        out_degree = len(connections)
                        
                        if out_degree > 0:
                            score += self.damping_factor * pagerank[source_id] * weight / out_degree
                
                new_pagerank[product_id] = score
            
            # Check for convergence
            max_change = max(abs(new_pagerank[pid] - pagerank[pid]) for pid in pagerank.keys())
            
            if max_change < self.convergence_threshold:
                logger.info(f"PageRank converged after {iteration + 1} iterations")
                break
            
            pagerank = new_pagerank
        
        return pagerank
    
    def rank_products(self, product_ids: List[int], 
                     pagerank_weight: float = 0.3) -> List[Tuple[int, float]]:
        """
        Rank products using PageRank scores.
        
        Args:
            product_ids (List[int]): List of product IDs to rank
            pagerank_weight (float): Weight for PageRank in final score
            
        Returns:
            List[Tuple[int, float]]: List of (product_id, score) tuples
        """
        ranked_products = []
        
        for product_id in product_ids:
            if product_id in self.pagerank_scores:
                pagerank_score = self.pagerank_scores[product_id]
                
                # Combine with node weight
                node_weight = self.graph.node_weights.get(product_id, 1.0)
                combined_score = pagerank_score * (1 + node_weight * pagerank_weight)
                
                ranked_products.append((product_id, combined_score))
        
        # Sort by score (descending)
        ranked_products.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_products
    
    def get_product_rank(self, product_id: int) -> float:
        """
        Get PageRank score for a specific product.
        
        Args:
            product_id (int): Product ID
            
        Returns:
            float: PageRank score
        """
        return self.pagerank_scores.get(product_id, 0.0)
    
    def get_top_products(self, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Get top products by PageRank score.
        
        Args:
            top_k (int): Number of top products to return
            
        Returns:
            List[Tuple[int, float]]: List of top products
        """
        all_products = [(pid, score) for pid, score in self.pagerank_scores.items()]
        all_products.sort(key=lambda x: x[1], reverse=True)
        return all_products[:top_k]
    
    def get_related_products(self, product_id: int, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Get products related to a specific product.
        
        Args:
            product_id (int): Product ID
            top_k (int): Number of related products to return
            
        Returns:
            List[Tuple[int, float]]: List of related products
        """
        if product_id not in self.graph.graph:
            return []
        
        # Get connected products
        connected_products = self.graph.graph[product_id]
        
        # Rank them by PageRank score
        related_products = []
        for connected_id in connected_products:
            if connected_id in self.pagerank_scores:
                score = self.pagerank_scores[connected_id]
                related_products.append((connected_id, score))
        
        # Sort by score and return top results
        related_products.sort(key=lambda x: x[1], reverse=True)
        return related_products[:top_k]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the PageRank system.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        if not self.pagerank_scores:
            return {'error': 'PageRank not calculated'}
        
        scores = list(self.pagerank_scores.values())
        
        return {
            'total_products': len(self.pagerank_scores),
            'total_edges': sum(len(connections) for connections in self.graph.graph.values()),
            'average_pagerank': sum(scores) / len(scores),
            'max_pagerank': max(scores),
            'min_pagerank': min(scores),
            'damping_factor': self.damping_factor,
            'convergence_threshold': self.convergence_threshold
        }
    
    def save_ranker(self, filepath: str) -> None:
        """
        Save PageRank scores to file.
        
        Args:
            filepath (str): Path to save scores
        """
        data = {
            'pagerank_scores': {str(k): v for k, v in self.pagerank_scores.items()},
            'node_weights': {str(k): v for k, v in self.graph.node_weights.items()},
            'damping_factor': self.damping_factor,
            'max_iterations': self.max_iterations
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"PageRank scores saved to {filepath}")
    
    def load_ranker(self, filepath: str) -> None:
        """
        Load PageRank scores from file.
        
        Args:
            filepath (str): Path to load scores from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.pagerank_scores = {int(k): v for k, v in data['pagerank_scores'].items()}
        self.graph.node_weights = {int(k): v for k, v in data['node_weights'].items()}
        self.damping_factor = data.get('damping_factor', self.damping_factor)
        self.max_iterations = data.get('max_iterations', self.max_iterations)
        
        logger.info(f"PageRank scores loaded from {filepath}")


def main():
    """Demo function to test PageRank ranking."""
    print("=== PageRank Ranking System Demo ===")
    print("This module provides PageRank-inspired product ranking.")
    print("Use it with the main search engine for enhanced ranking.")


if __name__ == "__main__":
    main()
