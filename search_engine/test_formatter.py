#!/usr/bin/env python3
"""
Test the formatter to see what the results look like
"""

def test_formatter():
    """Test the formatter."""
    print("🎨 Testing Result Formatter...")
    try:
        from search_engine import KintsugiSearchEngine
        
        engine = KintsugiSearchEngine('data-set.json')
        results = engine.search('iPhone', max_results=1)
        
        print(f"Search results: {len(results['results'])} found")
        if results['results']:
            first_result = results['results'][0]
            print("\nFormatted result structure:")
            for key, value in first_result.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str) and len(sub_value) > 100:
                            print(f"    {sub_key}: {sub_value[:100]}...")
                        else:
                            print(f"    {sub_key}: {sub_value}")
                else:
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
        
        print("✅ Formatter test completed")
        return True
        
    except Exception as e:
        print(f"❌ Formatter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_formatter()
