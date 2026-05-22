"""
Original Web UI for Kintsugi E-commerce Search Engine
====================================================

A Flask-based web interface for the Kintsugi search engine with
fuzzy matching, highlighting, and Kintsugi-inspired design.

Author: Search Engine Implementation
Date: 2025
"""

from flask import Flask, render_template, request, jsonify, session
import json
import time
import random
from pathlib import Path

# Import the original search engine
from search_engine import KintsugiSearchEngine

app = Flask(__name__)
app.secret_key = 'kintsugi_search_engine_secret_key_2025'

# Initialize the search engine
print("🔍 Initializing Kintsugi Search Engine...")
search_engine = KintsugiSearchEngine('data-set.json')
print("✅ Search engine ready!")

@app.route('/')
def index():
    """Main search page."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'comprehensive')
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        user_id = data.get('user_id', session.get('user_id', f'user_{random.randint(1000, 9999)}'))
        
        # Store user ID in session
        session['user_id'] = user_id
        
        if not query:
            return jsonify({
                'error': 'Please enter a search query',
                'results': [],
                'total_results': 0,
                'page': 1,
                'per_page': per_page,
                'total_pages': 0
            })
        
        # Perform search
        start_time = time.time()
        search_results = search_engine.search(query, search_type=search_type, max_results=1000)
        search_time = time.time() - start_time
        
        # Calculate pagination
        total_results = len(search_results['results'])
        total_pages = (total_results + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        # Get results for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_results = search_results['results'][start_idx:end_idx]
        
        return jsonify({
            'query': query,
            'search_type': search_type,
            'total_results': total_results,
            'search_time': round(search_time, 3),
            'kintsugi_insights': search_results.get('kintsugi_insights', []),
            'results': page_results,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Search error: {str(e)}',
            'results': [],
            'total_results': 0
        })

@app.route('/suggestions', methods=['POST'])
def suggestions():
    """Handle suggestion requests."""
    try:
        data = request.get_json()
        partial_query = data.get('query', '').strip()
        
        if len(partial_query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = search_engine.get_search_suggestions(partial_query)
        return jsonify({'suggestions': suggestions[:5]})  # Return top 5
    
    except Exception as e:
        return jsonify({'suggestions': []})

@app.route('/field_suggestions', methods=['POST'])
def field_suggestions():
    """Handle field suggestion requests."""
    try:
        data = request.get_json()
        field_name = data.get('field', '').strip()
        
        if not field_name:
            return jsonify({'suggestions': []})
        
        suggestions = search_engine.get_field_suggestions(field_name)
        return jsonify({'suggestions': suggestions[:10]})  # Return top 10
    
    except Exception as e:
        return jsonify({'suggestions': []})

@app.route('/recommendations', methods=['POST'])
def recommendations():
    """Get recommendations for a user."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', session.get('user_id', f'user_{random.randint(1000, 9999)}'))
        top_k = data.get('top_k', 10)
        
        # Store user ID in session
        session['user_id'] = user_id
        
        # Get recommendations (basic implementation)
        recommendations = search_engine.get_recommendations(user_id, top_k)
        
        return jsonify({
            'user_id': user_id,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'kintsugi_insights': [
                "🎯 Recommendations based on your search history",
                "✨ Personalized for your preferences",
                "💫 Discover new products you might love"
            ]
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Recommendation error: {str(e)}',
            'recommendations': [],
            'total_recommendations': 0
        })

@app.route('/interaction', methods=['POST'])
def record_interaction():
    """Record user interaction with a product."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', session.get('user_id', f'user_{random.randint(1000, 9999)}'))
        product_id = data.get('product_id')
        interaction_type = data.get('interaction_type', 'click')
        
        if not product_id:
            return jsonify({'error': 'Product ID required'})
        
        # Record interaction
        search_engine.record_interaction(user_id, product_id, interaction_type)
        
        return jsonify({
            'success': True,
            'message': f'Recorded {interaction_type} for product {product_id}',
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Interaction recording error: {str(e)}'})

@app.route('/product/<product_id>', methods=['GET'])
def product_details(product_id):
    """Get detailed information about a specific product."""
    try:
        # Record this interaction for recommendations
        user_id = session.get('user_id', f'user_{random.randint(1000, 9999)}')
        session['user_id'] = user_id
        
        # Record the product view interaction
        try:
            search_engine.record_interaction(user_id, product_id, 'view')
        except Exception as e:
            print(f"Warning: Could not record interaction: {e}")
        
        # Use the search engine's method to get product details
        result = search_engine.get_product_details(product_id)
        
        if not result['success']:
            return jsonify(result), 404
        
        # Add additional web-specific insights
        result['kintsugi_insights'].extend([
            "🔍 Click-through recorded for recommendations",
            "🌐 Accessed via web interface",
            f"👤 User ID: {user_id}"
        ])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Product details error: {str(e)}',
            'product_id': product_id,
            'success': False
        }), 500

@app.route('/analytics', methods=['GET'])
def analytics():
    """Get search analytics."""
    try:
        stats = search_engine.get_stats()
        
        return jsonify({
            'search_analytics': stats,
            'kintsugi_insights': [
                "🔍 Search engine is working harmoniously",
                "📊 Analytics show healthy search patterns",
                "✨ System is learning and improving"
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Analytics error: {str(e)}'})

@app.route('/stats')
def stats():
    """Get search engine statistics."""
    try:
        stats = search_engine.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("🌟 Starting Kintsugi Search Engine Web Interface...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
