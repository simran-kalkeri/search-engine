"""
Data Parser for E-commerce Search Engine
========================================

This module handles loading and parsing of the e-commerce JSON dataset.
It provides a clean interface for accessing product data with proper
error handling and data validation.

Author: Search Engine Implementation
Date: 2025
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ECommerceDataParser:
    """
    A robust parser for e-commerce product data from JSON files.
    
    This class handles data loading, validation, and provides methods
    for accessing product information in a structured way.
    """
    
    def __init__(self, data_file_path: str):
        """
        Initialize the parser with a data file path.
        
        Args:
            data_file_path (str): Path to the JSON data file
        """
        self.data_file_path = Path(data_file_path)
        self.products: List[Dict[str, Any]] = []
        self.load_data()
    
    def load_data(self) -> None:
        """
        Load and validate data from the JSON file.
        
        Raises:
            FileNotFoundError: If the data file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        try:
            if not self.data_file_path.exists():
                raise FileNotFoundError(f"Data file not found: {self.data_file_path}")
            
            with open(self.data_file_path, 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
            
            # Validate that data is a list
            if not isinstance(raw_data, list):
                raise ValueError("Expected JSON data to be a list of products")
            
            # Clean and validate each product
            self.products = []
            for i, product in enumerate(raw_data):
                if isinstance(product, dict):
                    # Add a unique index if not present
                    if 'id' not in product or not product['id']:
                        product['id'] = str(i + 1)
                    
                    # Clean string values
                    cleaned_product = self._clean_product_data(product)
                    self.products.append(cleaned_product)
                else:
                    logger.warning(f"Skipping invalid product at index {i}: not a dictionary")
            
            logger.info(f"Successfully loaded {len(self.products)} products from {self.data_file_path}")
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {self.data_file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            raise
    
    def _clean_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize product data.
        
        Args:
            product (Dict[str, Any]): Raw product data
            
        Returns:
            Dict[str, Any]: Cleaned product data
        """
        cleaned = {}
        
        for key, value in product.items():
            # Skip empty keys
            if not key or not key.strip():
                continue
            
            # Clean the key
            clean_key = key.strip()
            
            # Clean the value
            if value is None:
                cleaned[clean_key] = None
            elif isinstance(value, str):
                # Remove extra whitespace and normalize
                cleaned[clean_key] = value.strip()
            else:
                cleaned[clean_key] = value
        
        return cleaned
    
    def get_all_products(self, repaired: bool = False) -> List[Dict[str, Any]]:
        """
        Get all products from the dataset.
        If repaired=True, returns products with Kintsugi repairs/annotations. Else: broken!
        
        Args:
            repaired (bool): Whether to return repaired products with Kintsugi notes
            
        Returns:
            List[Dict[str, Any]]: List of products
        """
        if not repaired:
            # Return broken products directly (no reprocessing)
            return self.products_broken.copy() if hasattr(self, 'products_broken') else self.products.copy()
        else:
            # Cache repaired products to avoid reprocessing on every call
            if not hasattr(self, '_repaired_cache'):
                import copy
                source_data = self.products_broken if hasattr(self, 'products_broken') else self.products
                self._repaired_cache = [self.repair_product(copy.deepcopy(d)) for d in source_data]
            return self._repaired_cache.copy()
    
    def get_product_by_id(self, product_id: str, repaired: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a specific product by its ID.
        
        Args:
            product_id (str): The product ID to search for
            repaired (bool): Whether to return repaired product with Kintsugi notes
            
        Returns:
            Optional[Dict[str, Any]]: The product if found, None otherwise
        """
        # Efficient lookup without getting all products
        if not repaired:
            source_data = self.products_broken if hasattr(self, 'products_broken') else self.products
            for product in source_data:
                if product.get('id') == str(product_id):
                    return product.copy()
        else:
            # Use cached repaired products if available
            if hasattr(self, '_repaired_cache'):
                for product in self._repaired_cache:
                    if product.get('id') == str(product_id):
                        return product.copy()
            else:
                # Repair only this specific product to avoid processing all
                source_data = self.products_broken if hasattr(self, 'products_broken') else self.products
                for product in source_data:
                    if product.get('id') == str(product_id):
                        import copy
                        return self.repair_product(copy.deepcopy(product))
        return None
    
    def get_products_by_field(self, field_name: str, field_value: Any) -> List[Dict[str, Any]]:
        """
        Get products that have a specific field with a specific value.
        
        Args:
            field_name (str): The field name to search
            field_value (Any): The value to match
            
        Returns:
            List[Dict[str, Any]]: List of matching products
        """
        results = []
        for product in self.products:
            if field_name in product and product[field_name] == field_value:
                results.append(product)
        return results
    
    def get_all_field_names(self) -> set:
        """
        Get all unique field names across all products.
        
        Returns:
            set: Set of all field names
        """
        field_names = set()
        for product in self.products:
            field_names.update(product.keys())
        return field_names
    
    def get_field_values(self, field_name: str) -> set:
        """
        Get all unique values for a specific field.
        
        Args:
            field_name (str): The field name to get values for
            
        Returns:
            set: Set of all unique values for the field
        """
        values = set()
        for product in self.products:
            if field_name in product and product[field_name] is not None:
                values.add(str(product[field_name]))
        return values
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about the dataset.
        
        Returns:
            Dict[str, Any]: Statistics including count, fields, etc.
        """
        if not self.products:
            return {"total_products": 0, "total_fields": 0, "field_names": []}
        
        all_fields = self.get_all_field_names()
        field_counts = {}
        
        for field in all_fields:
            count = sum(1 for product in self.products if field in product and product[field] is not None)
            field_counts[field] = count
        
        return {
            "total_products": len(self.products),
            "total_fields": len(all_fields),
            "field_names": sorted(list(all_fields)),
            "field_coverage": field_counts
        }
    
    def _inject_imperfections(self, product: Dict[str, Any]) -> None:
        """
        Randomly remove fields or corrupt values, simulating 'broken pottery'.
        """
        # Ensure there is a notes field
        product.setdefault(KINTSUGI_NOTES_FIELD, [])

        kbroken_fields = ["Brand", "Features", "Price", "Type", "Color", "Description", "Model Number"]
        text_fields = ["Description", "Features", "Title"]

        # Remove some fields
        import random
        for field in kbroken_fields:
            if field in product and product[field] and random.random() < self.imperfection_rate:
                product[field] = None
                product[KINTSUGI_NOTES_FIELD].append(f"✨ Simulated missing or broken {field}")

        # Add noise to text
        for field in text_fields:
            if field in product and product[field] and isinstance(product[field], str) and random.random() < self.noise_rate:
                product[field] = self._randomly_mess_text(product[field])
                product[KINTSUGI_NOTES_FIELD].append(f"✨ Added imperfection/noise to {field}")

    def _randomly_mess_text(self, text: str) -> str:
        """Add random noise to text."""
        import random
        chars = list(text)
        n = max(1, len(chars) // 12)  # About 8% of chars get messed
        for _ in range(n):
            idx = random.randint(0, len(chars) - 1)
            chars[idx] = random.choice(['*', '_', '', '#', '@', ' '])
        return ''.join(chars)

    def repair_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to repair a broken product using heuristics. Annotate every repair attempt.
        """
        import copy
        item = copy.deepcopy(product)
        notes = item.get(KINTSUGI_NOTES_FIELD, [])

        # Example: Repair Brand from Description (very basic, can be improved)
        if not item.get("Brand") and item.get("Description"):
            guess = self._guess_brand_from_text(item["Description"])
            if guess:
                item["Brand"] = guess
                notes.append("✨ Repaired missing Brand using Description.")

        # Example: Repair Features from Description
        if not item.get("Features") and item.get("Description"):
            guess = self._guess_features_from_text(item["Description"])
            if guess:
                item["Features"] = guess
                notes.append("✨ Repaired missing Features using Description.")

        # Example: Repair Price if a numeric-like string in Description
        if not item.get("Price") and item.get("Description"):
            import re
            price_str = re.search(r"(\d{2,6}(?:\.\d{1,2})?)", item["Description"])
            if price_str:
                item["Price"] = price_str.group(1)
                notes.append("✨ Guessed Price from Description.")

        item[KINTSUGI_NOTES_FIELD] = notes
        return item

    def _guess_brand_from_text(self, text: str) -> Optional[str]:
        """Extract first capitalized word as potential brand."""
        for word in text.split():
            if word.istitle() and len(word) > 2:
                return word
        return None

    def _guess_features_from_text(self, text: str) -> Optional[str]:
        """Naive heuristic: take first line or comma-separated group."""
        if "," in text:
            return text.split(",")[0].strip()
        elif "." in text:
            return text.split(".")[0].strip()
        else:
            return None


def main():
    """
    Demo function to test the parser.
    """
    try:
        # Initialize parser
        parser = ECommerceDataParser('../data-set.json')
        
        # Print basic stats
        stats = parser.get_stats()
        print("=== E-commerce Data Parser Demo ===")
        print(f"Total products: {stats['total_products']}")
        print(f"Total fields: {stats['total_fields']}")
        print(f"Field names: {stats['field_names'][:10]}...")  # Show first 10 fields
        
        # Show a sample product
        if parser.products:
            print("\n=== Sample Product ===")
            sample = parser.products[0]
            for key, value in list(sample.items())[:5]:  # Show first 5 fields
                print(f"{key}: {value}")
            print("...")
        
    except Exception as e:
        print(f"Error in parser demo: {e}")


if __name__ == "__main__":
    main()
