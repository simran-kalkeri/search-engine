"""
Advanced Kintsugi Repair System with Detailed Annotation
=======================================================

This module implements a comprehensive Kintsugi-inspired repair system that:
- Detects and repairs imperfect queries, data, and results
- Provides detailed annotations about repair processes
- Tracks repair history and quality improvements
- Generates Kintsugi insights and visualizations
- Embodies the philosophy of finding beauty in imperfection

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import re
import time
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path
import difflib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KintsugiRepairSystem:
    """
    Advanced Kintsugi repair system for search and recommendation.
    
    This class implements a comprehensive repair system that treats
    imperfections as opportunities for enhancement rather than problems
    to be hidden or discarded.
    """
    
    def __init__(self):
        """Initialize the Kintsugi repair system."""
        self.repair_history = []
        self.repair_patterns = self._initialize_repair_patterns()
        self.quality_metrics = defaultdict(list)
        self.kintsugi_notes = []
        
        # Repair statistics
        self.stats = {
            'total_repairs': 0,
            'successful_repairs': 0,
            'failed_repairs': 0,
            'quality_improvements': 0,
            'repair_types': defaultdict(int)
        }
    
    def _initialize_repair_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize repair patterns for different types of imperfections."""
        return {
            'typos': {
                'pattern': r'\b(\w+)\b',
                'repair_function': self._repair_typos,
                'description': 'Repair spelling mistakes and typos'
            },
            'missing_fields': {
                'pattern': r'^\s*$',
                'repair_function': self._repair_missing_fields,
                'description': 'Fill in missing or empty fields'
            },
            'broken_text': {
                'pattern': r'[^\w\s\-\.]',
                'repair_function': self._repair_broken_text,
                'description': 'Clean and normalize broken text'
            },
            'incomplete_queries': {
                'pattern': r'^\s*\w{1,2}\s*$',
                'repair_function': self._repair_incomplete_queries,
                'description': 'Expand incomplete or very short queries'
            },
            'noisy_data': {
                'pattern': r'\s{2,}',
                'repair_function': self._repair_noisy_data,
                'description': 'Clean noisy data with extra spaces and characters'
            },
            'case_issues': {
                'pattern': r'^[a-z]',
                'repair_function': self._repair_case_issues,
                'description': 'Fix capitalization issues'
            }
        }
    
    def repair_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Repair a search query using Kintsugi principles.
        
        Args:
            query (str): Original query
            context (Optional[Dict[str, Any]]): Additional context for repair
            
        Returns:
            Dict[str, Any]: Repair result with annotations
        """
        if not query or not query.strip():
            return self._create_empty_repair_result(query, "Empty query provided")
        
        original_query = query.strip()
        repaired_query = original_query
        repair_notes = []
        quality_score = 0.0
        
        # Detect and repair different types of imperfections
        for repair_type, pattern_info in self.repair_patterns.items():
            if self._needs_repair(original_query, pattern_info['pattern']):
                repair_result = pattern_info['repair_function'](repaired_query, context)
                
                if repair_result['success']:
                    repaired_query = repair_result['repaired_text']
                    repair_notes.extend(repair_result['notes'])
                    quality_score += repair_result['quality_improvement']
                    
                    # Record repair
                    self._record_repair(repair_type, original_query, repaired_query, repair_result)
        
        # Calculate final quality score
        final_quality = min(1.0, quality_score + self._calculate_base_quality(repaired_query))
        
        # Generate Kintsugi insights
        kintsugi_insights = self._generate_repair_insights(original_query, repaired_query, repair_notes)
        
        return {
            'original_query': original_query,
            'repaired_query': repaired_query,
            'repair_notes': repair_notes,
            'quality_score': final_quality,
            'kintsugi_insights': kintsugi_insights,
            'repair_successful': repaired_query != original_query,
            'repair_timestamp': time.time()
        }
    
    def _needs_repair(self, text: str, pattern: str) -> bool:
        """Check if text needs repair based on pattern."""
        return bool(re.search(pattern, text))
    
    def _repair_typos(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Repair typos in text."""
        # Common typo corrections
        typo_corrections = {
            'samsng': 'samsung',
            'iphne': 'iphone',
            'galxy': 'galaxy',
            'headphnes': 'headphones',
            'wireles': 'wireless',
            'blutooth': 'bluetooth',
            'laptp': 'laptop',
            'smartphne': 'smartphone',
            'disply': 'display',
            'batery': 'battery',
            'camra': 'camera',
            'storag': 'storage',
            'memry': 'memory',
            'procesor': 'processor',
            'graphcs': 'graphics',
            'connectivty': 'connectivity',
            'durabilty': 'durability',
            'waterprof': 'waterproof',
            'nois': 'noise',
            'canceling': 'cancelling'
        }
        
        repaired_text = text
        notes = []
        quality_improvement = 0.0
        
        for typo, correction in typo_corrections.items():
            if typo in text.lower():
                repaired_text = re.sub(typo, correction, repaired_text, flags=re.IGNORECASE)
                notes.append(f"🔧 Fixed typo: '{typo}' → '{correction}'")
                quality_improvement += 0.1
        
        return {
            'success': repaired_text != text,
            'repaired_text': repaired_text,
            'notes': notes,
            'quality_improvement': quality_improvement
        }
    
    def _repair_missing_fields(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Repair missing or empty fields."""
        if not text or not text.strip():
            # Try to infer from context
            if context and 'product_type' in context:
                inferred_text = f"Product: {context['product_type']}"
                return {
                    'success': True,
                    'repaired_text': inferred_text,
                    'notes': [f"✨ Inferred missing field from context: '{inferred_text}'"],
                    'quality_improvement': 0.3
                }
            else:
                return {
                    'success': False,
                    'repaired_text': text,
                    'notes': ["❌ Cannot repair empty field without context"],
                    'quality_improvement': 0.0
                }
        
        return {
            'success': False,
            'repaired_text': text,
            'notes': [],
            'quality_improvement': 0.0
        }
    
    def _repair_broken_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Repair broken text with special characters and formatting issues."""
        repaired_text = text
        notes = []
        quality_improvement = 0.0
        
        # Remove excessive special characters
        if re.search(r'[^\w\s\-\.]{2,}', text):
            repaired_text = re.sub(r'[^\w\s\-\.]{2,}', ' ', repaired_text)
            notes.append("🔧 Removed excessive special characters")
            quality_improvement += 0.1
        
        # Fix multiple spaces
        if re.search(r'\s{2,}', text):
            repaired_text = re.sub(r'\s{2,}', ' ', repaired_text)
            notes.append("🔧 Normalized multiple spaces")
            quality_improvement += 0.05
        
        # Remove repeated words
        if re.search(r'\b(\w+)\s+\1\b', text):
            repaired_text = re.sub(r'\b(\w+)\s+\1\b', r'\1', repaired_text)
            notes.append("🔧 Removed repeated words")
            quality_improvement += 0.1
        
        # Clean up punctuation
        if re.search(r'[^\w\s\-\.]', text):
            repaired_text = re.sub(r'[^\w\s\-\.]', ' ', repaired_text)
            notes.append("🔧 Cleaned up punctuation")
            quality_improvement += 0.05
        
        return {
            'success': repaired_text != text,
            'repaired_text': repaired_text.strip(),
            'notes': notes,
            'quality_improvement': quality_improvement
        }
    
    def _repair_incomplete_queries(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Repair incomplete or very short queries."""
        if len(text.split()) <= 2:
            # Try to expand based on context or common patterns
            expanded_text = self._expand_incomplete_query(text, context)
            
            if expanded_text != text:
                return {
                    'success': True,
                    'repaired_text': expanded_text,
                    'notes': [f"✨ Expanded incomplete query: '{text}' → '{expanded_text}'"],
                    'quality_improvement': 0.2
                }
        
        return {
            'success': False,
            'repaired_text': text,
            'notes': [],
            'quality_improvement': 0.0
        }
    
    def _expand_incomplete_query(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Expand an incomplete query."""
        # Common expansions
        expansions = {
            'iphone': 'iPhone smartphone',
            'samsung': 'Samsung smartphone',
            'laptop': 'laptop computer',
            'headphone': 'headphones audio',
            'camera': 'camera photography',
            'watch': 'smartwatch wearable',
            'tablet': 'tablet computer',
            'speaker': 'speaker audio',
            'mouse': 'computer mouse',
            'keyboard': 'computer keyboard'
        }
        
        text_lower = text.lower()
        for short, expanded in expansions.items():
            if short in text_lower:
                return expanded
        
        return text
    
    def _repair_noisy_data(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Repair noisy data with extra spaces and characters."""
        repaired_text = text
        notes = []
        quality_improvement = 0.0
        
        # Remove extra spaces
        if re.search(r'\s{2,}', text):
            repaired_text = re.sub(r'\s{2,}', ' ', repaired_text)
            notes.append("🔧 Removed extra spaces")
            quality_improvement += 0.05
        
        # Remove leading/trailing whitespace
        if text != text.strip():
            repaired_text = repaired_text.strip()
            notes.append("🔧 Trimmed whitespace")
            quality_improvement += 0.02
        
        # Remove excessive punctuation
        if re.search(r'[!]{2,}|[?]{2,}|[.]{2,}', text):
            repaired_text = re.sub(r'[!]{2,}', '!', repaired_text)
            repaired_text = re.sub(r'[?]{2,}', '?', repaired_text)
            repaired_text = re.sub(r'[.]{2,}', '.', repaired_text)
            notes.append("🔧 Normalized punctuation")
            quality_improvement += 0.05
        
        return {
            'success': repaired_text != text,
            'repaired_text': repaired_text,
            'notes': notes,
            'quality_improvement': quality_improvement
        }
    
    def _repair_case_issues(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Repair capitalization issues."""
        repaired_text = text
        notes = []
        quality_improvement = 0.0
        
        # Fix brand names that should be capitalized
        brand_names = ['iphone', 'samsung', 'apple', 'sony', 'dell', 'hp', 'lenovo', 'asus']
        
        for brand in brand_names:
            if brand in text.lower():
                # Capitalize the brand name
                pattern = re.compile(re.escape(brand), re.IGNORECASE)
                repaired_text = pattern.sub(brand.title(), repaired_text)
                notes.append(f"🔧 Fixed capitalization: '{brand}' → '{brand.title()}'")
                quality_improvement += 0.05
        
        # Fix sentence case for descriptions
        if text and text[0].islower() and len(text.split()) > 3:
            repaired_text = text[0].upper() + text[1:]
            notes.append("🔧 Fixed sentence capitalization")
            quality_improvement += 0.03
        
        return {
            'success': repaired_text != text,
            'repaired_text': repaired_text,
            'notes': notes,
            'quality_improvement': quality_improvement
        }
    
    def _calculate_base_quality(self, text: str) -> float:
        """Calculate base quality score for text."""
        if not text:
            return 0.0
        
        quality = 0.5  # Base quality
        
        # Length bonus
        word_count = len(text.split())
        if word_count > 3:
            quality += 0.1
        if word_count > 10:
            quality += 0.1
        
        # Character diversity bonus
        unique_chars = len(set(text.lower()))
        if unique_chars > 10:
            quality += 0.1
        
        # No excessive repetition
        words = text.split()
        if len(set(words)) / len(words) > 0.7:
            quality += 0.1
        
        return min(1.0, quality)
    
    def _record_repair(self, repair_type: str, original: str, repaired: str, result: Dict[str, Any]) -> None:
        """Record a repair in the history."""
        repair_record = {
            'repair_type': repair_type,
            'original_text': original,
            'repaired_text': repaired,
            'success': result['success'],
            'quality_improvement': result['quality_improvement'],
            'notes': result['notes'],
            'timestamp': time.time()
        }
        
        self.repair_history.append(repair_record)
        self.stats['total_repairs'] += 1
        
        if result['success']:
            self.stats['successful_repairs'] += 1
            self.stats['repair_types'][repair_type] += 1
        else:
            self.stats['failed_repairs'] += 1
        
        if result['quality_improvement'] > 0:
            self.stats['quality_improvements'] += 1
    
    def _generate_repair_insights(self, original: str, repaired: str, notes: List[str]) -> List[str]:
        """Generate Kintsugi insights about the repair process."""
        insights = []
        
        if original == repaired:
            insights.append("✨ No repair needed - perfect as is!")
            return insights
        
        # Analyze repair success
        if notes:
            insights.append(f"🔧 Applied {len(notes)} repairs to enhance the query")
        
        # Analyze quality improvement
        quality_diff = self._calculate_base_quality(repaired) - self._calculate_base_quality(original)
        if quality_diff > 0.1:
            insights.append("🌟 Significant quality improvement achieved!")
        elif quality_diff > 0.05:
            insights.append("✨ Good quality improvement achieved")
        else:
            insights.append("🔧 Minor quality improvement achieved")
        
        # Analyze repair types
        repair_types = set()
        for note in notes:
            if 'typo' in note:
                repair_types.add('typos')
            elif 'space' in note:
                repair_types.add('formatting')
            elif 'capitalization' in note:
                repair_types.add('capitalization')
            elif 'expanded' in note:
                repair_types.add('expansion')
        
        if repair_types:
            insights.append(f"🎨 Repaired: {', '.join(repair_types)}")
        
        # Kintsugi philosophy
        insights.append("💫 Every imperfection is an opportunity for beauty")
        
        return insights
    
    def _create_empty_repair_result(self, query: str, message: str) -> Dict[str, Any]:
        """Create an empty repair result."""
        return {
            'original_query': query,
            'repaired_query': query,
            'repair_notes': [message],
            'quality_score': 0.0,
            'kintsugi_insights': [message],
            'repair_successful': False,
            'repair_timestamp': time.time()
        }
    
    def repair_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Repair search results using Kintsugi principles.
        
        Args:
            results (List[Dict[str, Any]]): List of search results
            
        Returns:
            List[Dict[str, Any]]: Repaired results with annotations
        """
        repaired_results = []
        
        for result in results:
            repaired_result = result.copy()
            
            # Repair document fields if needed
            if 'document' in result:
                repaired_document = self._repair_document(result['document'])
                repaired_result['document'] = repaired_document
                repaired_result['repair_notes'] = repaired_document.get('_repair_notes', [])
            
            # Add Kintsugi quality assessment
            repaired_result['kintsugi_quality'] = self._assess_result_quality(repaired_result)
            
            repaired_results.append(repaired_result)
        
        return repaired_results
    
    def _repair_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Repair a document by fixing its fields."""
        repaired_doc = document.copy()
        repair_notes = []
        
        # Repair text fields
        text_fields = ['Brand', 'Type', 'Features', 'Description', 'Specifications']
        
        for field in text_fields:
            if field in document and document[field]:
                field_value = str(document[field])
                repair_result = self.repair_query(field_value)
                
                if repair_result['repair_successful']:
                    repaired_doc[field] = repair_result['repaired_query']
                    repair_notes.extend(repair_result['repair_notes'])
        
        repaired_doc['_repair_notes'] = repair_notes
        return repaired_doc
    
    def _assess_result_quality(self, result: Dict[str, Any]) -> str:
        """Assess the Kintsugi quality of a search result."""
        score = result.get('blended_score', 0.0)
        match_type = result.get('match_type', '')
        
        if score >= 0.9:
            return 'perfect'
        elif score >= 0.7:
            return 'excellent'
        elif score >= 0.5:
            return 'good'
        elif score >= 0.3:
            return 'fair'
        else:
            return 'poor'
    
    def get_repair_statistics(self) -> Dict[str, Any]:
        """Get comprehensive repair statistics."""
        total_repairs = self.stats['total_repairs']
        success_rate = (self.stats['successful_repairs'] / total_repairs * 100) if total_repairs > 0 else 0
        
        return {
            'total_repairs': total_repairs,
            'successful_repairs': self.stats['successful_repairs'],
            'failed_repairs': self.stats['failed_repairs'],
            'success_rate': success_rate,
            'quality_improvements': self.stats['quality_improvements'],
            'repair_types': dict(self.stats['repair_types']),
            'recent_repairs': self.repair_history[-10:] if self.repair_history else []
        }
    
    def get_kintsugi_insights(self) -> List[str]:
        """Get Kintsugi insights about the repair system."""
        insights = []
        
        stats = self.get_repair_statistics()
        
        if stats['total_repairs'] > 0:
            insights.append(f"🔧 {stats['total_repairs']} repairs performed")
            insights.append(f"✨ {stats['success_rate']:.1f}% success rate")
            insights.append(f"🌟 {stats['quality_improvements']} quality improvements achieved")
        
        # Analyze repair types
        if stats['repair_types']:
            most_common = max(stats['repair_types'].items(), key=lambda x: x[1])
            insights.append(f"🎨 Most common repair: {most_common[0]} ({most_common[1]} times)")
        
        # Kintsugi philosophy
        insights.append("💫 Every imperfection is an opportunity for beauty")
        insights.append("🔧 Repair makes things stronger, not weaker")
        
        return insights
    
    def save_repair_history(self, filepath: str) -> None:
        """Save repair history to file."""
        data = {
            'repair_history': self.repair_history,
            'stats': dict(self.stats),
            'kintsugi_notes': self.kintsugi_notes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Repair history saved to {filepath}")
    
    def load_repair_history(self, filepath: str) -> None:
        """Load repair history from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.repair_history = data.get('repair_history', [])
        self.stats = defaultdict(int, data.get('stats', {}))
        self.kintsugi_notes = data.get('kintsugi_notes', [])
        
        logger.info(f"Repair history loaded from {filepath}")


def main():
    """Demo function to test the Kintsugi repair system."""
    print("=== Kintsugi Repair System Demo ===")
    
    repair_system = KintsugiRepairSystem()
    
    # Test queries with various imperfections
    test_queries = [
        "samsng galaxy s23",  # Typo
        "iphne 14 pro max",   # Typo
        "noise cancelling headphnes",  # Typo
        "wireles blutooth speaker",  # Multiple typos
        "laptp",  # Incomplete
        "   extra   spaces   ",  # Noisy data
        "iphone",  # Short query
        "SAMSUNG GALAXY",  # Case issues
    ]
    
    for query in test_queries:
        print(f"\nOriginal: '{query}'")
        result = repair_system.repair_query(query)
        
        print(f"Repaired: '{result['repaired_query']}'")
        print(f"Quality: {result['quality_score']:.2f}")
        print(f"Success: {result['repair_successful']}")
        
        for note in result['repair_notes']:
            print(f"  {note}")
        
        for insight in result['kintsugi_insights']:
            print(f"  {insight}")
    
    # Get statistics
    stats = repair_system.get_repair_statistics()
    print(f"\nRepair Statistics:")
    print(f"  Total repairs: {stats['total_repairs']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print(f"  Quality improvements: {stats['quality_improvements']}")


if __name__ == "__main__":
    main()
