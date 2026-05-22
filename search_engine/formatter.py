"""
Result Formatter for Kintsugi Search Engine
==========================================

This module handles the formatting and display of search results
in a clean, user-friendly format with Kintsugi-inspired highlighting.

Author: Search Engine Implementation
Date: 2025
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from fuzzy_matcher import KintsugiFuzzyMatcher


class KintsugiResultFormatter:
    """
    Formats search results with Kintsugi-inspired highlighting and clean display.
    
    This class transforms raw search results into user-friendly formats that
    emphasize the Kintsugi concept of treating "imperfect" matches as valuable.
    """
    
    def __init__(self):
        """Initialize the formatter."""
        self.fuzzy_matcher = KintsugiFuzzyMatcher()
        
        # Kintsugi quality symbols and descriptions
        self.quality_markers = {
            'perfect': ('✨', 'Perfect Match'),
            'excellent': ('🌟', 'Kintsugi Match – excellent'),
            'good': ('⭐', 'Kintsugi Match – near'),
            'fair': ('💫', 'Kintsugi Match – partial'),
            'poor': ('✨', 'Kintsugi Match – weak')
        }
        
        # Primary fields to display prominently
        self.primary_fields = ['id', 'Brand', 'Type', 'Model Number', 'Color', 'Price']
        
        # Secondary fields to display if available
        self.secondary_fields = [
            'Features', 'Description', 'Specifications', 'Key Features', 'Other Features',
            'Weight', 'Dimensions', 'Warranty', 'Sales Package', 'In The Box',
            'Display', 'Battery', 'Connectivity', 'Bluetooth', 'WiFi', 'USB',
            'Material', 'Finish', 'Size', 'Capacity', 'Power', 'Voltage',
            'Durability', 'Water Resistant', 'Dust Resistant', 'Weather Resistant'
        ]
        
        # Fields to use for preview generation
        self.preview_fields = [
            'Brand', 'Type', 'Model Number', 'Color', 'Features', 
            'Description', 'Specifications', 'Key Features', 'Other Features'
        ]
    
    def format_result(self, result: Dict[str, Any], query: str = "") -> Dict[str, Any]:
        """
        Format a single search result with Kintsugi styling.
        
        Args:
            result (Dict[str, Any]): Raw search result
            query (str): Original search query for highlighting
            
        Returns:
            Dict[str, Any]: Formatted result with clean display
        """
        product = result['document']
        
        # Extract all available information
        formatted = {
            'id': product.get('id', result.get('doc_id', 'N/A')),
            'score': self._format_score(result['score'], result['kintsugi_quality']),
            'primary_info': self._extract_primary_info(product),
            'secondary_info': self._extract_secondary_info(product),
            'all_features': self._extract_all_features(product),
            'highlights': self._extract_highlights(product, query, result.get('matches', [])),
            'preview': self._generate_preview(product),
            'kintsugi_quality': result['kintsugi_quality'],
            'match_type': result['match_type']
        }
        
        return formatted
    
    def _format_score(self, score: float, quality: str) -> str:
        """
        Format score with Kintsugi marker.
        
        Args:
            score (float): Raw score
            quality (str): Kintsugi quality level
            
        Returns:
            str: Formatted score with marker
        """
        symbol, description = self.quality_markers.get(quality, ('✨', 'Match'))
        return f"{score:.1f} {symbol} ({description})"
    
    def _get_field_value(self, product: Dict[str, Any], field: str) -> str:
        """
        Get a field value from product, handling missing values gracefully.
        
        Args:
            product (Dict[str, Any]): Product data
            field (str): Field name
            
        Returns:
            str: Field value or 'Not specified'
        """
        value = product.get(field, '')
        if not value or value.strip() == '':
            return 'Not specified'
        return str(value).strip()
    
    def _extract_primary_info(self, product: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract primary information (ID, Brand, Type, Model, Color, Price).
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            Dict[str, str]: Primary information
        """
        primary_info = {}
        for field in self.primary_fields:
            value = self._get_field_value(product, field)
            if value != 'Not specified':
                primary_info[field] = value
        return primary_info
    
    def _extract_secondary_info(self, product: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract secondary information (Features, Weight, etc.).
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            Dict[str, str]: Secondary information
        """
        secondary_info = {}
        for field in self.secondary_fields:
            value = self._get_field_value(product, field)
            if value != 'Not specified':
                secondary_info[field] = value
        return secondary_info
    
    def _extract_all_features(self, product: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract all available features from the product.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            Dict[str, str]: All available features
        """
        all_features = {}
        for key, value in product.items():
            if value and str(value).strip() and key != 'id':
                all_features[key] = str(value).strip()
        return all_features
    
    def _extract_highlights(self, product: Dict[str, Any], query: str, 
                           matches: List[Dict[str, Any]]) -> List[str]:
        """
        Extract and format Kintsugi repair highlights.
        
        Args:
            product (Dict[str, Any]): Product data
            query (str): Original search query
            matches (List[Dict[str, Any]]): Fuzzy matches
            
        Returns:
            List[str]: List of highlighted repairs
        """
        highlights = []
        
        if not query:
            return highlights
        
        # Find fuzzy matches in key fields
        key_texts = []
        for field in self.primary_fields + self.secondary_fields:
            value = product.get(field, '')
            if value and str(value).strip():
                key_texts.append(str(value).strip())
        
        # Combine all searchable text
        searchable_text = ' '.join(key_texts)
        
        # Find matches using fuzzy matcher
        fuzzy_matches = self.fuzzy_matcher.find_matches(query, searchable_text, threshold=0.6)
        
        # Extract unique repairs
        seen_repairs = set()
        for match in fuzzy_matches:
            if match['kintsugi_quality'] in ['fair', 'good', 'excellent']:
                repair_text = match['matched_text']
                if repair_text not in seen_repairs and len(repair_text) > 2:
                    highlights.append(f"💫 '{repair_text}' → found in {self._find_field_for_text(product, repair_text)}")
                    seen_repairs.add(repair_text)
        
        # Add original query repairs if found
        if query.lower() not in searchable_text.lower():
            # Find what was actually matched
            for match in fuzzy_matches:
                if match['kintsugi_quality'] in ['good', 'excellent']:
                    highlights.append(f"✨ Query '{query}' → matched '{match['matched_text']}'")
                    break
        
        return highlights[:3]  # Limit to top 3 highlights
    
    def _find_field_for_text(self, product: Dict[str, Any], text: str) -> str:
        """
        Find which field contains the given text.
        
        Args:
            product (Dict[str, Any]): Product data
            text (str): Text to find
            
        Returns:
            str: Field name containing the text
        """
        for field in self.primary_fields + self.secondary_fields:
            value = product.get(field, '')
            if value and text.lower() in str(value).lower():
                return field
        return 'product details'
    
    def _generate_preview(self, product: Dict[str, Any]) -> str:
        """
        Generate a short, readable preview of the product.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            str: Short preview description
        """
        preview_parts = []
        
        # Add brand and type
        brand = self._get_field_value(product, 'Brand')
        product_type = self._get_field_value(product, 'Type')
        
        if brand != 'Not specified' and product_type != 'Not specified':
            preview_parts.append(f"{brand} {product_type}")
        elif brand != 'Not specified':
            preview_parts.append(brand)
        elif product_type != 'Not specified':
            preview_parts.append(product_type)
        
        # Add model if available
        model = self._get_field_value(product, 'Model Number')
        if model != 'Not specified':
            preview_parts.append(f"Model: {model}")
        
        # Add color if available
        color = self._get_field_value(product, 'Color')
        if color != 'Not specified':
            preview_parts.append(f"Color: {color}")
        
        # Add key features
        features = self._extract_key_features(product)
        if features:
            preview_parts.append(f"Features: {', '.join(features[:3])}")
        
        # Join parts with proper formatting
        if preview_parts:
            preview = ' • '.join(preview_parts)
            # Limit length
            if len(preview) > 150:
                preview = preview[:147] + "..."
            return preview
        else:
            return "Product details available"
    
    def _extract_key_features(self, product: Dict[str, Any]) -> List[str]:
        """
        Extract key features from product data.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            List[str]: List of key features
        """
        features = []
        
        # Look for common feature fields
        feature_fields = ['Features', 'Key Features', 'Specifications', 'Description']
        
        for field in feature_fields:
            value = product.get(field, '')
            if value and str(value).strip():
                # Split by common separators and clean up
                feature_text = str(value).strip()
                # Split by commas, semicolons, or newlines
                parts = re.split(r'[,;]\s*|\n', feature_text)
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 5 and len(part) < 50:
                        features.append(part)
        
        return features[:5]  # Limit to top 5 features
    
    def format_results_list(self, results: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
        """
        Format a list of search results.
        
        Args:
            results (List[Dict[str, Any]]): List of raw results
            query (str): Original search query
            
        Returns:
            List[Dict[str, Any]]: List of formatted results
        """
        formatted_results = []
        seen_products = set()  # Track duplicates by key fields
        
        for result in results:
            product = result['document']
            
            # Create a key to identify duplicates
            duplicate_key = self._create_duplicate_key(product)
            if duplicate_key in seen_products:
                continue  # Skip duplicate
            
            seen_products.add(duplicate_key)
            
            # Format the result
            formatted_result = self.format_result(result, query)
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _create_duplicate_key(self, product: Dict[str, Any]) -> str:
        """
        Create a key to identify duplicate products.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            str: Duplicate key
        """
        key_parts = []
        
        # Use brand, type, and model to identify duplicates
        for field in ['Brand', 'Type', 'Model Number']:
            value = product.get(field, '')
            if value and str(value).strip():
                key_parts.append(str(value).strip().lower())
        
        return '|'.join(key_parts) if key_parts else product.get('id', 'unknown')
    
    def print_formatted_result(self, formatted_result: Dict[str, Any], index: int = 1) -> None:
        """
        Print a single formatted result to console.
        
        Args:
            formatted_result (Dict[str, Any]): Formatted result
            index (int): Result index
        """
        print(f"\n📦 Result {index}:")
        print(f"   {formatted_result['score']}")
        
        # Display primary information
        primary_info = formatted_result['primary_info']
        if primary_info:
            print(f"   🏷️  Primary Info:")
            for field, value in primary_info.items():
                print(f"     {field}: {value}")
        
        # Display secondary information
        secondary_info = formatted_result['secondary_info']
        if secondary_info:
            print(f"   🔧 Features:")
            for field, value in list(secondary_info.items())[:8]:  # Show top 8 features
                print(f"     {field}: {value}")
            if len(secondary_info) > 8:
                print(f"     ... and {len(secondary_info) - 8} more features")
        
        # Display highlights
        if formatted_result['highlights']:
            print(f"   ✨ Kintsugi Repairs:")
            for highlight in formatted_result['highlights']:
                print(f"     {highlight}")
        
        # Display preview
        print(f"   📝 Preview: {formatted_result['preview']}")
    
    def print_formatted_results(self, results: List[Dict[str, Any]], query: str = "", 
                              max_results: int = 10) -> None:
        """
        Print formatted results to console.
        
        Args:
            results (List[Dict[str, Any]]): List of raw results
            query (str): Original search query
            max_results (int): Maximum results to display
        """
        formatted_results = self.format_results_list(results, query)
        
        if not formatted_results:
            print("😔 No results found. Try a different query or check for typos.")
            return
        
        print(f"\n📊 Found {len(formatted_results)} unique results")
        
        # Display results
        for i, formatted_result in enumerate(formatted_results[:max_results], 1):
            self.print_formatted_result(formatted_result, i)
        
        if len(formatted_results) > max_results:
            print(f"\n... and {len(formatted_results) - max_results} more results")


def main():
    """
    Demo function to test the formatter.
    """
    formatter = KintsugiResultFormatter()
    
    # Test with sample data
    sample_result = {
        'document': {
            'id': '123',
            'Brand': 'Samsung',
            'Type': 'Smartphone',
            'Model Number': 'Galaxy S23',
            'Color': 'Black',
            'Price': '$999',
            'Features': '5G, 128GB, OLED Display'
        },
        'score': 16.6,
        'kintsugi_quality': 'good',
        'match_type': 'kintsugi_near',
        'matches': []
    }
    
    print("=== Kintsugi Result Formatter Demo ===")
    formatted = formatter.format_result(sample_result, "samsng galaxy")
    formatter.print_formatted_result(formatted, 1)


if __name__ == "__main__":
    main()
