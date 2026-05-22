"""
Kintsugi Data Enhancer
=====================

This module enhances the dataset with Kintsugi-inspired imperfections:
- Randomly missing fields (brand, features, price)
- Noisy entries with typos and variations
- Broken text that needs repair
- Simulates real-world data quality issues

Author: Search Engine Implementation
Date: 2025
"""

import json
import random
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KintsugiDataEnhancer:
    """
    Enhances e-commerce data with Kintsugi-inspired imperfections.
    
    This class simulates real-world data quality issues by introducing
    missing fields, typos, and broken text that the search engine
    must repair and work with.
    """
    
    def __init__(self):
        """Initialize the data enhancer."""
        # Common typos and variations for e-commerce terms
        self.typo_patterns = {
            'samsung': ['samsng', 'samsun', 'samsug', 'samsunng'],
            'iphone': ['iphne', 'iphne', 'iphonee', 'iphne'],
            'galaxy': ['galxy', 'galax', 'galaxy', 'galaxyy'],
            'headphones': ['headphnes', 'headphons', 'headphones', 'headphnes'],
            'wireless': ['wireles', 'wireless', 'wireles', 'wirelesss'],
            'bluetooth': ['blutooth', 'bluetooth', 'blutooth', 'bluetooth'],
            'laptop': ['laptp', 'lapto', 'laptop', 'laptopp'],
            'smartphone': ['smartphne', 'smartphn', 'smartphone', 'smartphne'],
            'display': ['disply', 'displa', 'display', 'disply'],
            'battery': ['batery', 'battry', 'battery', 'batery'],
            'camera': ['camra', 'camer', 'camera', 'camra'],
            'storage': ['storag', 'storag', 'storage', 'storag'],
            'memory': ['memry', 'memor', 'memory', 'memry'],
            'processor': ['procesor', 'procesor', 'processor', 'procesor'],
            'graphics': ['graphcs', 'graphic', 'graphics', 'graphcs'],
            'connectivity': ['connectivty', 'connectivty', 'connectivity', 'connectivty'],
            'durability': ['durabilty', 'durabilty', 'durability', 'durabilty'],
            'waterproof': ['waterprof', 'waterprof', 'waterproof', 'waterprof'],
            'noise': ['nois', 'nois', 'noise', 'nois'],
            'cancelling': ['canceling', 'canceling', 'cancelling', 'canceling']
        }
        
        # Fields that can be randomly missing
        self.missing_field_candidates = [
            'Brand', 'Color', 'Price', 'Features', 'Specifications',
            'Key Features', 'Other Features', 'Weight', 'Dimensions',
            'Warranty', 'Display', 'Battery', 'Connectivity', 'Bluetooth',
            'WiFi', 'USB', 'Material', 'Finish', 'Size', 'Capacity',
            'Power', 'Voltage', 'Durability', 'Water Resistant',
            'Dust Resistant', 'Weather Resistant'
        ]
        
        # Fields that can have noisy/typo variations
        self.noisy_field_candidates = [
            'Brand', 'Type', 'Model Number', 'Features', 'Description',
            'Specifications', 'Key Features', 'Other Features'
        ]
        
        # Common broken text patterns
        self.broken_text_patterns = [
            r'\s+',  # Multiple spaces
            r'[^\w\s\-\.]',  # Special characters
            r'\b(\w+)\s+\1\b',  # Repeated words
            r'(\w+)\s*,\s*(\w+)\s*,\s*(\w+)',  # Comma-separated lists
        ]
        
        # Repair patterns for broken text
        self.repair_patterns = {
            r'\s+': ' ',  # Multiple spaces to single space
            r'[^\w\s\-\.]': ' ',  # Special characters to space
            r'\b(\w+)\s+\1\b': r'\1',  # Remove repeated words
            r'(\w+)\s*,\s*(\w+)\s*,\s*(\w+)': r'\1, \2, \3',  # Clean comma lists
        }
    
    def enhance_dataset(self, input_file: str, output_file: str, 
                       imperfection_rate: float = 0.3) -> None:
        """
        Enhance dataset with Kintsugi imperfections.
        
        Args:
            input_file (str): Path to input JSON file
            output_file (str): Path to output JSON file
            imperfection_rate (float): Rate of imperfections to introduce (0.0-1.0)
        """
        logger.info(f"Loading dataset from {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        logger.info(f"Enhancing {len(products)} products with {imperfection_rate*100}% imperfection rate")
        
        enhanced_products = []
        for i, product in enumerate(products):
            enhanced_product = self._enhance_product(product, imperfection_rate)
            enhanced_products.append(enhanced_product)
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Enhanced {i + 1} products...")
        
        # Save enhanced dataset
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_products, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enhanced dataset saved to {output_file}")
    
    def _enhance_product(self, product: Dict[str, Any], 
                        imperfection_rate: float) -> Dict[str, Any]:
        """
        Enhance a single product with Kintsugi imperfections.
        
        Args:
            product (Dict[str, Any]): Original product
            imperfection_rate (float): Rate of imperfections
            
        Returns:
            Dict[str, Any]: Enhanced product with imperfections
        """
        enhanced = product.copy()
        
        # Add Kintsugi metadata
        enhanced['_kintsugi_metadata'] = {
            'original_quality': 'perfect',
            'imperfections_introduced': [],
            'repair_notes': []
        }
        
        # Randomly introduce missing fields
        if random.random() < imperfection_rate * 0.4:  # 40% of imperfection rate
            missing_fields = self._introduce_missing_fields(enhanced)
            enhanced['_kintsugi_metadata']['imperfections_introduced'].extend(missing_fields)
        
        # Randomly introduce typos and noise
        if random.random() < imperfection_rate * 0.6:  # 60% of imperfection rate
            noisy_fields = self._introduce_noise(enhanced)
            enhanced['_kintsugi_metadata']['imperfections_introduced'].extend(noisy_fields)
        
        # Randomly introduce broken text
        if random.random() < imperfection_rate * 0.3:  # 30% of imperfection rate
            broken_fields = self._introduce_broken_text(enhanced)
            enhanced['_kintsugi_metadata']['imperfections_introduced'].extend(broken_fields)
        
        # Add repair suggestions
        enhanced['_kintsugi_metadata']['repair_notes'] = self._generate_repair_notes(enhanced)
        
        return enhanced
    
    def _introduce_missing_fields(self, product: Dict[str, Any]) -> List[str]:
        """Introduce missing fields randomly."""
        missing_fields = []
        num_missing = random.randint(1, 3)  # 1-3 missing fields
        
        candidates = [f for f in self.missing_field_candidates if f in product]
        if not candidates:
            return missing_fields
        
        selected_fields = random.sample(candidates, min(num_missing, len(candidates)))
        
        for field in selected_fields:
            if field in product:
                # Store original value for repair notes
                original_value = product[field]
                product[field] = None
                missing_fields.append(f"Missing {field}: {original_value}")
        
        return missing_fields
    
    def _introduce_noise(self, product: Dict[str, Any]) -> List[str]:
        """Introduce typos and noise in text fields."""
        noisy_fields = []
        
        for field in self.noisy_field_candidates:
            if field in product and product[field] and isinstance(product[field], str):
                original_value = product[field]
                noisy_value = self._add_typos(original_value)
                
                if noisy_value != original_value:
                    product[field] = noisy_value
                    noisy_fields.append(f"Typo in {field}: '{original_value}' → '{noisy_value}'")
        
        return noisy_fields
    
    def _add_typos(self, text: str) -> str:
        """Add typos to text based on common patterns."""
        words = text.split()
        modified_words = []
        
        for word in words:
            word_lower = word.lower()
            
            # Check if this word has known typo patterns
            if word_lower in self.typo_patterns:
                if random.random() < 0.3:  # 30% chance to introduce typo
                    typo_options = self.typo_patterns[word_lower]
                    # Choose a typo that's different from original
                    typo_options = [t for t in typo_options if t != word_lower]
                    if typo_options:
                        new_word = random.choice(typo_options)
                        # Preserve original case
                        if word.isupper():
                            new_word = new_word.upper()
                        elif word.istitle():
                            new_word = new_word.title()
                        modified_words.append(new_word)
                    else:
                        modified_words.append(word)
                else:
                    modified_words.append(word)
            else:
                # Randomly introduce other typos
                if random.random() < 0.05 and len(word) > 3:  # 5% chance for other typos
                    modified_word = self._random_typo(word)
                    modified_words.append(modified_word)
                else:
                    modified_words.append(word)
        
        return ' '.join(modified_words)
    
    def _random_typo(self, word: str) -> str:
        """Introduce random typos to a word."""
        if len(word) <= 2:
            return word
        
        typo_type = random.choice(['swap', 'delete', 'insert', 'substitute'])
        
        if typo_type == 'swap' and len(word) > 2:
            # Swap two adjacent characters
            pos = random.randint(0, len(word) - 2)
            chars = list(word)
            chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
            return ''.join(chars)
        
        elif typo_type == 'delete' and len(word) > 1:
            # Delete a random character
            pos = random.randint(0, len(word) - 1)
            return word[:pos] + word[pos + 1:]
        
        elif typo_type == 'insert':
            # Insert a random character
            pos = random.randint(0, len(word))
            char = random.choice('abcdefghijklmnopqrstuvwxyz')
            return word[:pos] + char + word[pos:]
        
        elif typo_type == 'substitute' and len(word) > 0:
            # Substitute a random character
            pos = random.randint(0, len(word) - 1)
            char = random.choice('abcdefghijklmnopqrstuvwxyz')
            return word[:pos] + char + word[pos + 1:]
        
        return word
    
    def _introduce_broken_text(self, product: Dict[str, Any]) -> List[str]:
        """Introduce broken text patterns."""
        broken_fields = []
        
        for field in self.noisy_field_candidates:
            if field in product and product[field] and isinstance(product[field], str):
                original_value = product[field]
                broken_value = self._break_text(original_value)
                
                if broken_value != original_value:
                    product[field] = broken_value
                    broken_fields.append(f"Broken text in {field}: '{original_value}' → '{broken_value}'")
        
        return broken_fields
    
    def _break_text(self, text: str) -> str:
        """Break text using common patterns."""
        broken = text
        
        # Add extra spaces
        if random.random() < 0.3:
            broken = re.sub(r'\s+', '   ', broken)  # Multiple spaces
        
        # Add random characters
        if random.random() < 0.2:
            pos = random.randint(0, len(broken))
            char = random.choice('!@#$%^&*()')
            broken = broken[:pos] + char + broken[pos:]
        
        # Remove punctuation
        if random.random() < 0.2:
            broken = re.sub(r'[^\w\s]', ' ', broken)
        
        # Add repeated words
        if random.random() < 0.1:
            words = broken.split()
            if words:
                word = random.choice(words)
                pos = random.randint(0, len(words))
                words.insert(pos, word)
                broken = ' '.join(words)
        
        return broken
    
    def _generate_repair_notes(self, product: Dict[str, Any]) -> List[str]:
        """Generate repair notes for the enhanced product."""
        repair_notes = []
        
        # Check for missing fields
        for field in self.missing_field_candidates:
            if field in product and product[field] is None:
                repair_notes.append(f"✨ Missing {field} - could be inferred from other fields")
        
        # Check for potential typos
        for field in self.noisy_field_candidates:
            if field in product and product[field] and isinstance(product[field], str):
                text = product[field]
                for correct, typos in self.typo_patterns.items():
                    for typo in typos:
                        if typo in text.lower():
                            repair_notes.append(f"🔧 Potential typo in {field}: '{typo}' → '{correct}'")
        
        # Check for broken text patterns
        for field in self.noisy_field_candidates:
            if field in product and product[field] and isinstance(product[field], str):
                text = product[field]
                if re.search(r'\s{2,}', text):  # Multiple spaces
                    repair_notes.append(f"🔧 Multiple spaces in {field} - needs normalization")
                if re.search(r'[^\w\s\-\.]', text):  # Special characters
                    repair_notes.append(f"🔧 Special characters in {field} - needs cleaning")
        
        return repair_notes[:5]  # Limit to 5 repair notes
    
    def create_enhanced_dataset(self, input_file: str, output_file: str) -> None:
        """
        Create an enhanced dataset with Kintsugi imperfections.
        
        Args:
            input_file (str): Path to input JSON file
            output_file (str): Path to output JSON file
        """
        logger.info("Creating Kintsugi-enhanced dataset...")
        
        # Different imperfection rates for different types of products
        imperfection_rates = [0.2, 0.3, 0.4, 0.5]  # Different rates for variety
        
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        enhanced_products = []
        for i, product in enumerate(products):
            # Vary imperfection rate based on product index
            rate = imperfection_rates[i % len(imperfection_rates)]
            enhanced_product = self._enhance_product(product, rate)
            enhanced_products.append(enhanced_product)
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Enhanced {i + 1} products...")
        
        # Save enhanced dataset
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_products, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enhanced dataset saved to {output_file}")
        logger.info(f"Total products: {len(enhanced_products)}")
        
        # Print statistics
        self._print_enhancement_stats(enhanced_products)
    
    def _print_enhancement_stats(self, products: List[Dict[str, Any]]) -> None:
        """Print statistics about the enhancement process."""
        total_products = len(products)
        products_with_imperfections = 0
        total_imperfections = 0
        total_repair_notes = 0
        
        for product in products:
            if '_kintsugi_metadata' in product:
                metadata = product['_kintsugi_metadata']
                if metadata['imperfections_introduced']:
                    products_with_imperfections += 1
                    total_imperfections += len(metadata['imperfections_introduced'])
                total_repair_notes += len(metadata['repair_notes'])
        
        logger.info("\n=== Kintsugi Enhancement Statistics ===")
        logger.info(f"Total products: {total_products}")
        logger.info(f"Products with imperfections: {products_with_imperfections} ({products_with_imperfections/total_products*100:.1f}%)")
        logger.info(f"Total imperfections introduced: {total_imperfections}")
        logger.info(f"Total repair notes generated: {total_repair_notes}")
        logger.info(f"Average imperfections per product: {total_imperfections/total_products:.2f}")
        logger.info(f"Average repair notes per product: {total_repair_notes/total_products:.2f}")


def main():
    """Demo function to enhance the dataset."""
    enhancer = KintsugiDataEnhancer()
    
    # Check if data-set.json exists
    input_file = "data-set.json"
    output_file = "data-set-kintsugi.json"
    
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} not found!")
        return
    
    # Create enhanced dataset
    enhancer.create_enhanced_dataset(input_file, output_file)
    
    logger.info(f"\n✨ Kintsugi-enhanced dataset created: {output_file}")
    logger.info("This dataset now contains imperfections that the search engine must repair!")


if __name__ == "__main__":
    main()
