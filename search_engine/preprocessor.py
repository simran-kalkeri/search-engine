"""
Text Preprocessing Module for E-commerce Search Engine
====================================================

This module handles text preprocessing including normalization,
tokenization, and cleaning for the search engine. It implements
the Kintsugi concept by treating "imperfect" text as valuable
rather than discarding it.

Author: Search Engine Implementation
Date: 2025
"""

import re
import string
import logging
from typing import List, Dict, Set, Tuple, Any
from collections import Counter
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Advanced text preprocessor with Kintsugi-inspired approach.
    
    This class treats "imperfect" text as valuable, implementing
    fuzzy matching and approximate text processing rather than
    strict normalization.
    """
    
    def __init__(self):
        """Initialize the preprocessor with default settings."""
        self.stop_words = self._load_stop_words()
        self.punctuation = set(string.punctuation)
        self.whitespace = set(string.whitespace)
        
        # Common misspellings and variations for e-commerce
        self.common_variations = {
            'colour': 'color',
            'centre': 'center',
            'organise': 'organize',
            'realise': 'realize',
            'analyse': 'analyze',
            'catalogue': 'catalog',
            'cheque': 'check',
            'defence': 'defense',
            'licence': 'license',
            'offence': 'offense',
            'practise': 'practice',
            'programme': 'program',
            'travelling': 'traveling',
            'travelled': 'traveled',
            'traveller': 'traveler'
        }
    
    def _load_stop_words(self) -> Set[str]:
        """Load common stop words for filtering."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'or', 'but', 'not', 'have', 'had',
            'this', 'these', 'they', 'them', 'their', 'there', 'then', 'than',
            'can', 'could', 'would', 'should', 'may', 'might', 'must', 'shall'
        }
    
    def normalize_text(self, text: str, aggressive: bool = False) -> str:
        """
        Normalize text while preserving Kintsugi characteristics.
        
        Args:
            text (str): Input text to normalize
            aggressive (bool): If True, apply more aggressive normalization
            
        Returns:
            str: Normalized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = text.strip()
        text = unicodedata.normalize('NFKD', text)  # Normalize unicode
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        if aggressive:
            # More aggressive normalization
            text = text.lower()
            text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        else:
            # Gentle normalization - preserve some character variations
            text = text.lower()
            # Keep some punctuation that might be meaningful
            text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str, preserve_case: bool = False) -> List[str]:
        """
        Tokenize text into words with Kintsugi approach.
        
        Args:
            text (str): Text to tokenize
            preserve_case (bool): Whether to preserve original case
            
        Returns:
            List[str]: List of tokens
        """
        if not text:
            return []
        
        # Normalize text
        normalized = self.normalize_text(text, aggressive=False)
        
        # Split into tokens
        tokens = re.findall(r'\b\w+\b', normalized)
        
        if not preserve_case:
            tokens = [token.lower() for token in tokens]
        
        return tokens
    
    def create_ngrams(self, text: str, n: int = 2) -> List[str]:
        """
        Create n-grams from text for better matching.
        
        Args:
            text (str): Input text
            n (int): Size of n-grams
            
        Returns:
            List[str]: List of n-grams
        """
        tokens = self.tokenize(text)
        if len(tokens) < n:
            return tokens
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def handle_misspellings(self, text: str) -> str:
        """
        Handle common misspellings and variations.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with corrections applied
        """
        tokens = self.tokenize(text)
        corrected_tokens = []
        
        for token in tokens:
            # Check for common variations
            if token in self.common_variations:
                corrected_tokens.append(self.common_variations[token])
            else:
                corrected_tokens.append(token)
        
        return ' '.join(corrected_tokens)
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        Extract various text features for analysis.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Dictionary of extracted features
        """
        if not text:
            return {}
        
        tokens = self.tokenize(text)
        normalized = self.normalize_text(text)
        
        features = {
            'original_text': text,
            'normalized_text': normalized,
            'tokens': tokens,
            'token_count': len(tokens),
            'char_count': len(text),
            'word_count': len(tokens),
            'unique_tokens': len(set(tokens)),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_special_chars': bool(re.search(r'[^\w\s]', text)),
            'is_all_caps': text.isupper(),
            'is_all_lower': text.islower(),
            'starts_with_capital': text[0].isupper() if text else False
        }
        
        # Add n-grams
        features['bigrams'] = self.create_ngrams(text, 2)
        features['trigrams'] = self.create_ngrams(text, 3)
        
        return features
    
    def preprocess_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess all text fields in a product.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            Dict[str, Any]: Preprocessed product data
        """
        preprocessed = {}
        
        for key, value in product.items():
            if isinstance(value, str) and value.strip():
                # Extract features for this field
                features = self.extract_features(value)
                preprocessed[key] = {
                    'original': value,
                    'normalized': features['normalized_text'],
                    'tokens': features['tokens'],
                    'bigrams': features['bigrams'],
                    'trigrams': features['trigrams'],
                    'features': features
                }
            else:
                preprocessed[key] = value
        
        return preprocessed
    
    def create_searchable_text(self, product: Dict[str, Any]) -> str:
        """
        Create a single searchable text string from all product fields.
        
        Args:
            product (Dict[str, Any]): Product data
            
        Returns:
            str: Combined searchable text
        """
        searchable_parts = []
        
        for key, value in product.items():
            if isinstance(value, str) and value.strip():
                # Add both original and normalized versions
                searchable_parts.append(value)
                searchable_parts.append(self.normalize_text(value))
            elif isinstance(value, (int, float)):
                # Include numeric values as strings
                searchable_parts.append(str(value))
        
        return ' '.join(searchable_parts)
    
    def find_similar_tokens(self, token: str, token_list: List[str], 
                          threshold: float = 0.8) -> List[Tuple[str, float]]:
        """
        Find similar tokens using simple character-based similarity.
        
        Args:
            token (str): Token to find similarities for
            token_list (List[str]): List of tokens to compare against
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            List[Tuple[str, float]]: List of (similar_token, similarity_score) pairs
        """
        similar = []
        token_lower = token.lower()
        
        for other_token in token_list:
            if other_token.lower() == token_lower:
                continue
            
            similarity = self._calculate_similarity(token_lower, other_token.lower())
            if similarity >= threshold:
                similar.append((other_token, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate simple character-based similarity between two strings.
        
        Args:
            str1 (str): First string
            str2 (str): Second string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity on character n-grams
        set1 = set(str1)
        set2 = set(str2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union


def main():
    """
    Demo function to test the preprocessor.
    """
    preprocessor = TextPreprocessor()
    
    # Test with sample e-commerce text
    sample_texts = [
        "Apple iPhone 14 Pro Max 256GB Space Black",
        "Samsung Galaxy S23 Ultra 512GB Phantom Black",
        "Sony WH-1000XM4 Wireless Noise Cancelling Headphones",
        "Dell XPS 13 Laptop Intel i7 16GB RAM 512GB SSD",
        "Nike Air Max 270 Men's Running Shoes Size 10"
    ]
    
    print("=== Text Preprocessor Demo ===")
    
    for text in sample_texts:
        print(f"\nOriginal: {text}")
        
        # Extract features
        features = preprocessor.extract_features(text)
        print(f"Normalized: {features['normalized_text']}")
        print(f"Tokens: {features['tokens']}")
        print(f"Bigrams: {features['bigrams']}")
        
        # Test similarity
        tokens = features['tokens']
        if tokens:
            similar = preprocessor.find_similar_tokens(tokens[0], tokens[1:])
            if similar:
                print(f"Similar to '{tokens[0]}': {similar}")


if __name__ == "__main__":
    main()
