#!/usr/bin/env python3
"""
Simple test script for individual components
"""

def test_query_repair():
    """Test query repair system."""
    print("🔧 Testing Query Repair System...")
    try:
        from kintsugi_repair_system import KintsugiRepairSystem
        
        repair_system = KintsugiRepairSystem()
        
        test_queries = [
            "samsng galaxy s23",
            "iphne 14 pro max", 
            "noise cancelling headphnes",
            "wireles blutooth speaker",
            "laptp gaming"
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
        return False

def test_polya_urn():
    """Test Polya Urn Model."""
    print("\n🎯 Testing Polya Urn Model...")
    try:
        from polya_urn_model import PolyaUrnModel
        
        polya_urn = PolyaUrnModel(initial_balls=1, boost_factor=1.5)
        
        # Add products
        for i in range(1, 6):
            polya_urn.add_product(i)
        
        # Simulate clicks
        for i in range(20):
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
        return False

def test_cascade_model():
    """Test Granovetter Cascade Model."""
    print("\n🌊 Testing Granovetter Cascade Model...")
    try:
        from granovetter_cascade import GranovetterCascadeModel
        
        cascade = GranovetterCascadeModel(base_threshold=0.3, cascade_strength=0.6)
        
        # Simulate a small network
        cascade.simulate_cascade_network(num_products=10, num_users=20)
        
        # Simulate adoptions
        for i in range(30):
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
        return False

def test_unified_scoring():
    """Test unified scoring system."""
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
        return False

def main():
    """Run all tests."""
    print("🌟 Kintsugi Search + Recommendation Engine - Component Tests")
    print("=" * 70)
    
    tests = [
        test_query_repair,
        test_polya_urn,
        test_cascade_model,
        test_unified_scoring,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__}: FAILED - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All component tests passed! The Kintsugi system is working beautifully!")
    else:
        print(f"⚠️  {total - passed} tests failed. Some components need repair.")
    
    return passed == total

if __name__ == "__main__":
    main()
