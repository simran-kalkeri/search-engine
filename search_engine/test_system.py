#!/usr/bin/env python3
"""
Test script for Kintsugi Search + Recommendation Engine
"""

import sys
import traceback

def test_query_repair():
    """Test the query repair system."""
    print("🔧 Testing Query Repair System...")
    try:
        from kintsugi_repair_system import KintsugiRepairSystem
        
        repair_system = KintsugiRepairSystem()
        
        # Test queries with various imperfections
        test_queries = [
            "samsng galaxy s23",           # Typo
            "iphne 14 pro max",            # Typo
            "noise cancelling headphnes",  # Typo
            "wireles blutooth speaker",    # Multiple typos
            "laptp gaming",                # Incomplete + typo
        ]
        
        for query in test_queries:
            print(f"\nOriginal: '{query}'")
            result = repair_system.repair_query(query)
            print(f"Repaired: '{result['repaired_query']}'")
            print(f"Success: {result['repair_successful']}")
            print(f"Quality: {result['quality_score']:.3f}")
            
            if result['repair_notes']:
                print("Repair notes:")
                for note in result['repair_notes']:
                    print(f"  {note}")
        
        print("✅ Query Repair System: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Query Repair System: FAILED - {e}")
        traceback.print_exc()
        return False

def test_polya_urn():
    """Test the Polya Urn Model."""
    print("\n🎯 Testing Polya Urn Model...")
    try:
        from polya_urn_model import PolyaUrnModel
        
        polya_urn = PolyaUrnModel(initial_balls=1, boost_factor=1.5)
        
        # Add some products
        for i in range(1, 6):
            polya_urn.add_product(i)
        
        # Simulate clicks
        for _ in range(20):
            user_id = f"user_{i}"
            product_id = i % 5 + 1
            polya_urn.record_click(product_id, user_id)
        
        # Get boosted products
        boosted = polya_urn.get_boosted_products(3)
        print(f"Top boosted products: {len(boosted)}")
        for product_id, score, stats in boosted:
            print(f"  Product {product_id}: {score:.3f} (clicks: {stats['total_clicks']})")
        
        print("✅ Polya Urn Model: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Polya Urn Model: FAILED - {e}")
        traceback.print_exc()
        return False

def test_cascade_model():
    """Test the Granovetter Cascade Model."""
    print("\n🌊 Testing Granovetter Cascade Model...")
    try:
        from granovetter_cascade import GranovetterCascadeModel
        
        cascade = GranovetterCascadeModel(base_threshold=0.3, cascade_strength=0.6)
        
        # Simulate a small network
        cascade.simulate_cascade_network(num_products=10, num_users=20)
        
        # Simulate adoptions
        for _ in range(30):
            user_id = f"user_{i % 20 + 1}"
            product_id = i % 10 + 1
            cascade.record_adoption(user_id, product_id)
        
        # Get viral products
        viral = cascade.get_viral_products(3)
        print(f"Viral products: {len(viral)}")
        for product_id, score, stats in viral:
            print(f"  Product {product_id}: {score:.3f} (adoptions: {stats['adoption_count']})")
        
        print("✅ Granovetter Cascade Model: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Granovetter Cascade Model: FAILED - {e}")
        traceback.print_exc()
        return False

def test_unified_scoring():
    """Test the unified scoring system."""
    print("\n⚖️ Testing Unified Scoring System...")
    try:
        from unified_scoring_system import UnifiedScoringSystem
        
        scoring_system = UnifiedScoringSystem()
        
        # Test scoring
        result = scoring_system.calculate_unified_score(
            text_score=0.8,
            vector_score=0.7,
            pagerank_score=0.6,
            polya_urn_score=0.5,
            cascade_score=0.4,
            repair_score=0.9,
            freshness_score=0.3
        )
        
        print(f"Unified Score: {result['unified_score']:.3f}")
        print(f"Quality Level: {result['score_quality']['quality_level']}")
        print(f"Balance: {result['score_quality']['balance']:.3f}")
        
        print("✅ Unified Scoring System: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Unified Scoring System: FAILED - {e}")
        traceback.print_exc()
        return False

def test_search_engine():
    """Test the advanced search engine."""
    print("\n🔍 Testing Advanced Search Engine...")
    try:
        from advanced_search_engine import AdvancedSearchEngine
        
        # This will take some time to initialize
        print("Initializing search engine (this may take a moment)...")
        search_engine = AdvancedSearchEngine('data-set.json')
        
        # Test search
        results = search_engine.search("iPhone", top_k=3)
        print(f"Search results: {len(results['results'])} found")
        
        if results['results']:
            for i, result in enumerate(results['results'][:2], 1):
                print(f"  {i}. Score: {result.get('unified_score', 0):.3f}")
                print(f"     Quality: {result.get('kintsugi_quality', 'Unknown')}")
        
        print("✅ Advanced Search Engine: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Advanced Search Engine: FAILED - {e}")
        traceback.print_exc()
        return False

def test_recommendation_engine():
    """Test the recommendation engine."""
    print("\n🎯 Testing Recommendation Engine...")
    try:
        from recommendation_engine import KintsugiRecommendationEngine
        from vector_search import VectorSearchEngine
        
        vector_engine = VectorSearchEngine()
        rec_engine = KintsugiRecommendationEngine(vector_engine)
        
        # Add some sample products
        sample_products = [
            {'id': 1, 'Brand': 'Apple', 'Type': 'Smartphone', 'Features': 'iPhone 14 Pro'},
            {'id': 2, 'Brand': 'Samsung', 'Type': 'Smartphone', 'Features': 'Galaxy S23'},
            {'id': 3, 'Brand': 'Sony', 'Type': 'Headphones', 'Features': 'Noise Cancelling'},
        ]
        
        for product in sample_products:
            rec_engine.add_product(product['id'], product)
        
        # Add user and simulate interactions
        rec_engine.add_user("test_user")
        rec_engine.record_interaction("test_user", 1, "click")
        rec_engine.record_interaction("test_user", 2, "purchase", rating=4.5)
        
        # Get recommendations
        recommendations = rec_engine.get_recommendations("test_user", top_k=3)
        print(f"Recommendations: {len(recommendations)} generated")
        
        for rec in recommendations:
            print(f"  Product {rec['product_id']}: {rec['blended_score']:.3f}")
        
        print("✅ Recommendation Engine: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Recommendation Engine: FAILED - {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🌟 Kintsugi Search + Recommendation Engine - Test Suite")
    print("=" * 60)
    
    tests = [
        test_query_repair,
        test_polya_urn,
        test_cascade_model,
        test_unified_scoring,
        test_recommendation_engine,
        test_search_engine,  # This one takes longest, so put it last
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__}: FAILED - {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Kintsugi system is working beautifully!")
    else:
        print(f"⚠️  {total - passed} tests failed. Some components need repair.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
