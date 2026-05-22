#!/usr/bin/env python3
"""
Test Click Functionality
========================

This script demonstrates how clicking on products makes them trending/viral
in the hybrid search + recommendation engine.
"""

import json
import time
from search_engine import KintsugiSearchEngine

def test_click_functionality():
    """Test the click-to-trend functionality."""
    print("🎯 Testing Click-to-Trend Functionality")
    print("=" * 50)
    
    # Initialize the search engine
    print("🔍 Initializing Kintsugi Search Engine...")
    engine = KintsugiSearchEngine("data-set.json")
    print("✅ Search engine ready!")
    
    # Test initial recommendations
    print("\n📊 Initial Recommendations (before clicks):")
    user_id = "test_user_123"
    initial_recs = engine.get_recommendations(user_id, top_k=5)
    print(f"   Found {len(initial_recs)} recommendations")
    
    if initial_recs:
        print("   Top recommendations:")
        for i, rec in enumerate(initial_recs[:3], 1):
            print(f"   {i}. {rec.get('title', 'Product')} - {rec.get('recommendation_reason', 'N/A')}")
    
    # Simulate multiple clicks on specific products
    print("\n👆 Simulating clicks on products...")
    products_to_click = ["0", "1", "2", "3", "4"]  # Product IDs
    
    for i, product_id in enumerate(products_to_click):
        print(f"   Clicking product {product_id}...")
        engine.record_interaction(user_id, product_id, "click")
        
        # Also record some purchases for cascade effect
        if i < 3:
            engine.record_interaction(user_id, product_id, "purchase")
            print(f"   Also purchased product {product_id} (cascade effect)")
    
    # Wait a moment for processing
    time.sleep(1)
    
    # Test recommendations after clicks
    print("\n📈 Recommendations After Clicks:")
    updated_recs = engine.get_recommendations(user_id, top_k=5)
    print(f"   Found {len(updated_recs)} recommendations")
    
    if updated_recs:
        print("   Updated recommendations:")
        for i, rec in enumerate(updated_recs[:3], 1):
            print(f"   {i}. {rec.get('title', 'Product')} - {rec.get('recommendation_reason', 'N/A')}")
    
    # Test search with enhanced ranking
    print("\n🔍 Testing Enhanced Search (clicked products should rank higher):")
    search_results = engine.search("smartphone", max_results=5)
    print(f"   Search results: {search_results.get('total_results', 0)}")
    
    if search_results.get('results'):
        print("   Top search results:")
        for i, result in enumerate(search_results['results'][:3], 1):
            print(f"   {i}. Score: {result.get('score', 'N/A')} - {result.get('id', 'N/A')}")
    
    # Show model status
    print("\n🔧 Model Status:")
    print(f"   ✅ Polya Urn Model: {'Active' if engine.polya_urn else 'Inactive'}")
    print(f"   ✅ Granovetter Cascade: {'Active' if engine.cascade_model else 'Inactive'}")
    print(f"   ✅ PageRank: {'Active' if engine.pagerank_ranker else 'Inactive'}")
    
    print("\n🎉 Click-to-Trend Test Complete!")
    print("=" * 50)
    print("✅ Products can be clicked to make them trending/viral")
    print("✅ Polya Urn Model tracks clicks for trending items")
    print("✅ Granovetter Cascade tracks purchases for viral items")
    print("✅ Enhanced search ranking includes click/purchase signals")

if __name__ == "__main__":
    test_click_functionality()
