#!/usr/bin/env python3
"""
Test the web application endpoints
"""

import requests
import json
import time

def test_web_app():
    """Test the web application."""
    print("🌐 Testing Web Application...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test search endpoint
        print("\n🔍 Testing search endpoint...")
        search_data = {
            "query": "iPhone",
            "search_type": "comprehensive",
            "page": 1,
            "per_page": 5
        }
        
        response = requests.post(f"{base_url}/search", json=search_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint working")
            print(f"   Query: {data.get('query', 'N/A')}")
            print(f"   Total results: {data.get('total_results', 0)}")
            print(f"   Search time: {data.get('search_time', 0)}s")
            print(f"   Results on page: {len(data.get('results', []))}")
            
            if data.get('results'):
                first_result = data['results'][0]
                print(f"   First result:")
                print(f"     ID: {first_result.get('id', 'N/A')}")
                print(f"     Score: {first_result.get('score', 'N/A')}")
                print(f"     Quality: {first_result.get('kintsugi_quality', 'N/A')}")
                print(f"     Match Type: {first_result.get('match_type', 'N/A')}")
                print(f"     Preview: {first_result.get('preview', 'N/A')}")
                
                if first_result.get('primary_info'):
                    print(f"     Primary Info: {len(first_result['primary_info'])} fields")
                    for key, value in list(first_result['primary_info'].items())[:3]:
                        print(f"       {key}: {value}")
                
                if first_result.get('secondary_info'):
                    print(f"     Secondary Info: {len(first_result['secondary_info'])} fields")
                    for key, value in list(first_result['secondary_info'].items())[:3]:
                        print(f"       {key}: {value}")
                
                if first_result.get('highlights'):
                    print(f"     Highlights: {len(first_result['highlights'])} items")
                    for highlight in first_result['highlights'][:2]:
                        print(f"       {highlight}")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test recommendations endpoint
        print("\n🎯 Testing recommendations endpoint...")
        rec_data = {
            "user_id": "test_user_123",
            "top_k": 5
        }
        
        response = requests.post(f"{base_url}/recommendations", json=rec_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendations endpoint working")
            print(f"   User ID: {data.get('user_id', 'N/A')}")
            print(f"   Total recommendations: {data.get('total_recommendations', 0)}")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            
            if data.get('recommendations'):
                first_rec = data['recommendations'][0]
                print(f"   First recommendation:")
                print(f"     Title: {first_rec.get('title', 'N/A')}")
                print(f"     Brand: {first_rec.get('brand', 'N/A')}")
                print(f"     Type: {first_rec.get('type', 'N/A')}")
                print(f"     Price: {first_rec.get('price', 'N/A')}")
        else:
            print(f"❌ Recommendations endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test analytics endpoint
        print("\n📊 Testing analytics endpoint...")
        response = requests.get(f"{base_url}/analytics")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics endpoint working")
            print(f"   Search analytics available: {'search_analytics' in data}")
            print(f"   Kintsugi insights: {len(data.get('kintsugi_insights', []))}")
        else:
            print(f"❌ Analytics endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test interaction endpoint
        print("\n👆 Testing interaction endpoint...")
        interaction_data = {
            "user_id": "test_user_123",
            "product_id": "test_product_456",
            "interaction_type": "click"
        }
        
        response = requests.post(f"{base_url}/interaction", json=interaction_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Interaction endpoint working")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Message: {data.get('message', 'N/A')}")
        else:
            print(f"❌ Interaction endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        print("\n🎉 Web application testing completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web application. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Web application test failed: {e}")
        return False

if __name__ == "__main__":
    print("🌟 Testing Kintsugi Search Engine Web Application")
    print("=" * 60)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    success = test_web_app()
    
    if success:
        print("\n✅ All tests passed! The web application is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the web application.")
