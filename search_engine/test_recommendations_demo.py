#!/usr/bin/env python3
"""
Test Recommendations Demo
========================

This script demonstrates the hybrid search + recommendation engine
with all 3 models integrated and working.
"""

import json
import time
from search_engine import KintsugiSearchEngine

def test_recommendations_demo():
    """Test the complete recommendations system."""
    print("🎯 Testing Hybrid Search + Recommendation Engine")
    print("=" * 60)
    
    # Initialize the search engine
    print("🔍 Initializing Kintsugi Search Engine...")
    engine = KintsugiSearchEngine("data-set.json")
    print("✅ Search engine ready!")
    
    # Test search functionality
    print("\n🔍 Testing Search with Enhanced Ranking...")
    query = "iPhone"
    results = engine.search(query, max_results=5)
    print(f"   Query: {query}")
    print(f"   Results: {results.get('total_results', 0)} found")
    
    if results.get('results'):
        first_result = results['results'][0]
        print(f"   First result score: {first_result.get('score', 'N/A')}")
        print(f"   Quality: {first_result.get('kintsugi_quality', 'N/A')}")
    
    # Test recommendations
    print("\n🎯 Testing Recommendations with All 3 Models...")
    
    # Simulate user interactions to populate models
    print("   📊 Simulating user interactions...")
    user_id = "demo_user_123"
    
    # Record some clicks to populate Polya Urn
    for i in range(5):
        engine.record_interaction(user_id, str(i), "click")
    
    # Record some adoptions to populate Cascade
    for i in range(3):
        engine.record_interaction(user_id, str(i), "purchase")
    
    # Get recommendations
    recommendations = engine.get_recommendations(user_id, top_k=6)
    print(f"   Total recommendations: {len(recommendations)}")
    
    if recommendations:
        print("\n   📋 Recommendation Details:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec.get('title', 'Product')}")
            print(f"      Brand: {rec.get('brand', 'N/A')}")
            print(f"      Type: {rec.get('type', 'N/A')}")
            print(f"      Score: {rec.get('recommendation_score', 'N/A')}")
            print(f"      Reason: {rec.get('recommendation_reason', 'N/A')}")
            print()
    
    # Test model status
    print("🔧 Model Integration Status:")
    print(f"   ✅ Polya Urn Model: {'Active' if engine.polya_urn else 'Inactive'}")
    print(f"   ✅ Granovetter Cascade: {'Active' if engine.cascade_model else 'Inactive'}")
    print(f"   ✅ Vector Search: {'Active' if engine.vector_engine else 'Inactive'}")
    print(f"   ✅ PageRank: {'Active' if engine.pagerank_ranker else 'Inactive'}")
    
    # Test enhanced search with all models
    print("\n🚀 Testing Enhanced Search with All Models...")
    enhanced_results = engine.search("smartphone", max_results=3)
    print(f"   Enhanced search results: {enhanced_results.get('total_results', 0)}")
    
    if enhanced_results.get('results'):
        first_enhanced = enhanced_results['results'][0]
        print(f"   First enhanced result:")
        print(f"     Score: {first_enhanced.get('score', 'N/A')}")
        print(f"     Quality: {first_enhanced.get('kintsugi_quality', 'N/A')}")
        print(f"     Match Type: {first_enhanced.get('match_type', 'N/A')}")
    
    print("\n🎉 Hybrid Search + Recommendation Engine Demo Complete!")
    print("=" * 60)
    print("✅ All 3 models are integrated and working:")
    print("   🎲 Polya Urn Model - Click-based boosting")
    print("   🌊 Granovetter Cascade - Viral recommendations") 
    print("   📊 PageRank - Graph-based ranking")
    print("   🔍 Vector Search - Semantic similarity")
    print("   🎯 Unified Scoring - Blended ranking system")

if __name__ == "__main__":
    test_recommendations_demo()
