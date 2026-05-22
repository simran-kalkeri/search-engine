"""
Comprehensive Demo System for Kintsugi Search + Recommendation Engine
====================================================================

This module provides comprehensive testing and demonstration functionality
for the entire Kintsugi Search + Recommendation Engine system.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import time
import random
from typing import Dict, List, Any, Tuple
from pathlib import Path
import argparse

# Import all our modules
from advanced_search_engine import AdvancedSearchEngine
from recommendation_engine import KintsugiRecommendationEngine
from unified_scoring_system import UnifiedScoringSystem
from kintsugi_repair_system import KintsugiRepairSystem
from polya_urn_model import PolyaUrnModel
from granovetter_cascade import GranovetterCascadeModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KintsugiDemoSystem:
    """
    Comprehensive demo system for the Kintsugi Search + Recommendation Engine.
    
    This class provides end-to-end testing and demonstration of all system
    components with realistic data and scenarios.
    """
    
    def __init__(self, data_file: str = "data-set.json"):
        """
        Initialize the demo system.
        
        Args:
            data_file (str): Path to the data file
        """
        self.data_file = data_file
        self.search_engine = None
        self.recommendation_engine = None
        self.scoring_system = None
        self.repair_system = None
        
        # Demo statistics
        self.demo_stats = {
            'searches_performed': 0,
            'recommendations_generated': 0,
            'repairs_performed': 0,
            'interactions_recorded': 0,
            'total_demo_time': 0
        }
        
        # Demo users
        self.demo_users = [
            'demo_user_1', 'demo_user_2', 'demo_user_3', 
            'demo_user_4', 'demo_user_5'
        ]
        
        # Demo queries with various imperfections
        self.demo_queries = [
            "samsng galaxy s23",  # Typo
            "iphne 14 pro max",   # Typo
            "noise cancelling headphnes",  # Typo
            "wireles blutooth speaker",  # Multiple typos
            "laptp gaming",  # Incomplete + typo
            "   extra   spaces   ",  # Noisy data
            "SAMSUNG GALAXY",  # Case issues
            "smartphone with good camera",  # Semantic query
            "budget laptop under 500",  # Complex query
            "wireless headphones noise cancelling"  # Multi-word query
        ]
        
        # Initialize all components
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize all system components."""
        logger.info("🔍 Initializing Kintsugi Demo System...")
        
        # Initialize search engine
        self.search_engine = AdvancedSearchEngine(self.data_file)
        logger.info("✅ Advanced search engine initialized")
        
        # Initialize recommendation engine
        self.recommendation_engine = self.search_engine.recommendation_engine
        logger.info("✅ Recommendation engine initialized")
        
        # Initialize scoring system
        self.scoring_system = UnifiedScoringSystem()
        logger.info("✅ Unified scoring system initialized")
        
        # Initialize repair system
        self.repair_system = KintsugiRepairSystem()
        logger.info("✅ Kintsugi repair system initialized")
        
        logger.info("🌟 All components initialized successfully!")
    
    def run_comprehensive_demo(self) -> None:
        """Run a comprehensive demonstration of all system features."""
        logger.info("🚀 Starting Comprehensive Kintsugi Demo...")
        start_time = time.time()
        
        # Demo 1: Query Repair System
        self._demo_query_repair()
        
        # Demo 2: Search Engine
        self._demo_search_engine()
        
        # Demo 3: Recommendation Engine
        self._demo_recommendation_engine()
        
        # Demo 4: Unified Scoring System
        self._demo_unified_scoring()
        
        # Demo 5: Polya Urn Model
        self._demo_polya_urn_model()
        
        # Demo 6: Granovetter Cascade Model
        self._demo_cascade_model()
        
        # Demo 7: End-to-End Integration
        self._demo_end_to_end()
        
        # Calculate total demo time
        self.demo_stats['total_demo_time'] = time.time() - start_time
        
        # Display final statistics
        self._display_demo_statistics()
        
        logger.info("🎉 Comprehensive demo completed successfully!")
    
    def _demo_query_repair(self) -> None:
        """Demonstrate the query repair system."""
        logger.info("\n🔧 Demo 1: Query Repair System")
        logger.info("=" * 50)
        
        for query in self.demo_queries[:5]:  # Test first 5 queries
            logger.info(f"\nOriginal Query: '{query}'")
            
            repair_result = self.repair_system.repair_query(query)
            
            logger.info(f"Repaired Query: '{repair_result['repaired_query']}'")
            logger.info(f"Repair Successful: {repair_result['repair_successful']}")
            logger.info(f"Quality Score: {repair_result['quality_score']:.3f}")
            
            if repair_result['repair_notes']:
                logger.info("Repair Notes:")
                for note in repair_result['repair_notes']:
                    logger.info(f"  {note}")
            
            if repair_result['kintsugi_insights']:
                logger.info("Kintsugi Insights:")
                for insight in repair_result['kintsugi_insights']:
                    logger.info(f"  {insight}")
            
            self.demo_stats['repairs_performed'] += 1
    
    def _demo_search_engine(self) -> None:
        """Demonstrate the search engine."""
        logger.info("\n🔍 Demo 2: Advanced Search Engine")
        logger.info("=" * 50)
        
        for query in self.demo_queries[:3]:  # Test first 3 queries
            logger.info(f"\nSearching for: '{query}'")
            
            # Test different search types
            search_types = ['comprehensive', 'tfidf', 'vector', 'phrase']
            
            for search_type in search_types:
                start_time = time.time()
                results = self.search_engine.search(query, search_type=search_type, top_k=5)
                search_time = time.time() - start_time
                
                logger.info(f"  {search_type.title()} Search: {len(results['results'])} results in {search_time:.3f}s")
                
                if results['results']:
                    top_result = results['results'][0]
                    logger.info(f"    Top result: {top_result.get('document', {}).get('Brand', 'Unknown')} {top_result.get('document', {}).get('Type', 'Unknown')}")
                    logger.info(f"    Score: {top_result.get('unified_score', 0):.3f}")
                
                self.demo_stats['searches_performed'] += 1
    
    def _demo_recommendation_engine(self) -> None:
        """Demonstrate the recommendation engine."""
        logger.info("\n🎯 Demo 3: Recommendation Engine")
        logger.info("=" * 50)
        
        for user_id in self.demo_users[:3]:  # Test first 3 users
            logger.info(f"\nGenerating recommendations for {user_id}")
            
            # Simulate some user interactions first
            self._simulate_user_interactions(user_id)
            
            # Get recommendations
            recommendations = self.recommendation_engine.get_recommendations(user_id, top_k=5)
            
            logger.info(f"  Generated {len(recommendations)} recommendations")
            
            if recommendations:
                for i, rec in enumerate(recommendations[:3], 1):
                    product = rec.get('product', {})
                    logger.info(f"    {i}. {product.get('Brand', 'Unknown')} {product.get('Type', 'Unknown')}")
                    logger.info(f"       Score: {rec.get('blended_score', 0):.3f}, Methods: {rec.get('methods_used', [])}")
                    logger.info(f"       Quality: {rec.get('kintsugi_quality', 'Unknown')}")
            
            self.demo_stats['recommendations_generated'] += len(recommendations)
    
    def _demo_unified_scoring(self) -> None:
        """Demonstrate the unified scoring system."""
        logger.info("\n⚖️ Demo 4: Unified Scoring System")
        logger.info("=" * 50)
        
        # Test different scoring scenarios
        test_scenarios = [
            {
                'name': 'High Quality Result',
                'text_score': 0.9,
                'vector_score': 0.8,
                'pagerank_score': 0.7,
                'polya_urn_score': 0.6,
                'cascade_score': 0.5,
                'repair_score': 0.9,
                'freshness_score': 0.8
            },
            {
                'name': 'Medium Quality Result',
                'text_score': 0.6,
                'vector_score': 0.5,
                'pagerank_score': 0.4,
                'polya_urn_score': 0.3,
                'cascade_score': 0.2,
                'repair_score': 0.6,
                'freshness_score': 0.5
            },
            {
                'name': 'Low Quality Result',
                'text_score': 0.3,
                'vector_score': 0.2,
                'pagerank_score': 0.1,
                'polya_urn_score': 0.1,
                'cascade_score': 0.1,
                'repair_score': 0.3,
                'freshness_score': 0.2
            }
        ]
        
        for scenario in test_scenarios:
            logger.info(f"\nTesting: {scenario['name']}")
            
            scoring_result = self.scoring_system.calculate_unified_score(
                text_score=scenario['text_score'],
                vector_score=scenario['vector_score'],
                pagerank_score=scenario['pagerank_score'],
                polya_urn_score=scenario['polya_urn_score'],
                cascade_score=scenario['cascade_score'],
                repair_score=scenario['repair_score'],
                freshness_score=scenario['freshness_score']
            )
            
            logger.info(f"  Unified Score: {scoring_result['unified_score']:.3f}")
            logger.info(f"  Quality Level: {scoring_result['score_quality']['quality_level']}")
            logger.info(f"  Balance: {scoring_result['score_quality']['balance']:.3f}")
            logger.info(f"  Diversity: {scoring_result['score_quality']['diversity']:.3f}")
            
            if scoring_result['kintsugi_insights']:
                logger.info("  Kintsugi Insights:")
                for insight in scoring_result['kintsugi_insights']:
                    logger.info(f"    {insight}")
    
    def _demo_polya_urn_model(self) -> None:
        """Demonstrate the Polya Urn Model."""
        logger.info("\n🎯 Demo 5: Polya Urn Model")
        logger.info("=" * 50)
        
        # Create a new Polya Urn for demo
        polya_urn = PolyaUrnModel(initial_balls=1, boost_factor=1.5)
        
        # Add some products
        for i in range(1, 11):
            polya_urn.add_product(i)
        
        # Simulate clicks
        logger.info("Simulating user clicks...")
        for _ in range(50):
            user_id = random.choice(self.demo_users)
            product_id = random.randint(1, 10)
            polya_urn.record_click(product_id, user_id)
        
        # Get boosted products
        boosted_products = polya_urn.get_boosted_products(5)
        logger.info(f"\nTop 5 Boosted Products:")
        for i, (product_id, score, stats) in enumerate(boosted_products, 1):
            logger.info(f"  {i}. Product {product_id}: Score {score:.3f}, Clicks {stats['total_clicks']}")
        
        # Get insights
        insights = polya_urn.get_kintsugi_insights()
        logger.info(f"\nKintsugi Insights:")
        for insight in insights:
            logger.info(f"  {insight}")
    
    def _demo_cascade_model(self) -> None:
        """Demonstrate the Granovetter Cascade Model."""
        logger.info("\n🌊 Demo 6: Granovetter Cascade Model")
        logger.info("=" * 50)
        
        # Create a new cascade model for demo
        cascade_model = GranovetterCascadeModel(base_threshold=0.3, cascade_strength=0.6)
        
        # Simulate a network
        cascade_model.simulate_cascade_network(num_products=20, num_users=50)
        
        # Simulate adoptions
        logger.info("Simulating product adoptions...")
        for _ in range(100):
            user_id = random.choice([f"user_{i}" for i in range(1, 51)])
            product_id = random.randint(1, 20)
            cascade_model.record_adoption(user_id, product_id)
        
        # Get viral products
        viral_products = cascade_model.get_viral_products(5)
        logger.info(f"\nTop 5 Viral Products:")
        for i, (product_id, score, stats) in enumerate(viral_products, 1):
            logger.info(f"  {i}. Product {product_id}: Score {score:.3f}, Adoptions {stats['adoption_count']}, Viral {stats['is_viral']}")
        
        # Get insights
        insights = cascade_model.get_kintsugi_insights()
        logger.info(f"\nKintsugi Insights:")
        for insight in insights:
            logger.info(f"  {insight}")
    
    def _demo_end_to_end(self) -> None:
        """Demonstrate end-to-end integration."""
        logger.info("\n🔄 Demo 7: End-to-End Integration")
        logger.info("=" * 50)
        
        # Simulate a complete user journey
        user_id = "demo_user_complete"
        
        # Step 1: User searches with imperfect query
        query = "samsng galaxy s23"
        logger.info(f"User searches: '{query}'")
        
        # Step 2: Query gets repaired
        repair_result = self.repair_system.repair_query(query)
        logger.info(f"Query repaired: '{repair_result['repaired_query']}'")
        
        # Step 3: Search is performed
        search_results = self.search_engine.search(repair_result['repaired_query'], user_id=user_id, top_k=10)
        logger.info(f"Found {len(search_results['results'])} search results")
        
        # Step 4: Results are scored
        if search_results['results']:
            scored_results = self.scoring_system.rank_results(search_results['results'], user_id)
            logger.info(f"Results scored and ranked")
            
            # Step 5: User interacts with results
            for i, result in enumerate(scored_results[:3], 1):
                product_id = result.get('doc_id', result.get('product_id', 0))
                interaction_type = random.choice(['click', 'view', 'purchase'])
                
                self.search_engine.record_interaction(user_id, product_id, interaction_type)
                logger.info(f"  User {interaction_type}ed product {product_id}")
                
                self.demo_stats['interactions_recorded'] += 1
        
        # Step 6: Get personalized recommendations
        recommendations = self.recommendation_engine.get_recommendations(user_id, top_k=5)
        logger.info(f"Generated {len(recommendations)} personalized recommendations")
        
        # Step 7: Display final insights
        logger.info(f"\nEnd-to-End Kintsugi Insights:")
        all_insights = (
            search_results['kintsugi_insights'] + 
            repair_result['kintsugi_insights'] + 
            self.recommendation_engine.get_kintsugi_insights()
        )
        
        for insight in all_insights[:5]:  # Show top 5 insights
            logger.info(f"  {insight}")
    
    def _simulate_user_interactions(self, user_id: str) -> None:
        """Simulate user interactions for demo purposes."""
        # Simulate some random interactions
        for _ in range(random.randint(3, 8)):
            product_id = random.randint(0, 100)  # Random product ID
            interaction_type = random.choice(['click', 'view', 'purchase'])
            rating = random.uniform(3.0, 5.0) if interaction_type == 'purchase' else None
            
            self.recommendation_engine.record_interaction(user_id, product_id, interaction_type, rating)
            self.demo_stats['interactions_recorded'] += 1
    
    def _display_demo_statistics(self) -> None:
        """Display comprehensive demo statistics."""
        logger.info("\n📊 Demo Statistics")
        logger.info("=" * 50)
        
        logger.info(f"Total Demo Time: {self.demo_stats['total_demo_time']:.2f} seconds")
        logger.info(f"Searches Performed: {self.demo_stats['searches_performed']}")
        logger.info(f"Recommendations Generated: {self.demo_stats['recommendations_generated']}")
        logger.info(f"Repairs Performed: {self.demo_stats['repairs_performed']}")
        logger.info(f"Interactions Recorded: {self.demo_stats['interactions_recorded']}")
        
        # Get system statistics
        search_stats = self.search_engine.get_stats()
        repair_stats = self.repair_system.get_repair_statistics()
        scoring_stats = self.scoring_system.get_scoring_statistics()
        
        logger.info(f"\nSystem Statistics:")
        logger.info(f"  Total Products: {search_stats.get('tfidf_stats', {}).get('total_documents', 'N/A')}")
        logger.info(f"  Vocabulary Size: {search_stats.get('tfidf_stats', {}).get('vocabulary_size', 'N/A')}")
        logger.info(f"  Repair Success Rate: {repair_stats.get('success_rate', 0):.1f}%")
        logger.info(f"  Average Unified Score: {scoring_stats.get('overall', {}).get('mean_unified_score', 0):.3f}")
        
        logger.info(f"\n🎉 Demo completed successfully!")
        logger.info(f"💫 The Kintsugi Search + Recommendation Engine is working beautifully!")
    
    def run_quick_demo(self) -> None:
        """Run a quick demonstration of key features."""
        logger.info("⚡ Running Quick Kintsugi Demo...")
        
        # Quick query repair demo
        query = "samsng galaxy s23"
        repair_result = self.repair_system.repair_query(query)
        logger.info(f"Query Repair: '{query}' → '{repair_result['repaired_query']}'")
        
        # Quick search demo
        search_results = self.search_engine.search(repair_result['repaired_query'], top_k=3)
        logger.info(f"Search Results: {len(search_results['results'])} found")
        
        # Quick recommendation demo
        recommendations = self.recommendation_engine.get_recommendations("demo_user", top_k=3)
        logger.info(f"Recommendations: {len(recommendations)} generated")
        
        logger.info("✅ Quick demo completed!")
    
    def run_performance_test(self) -> None:
        """Run performance tests on the system."""
        logger.info("⚡ Running Performance Tests...")
        
        # Test search performance
        start_time = time.time()
        for query in self.demo_queries[:10]:
            self.search_engine.search(query, top_k=10)
        search_time = time.time() - start_time
        
        logger.info(f"Search Performance: {len(self.demo_queries[:10])} searches in {search_time:.3f}s")
        logger.info(f"Average Search Time: {search_time / len(self.demo_queries[:10]):.3f}s per query")
        
        # Test recommendation performance
        start_time = time.time()
        for user_id in self.demo_users:
            self.recommendation_engine.get_recommendations(user_id, top_k=10)
        rec_time = time.time() - start_time
        
        logger.info(f"Recommendation Performance: {len(self.demo_users)} recommendations in {rec_time:.3f}s")
        logger.info(f"Average Recommendation Time: {rec_time / len(self.demo_users):.3f}s per user")
        
        # Test repair performance
        start_time = time.time()
        for query in self.demo_queries:
            self.repair_system.repair_query(query)
        repair_time = time.time() - start_time
        
        logger.info(f"Repair Performance: {len(self.demo_queries)} repairs in {repair_time:.3f}s")
        logger.info(f"Average Repair Time: {repair_time / len(self.demo_queries):.3f}s per query")
        
        logger.info("✅ Performance tests completed!")


def main():
    """Main function to run the demo system."""
    parser = argparse.ArgumentParser(description="Kintsugi Search + Recommendation Engine Demo")
    parser.add_argument('--data', default='data-set.json', help='Path to data file')
    parser.add_argument('--mode', choices=['comprehensive', 'quick', 'performance'], 
                       default='comprehensive', help='Demo mode')
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not Path(args.data).exists():
        logger.error(f"Data file not found: {args.data}")
        return
    
    # Initialize demo system
    demo = KintsugiDemoSystem(args.data)
    
    # Run demo based on mode
    if args.mode == 'comprehensive':
        demo.run_comprehensive_demo()
    elif args.mode == 'quick':
        demo.run_quick_demo()
    elif args.mode == 'performance':
        demo.run_performance_test()


if __name__ == "__main__":
    main()
