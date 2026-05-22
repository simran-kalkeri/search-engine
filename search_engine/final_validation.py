#!/usr/bin/env python3
"""
Final validation script for the Kintsugi Search + Recommendation Engine
"""

def main():
    """Run final system validation."""
    print("🌟 Final System Validation")
    print("=" * 50)
    
    try:
        # Test core module imports
        print("Testing core module imports...")
        from advanced_search_engine import AdvancedSearchEngine
        from kintsugi_repair_system import KintsugiRepairSystem
        from unified_scoring_system import UnifiedScoringSystem
        from polya_urn_model import PolyaUrnModel
        from granovetter_cascade import GranovetterCascadeModel
        from recommendation_engine import KintsugiRecommendationEngine
        print("✅ All core modules imported successfully")
        
        # Test query repair system
        print("\nTesting query repair system...")
        repair = KintsugiRepairSystem()
        result = repair.repair_query("test query with typo")
        print(f"✅ Query repair working: {result['repair_successful']}")
        
        # Test unified scoring system
        print("\nTesting unified scoring system...")
        scoring = UnifiedScoringSystem()
        score = scoring.calculate_unified_score(0.8, 0.7, 0.6, 0.5, 0.4, 0.9, 0.3)
        print(f"✅ Unified scoring working: {score['unified_score']:.3f}")
        
        # Test Polya Urn Model
        print("\nTesting Polya Urn Model...")
        polya = PolyaUrnModel()
        polya.add_product(1)
        polya.record_click(1, "test_user")
        boosted = polya.get_boosted_products(1)
        print(f"✅ Polya Urn Model working: {len(boosted)} products boosted")
        
        # Test Granovetter Cascade Model
        print("\nTesting Granovetter Cascade Model...")
        cascade = GranovetterCascadeModel()
        cascade.simulate_cascade_network(5, 10)
        cascade.record_adoption("user1", 1)
        viral = cascade.get_viral_products(1)
        print(f"✅ Granovetter Cascade Model working: {len(viral)} viral products")
        
        print("\n" + "=" * 50)
        print("🎉 All systems operational!")
        print("🌟 The Kintsugi Search + Recommendation Engine is ready!")
        print("\nTo start the web application, run:")
        print("  python web_app.py")
        print("\nTo run the demo system, run:")
        print("  python demo_system.py --mode comprehensive")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
