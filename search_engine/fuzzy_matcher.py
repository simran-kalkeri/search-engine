"""
Fuzzy Matching Module with Kintsugi Concept
===========================================

This module implements advanced fuzzy matching algorithms inspired by
the Japanese art of Kintsugi - treating "imperfect" or partial matches
as valuable rather than discarding them. It highlights these "repaired"
matches like golden seams in pottery.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import re
from typing import List, Dict, Tuple, Set, Any, Optional
from difflib import SequenceMatcher
from collections import defaultdict
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KintsugiFuzzyMatcher:
    """
    Advanced fuzzy matcher implementing the Kintsugi concept.
    
    This class treats partial, misspelled, or incomplete queries as
    valuable rather than errors, implementing various fuzzy matching
    algorithms to find the best possible matches.
    """
    
    def __init__(self):
        """Initialize the fuzzy matcher."""
        self.match_types = {
            'exact': 'Perfect match',
            'kintsugi_exact': 'Kintsugi perfect match',
            'kintsugi_near': 'Kintsugi near match',
            'kintsugi_fuzzy': 'Kintsugi fuzzy match',
            'kintsugi_partial': 'Kintsugi partial match',
            'kintsugi_phonetic': 'Kintsugi phonetic match'
        }
        
        # Phonetic mapping for better matching
        self.phonetic_map = self._build_phonetic_map()
        
        # Common e-commerce abbreviations and variations
        self.abbreviations = {
            'wifi': 'wi-fi',
            'bluetooth': 'bt',
            'usb': 'universal serial bus',
            'hdmi': 'high definition multimedia interface',
            'led': 'light emitting diode',
            'oled': 'organic light emitting diode',
            'lcd': 'liquid crystal display',
            'ssd': 'solid state drive',
            'hdd': 'hard disk drive',
            'ram': 'random access memory',
            'cpu': 'central processing unit',
            'gpu': 'graphics processing unit',
            'gb': 'gigabyte',
            'mb': 'megabyte',
            'tb': 'terabyte',
            'hz': 'hertz',
            'ghz': 'gigahertz',
            'mhz': 'megahertz'
        }
    
    def _build_phonetic_map(self) -> Dict[str, str]:
        """Build a phonetic mapping for better matching."""
        return {
            'ph': 'f',
            'ck': 'k',
            'qu': 'kw',
            'x': 'ks',
            'z': 's',
            'c': 'k',  # In some contexts
            'ch': 'k',  # In some contexts
        }
    
    def find_matches(self, query: str, text: str, 
                    threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find fuzzy matches between query and text using Kintsugi approach.
        
        Args:
            query (str): Search query
            text (str): Text to search in
            threshold (float): Minimum similarity threshold
            
        Returns:
            List[Dict[str, Any]]: List of match results with Kintsugi metadata
        """
        if not query or not text:
            return []
        
        matches = []
        
        # Try different matching strategies
        strategies = [
            self._exact_match,
            self._substring_match,
            self._word_boundary_match,
            self._fuzzy_word_match,
            self._phonetic_match,
            self._abbreviation_match,
            self._character_sequence_match
        ]
        
        for strategy in strategies:
            strategy_matches = strategy(query, text, threshold)
            matches.extend(strategy_matches)
        
        # Remove duplicates and sort by score
        unique_matches = self._deduplicate_matches(matches)
        return sorted(unique_matches, key=lambda x: x['score'], reverse=True)
    
    def _exact_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find exact matches."""
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        if query_lower in text_lower:
            start = text_lower.find(query_lower)
            end = start + len(query_lower)
            
            matches.append({
                'type': 'exact',
                'score': 1.0,
                'start': start,
                'end': end,
                'matched_text': text[start:end],
                'kintsugi_quality': 'perfect',
                'description': 'Perfect exact match'
            })
        
        return matches
    
    def _substring_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find substring matches."""
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            
            end = pos + len(query_lower)
            similarity = len(query_lower) / len(text_lower)
            
            if similarity >= threshold:
                matches.append({
                    'type': 'kintsugi_exact',
                    'score': similarity,
                    'start': pos,
                    'end': end,
                    'matched_text': text[pos:end],
                    'kintsugi_quality': 'excellent',
                    'description': 'Kintsugi substring match'
                })
            
            start = pos + 1
        
        return matches
    
    def _word_boundary_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find matches at word boundaries."""
        matches = []
        query_words = query.lower().split()
        text_words = text.lower().split()
        
        for i in range(len(text_words) - len(query_words) + 1):
            window = text_words[i:i + len(query_words)]
            if window == query_words:
                # Calculate position in original text
                start_pos = sum(len(word) + 1 for word in text_words[:i])
                end_pos = start_pos + sum(len(word) + 1 for word in query_words) - 1
                
                matches.append({
                    'type': 'kintsugi_exact',
                    'score': 1.0,
                    'start': start_pos,
                    'end': end_pos,
                    'matched_text': ' '.join(text_words[i:i + len(query_words)]),
                    'kintsugi_quality': 'excellent',
                    'description': 'Kintsugi word boundary match'
                })
        
        return matches
    
    def _fuzzy_word_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find fuzzy word matches."""
        matches = []
        query_words = query.lower().split()
        text_words = text.lower().split()
        
        for i, query_word in enumerate(query_words):
            for j, text_word in enumerate(text_words):
                similarity = SequenceMatcher(None, query_word, text_word).ratio()
                
                if similarity >= threshold:
                    # Find the position in original text
                    start_pos = sum(len(word) + 1 for word in text_words[:j])
                    end_pos = start_pos + len(text_word)
                    
                    matches.append({
                        'type': 'kintsugi_fuzzy',
                        'score': similarity,
                        'start': start_pos,
                        'end': end_pos,
                        'matched_text': text_word,
                        'kintsugi_quality': 'good' if similarity >= 0.8 else 'fair',
                        'description': f'Kintsugi fuzzy word match (similarity: {similarity:.2f})'
                    })
        
        return matches
    
    def _phonetic_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find phonetic matches."""
        matches = []
        query_phonetic = self._to_phonetic(query)
        text_phonetic = self._to_phonetic(text)
        
        if query_phonetic in text_phonetic:
            # Find position in original text
            pos = text_phonetic.find(query_phonetic)
            end_pos = pos + len(query)
            
            matches.append({
                'type': 'kintsugi_phonetic',
                'score': 0.9,
                'start': pos,
                'end': end_pos,
                'matched_text': text[pos:end_pos],
                'kintsugi_quality': 'good',
                'description': 'Kintsugi phonetic match'
            })
        
        return matches
    
    def _abbreviation_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find abbreviation matches."""
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Check if query is an abbreviation
        if query_lower in self.abbreviations:
            expanded = self.abbreviations[query_lower]
            if expanded.lower() in text_lower:
                pos = text_lower.find(expanded.lower())
                end_pos = pos + len(expanded)
                
                matches.append({
                    'type': 'kintsugi_partial',
                    'score': 0.8,
                    'start': pos,
                    'end': end_pos,
                    'matched_text': text[pos:end_pos],
                    'kintsugi_quality': 'good',
                    'description': f'Kintsugi abbreviation match: {query} -> {expanded}'
                })
        
        # Check if text contains abbreviation for query
        for abbr, expansion in self.abbreviations.items():
            if expansion.lower() == query_lower and abbr in text_lower:
                pos = text_lower.find(abbr)
                end_pos = pos + len(abbr)
                
                matches.append({
                    'type': 'kintsugi_partial',
                    'score': 0.8,
                    'start': pos,
                    'end': end_pos,
                    'matched_text': text[pos:end_pos],
                    'kintsugi_quality': 'good',
                    'description': f'Kintsugi abbreviation match: {expansion} -> {abbr}'
                })
        
        return matches
    
    def _character_sequence_match(self, query: str, text: str, threshold: float) -> List[Dict[str, Any]]:
        """Find character sequence matches."""
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find longest common subsequence
        lcs_length = self._longest_common_subsequence(query_lower, text_lower)
        similarity = lcs_length / len(query_lower)
        
        if similarity >= threshold:
            # Find the actual subsequence
            subsequence = self._find_subsequence(query_lower, text_lower)
            if subsequence:
                start, end = subsequence
                matches.append({
                    'type': 'kintsugi_partial',
                    'score': similarity,
                    'start': start,
                    'end': end,
                    'matched_text': text[start:end],
                    'kintsugi_quality': 'fair' if similarity >= 0.7 else 'poor',
                    'description': f'Kintsugi character sequence match (similarity: {similarity:.2f})'
                })
        
        return matches
    
    def _to_phonetic(self, text: str) -> str:
        """Convert text to phonetic representation."""
        phonetic = text.lower()
        for original, replacement in self.phonetic_map.items():
            phonetic = phonetic.replace(original, replacement)
        return phonetic
    
    def _longest_common_subsequence(self, str1: str, str2: str) -> int:
        """Calculate the length of the longest common subsequence."""
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _find_subsequence(self, str1: str, str2: str) -> Optional[Tuple[int, int]]:
        """Find the position of the longest common subsequence."""
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        path = [[None] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    path[i][j] = 'diag'
                else:
                    if dp[i-1][j] > dp[i][j-1]:
                        dp[i][j] = dp[i-1][j]
                        path[i][j] = 'up'
                    else:
                        dp[i][j] = dp[i][j-1]
                        path[i][j] = 'left'
        
        # Backtrack to find the subsequence
        i, j = m, n
        subsequence_positions = []
        
        while i > 0 and j > 0:
            if path[i][j] == 'diag':
                subsequence_positions.append(j-1)
                i -= 1
                j -= 1
            elif path[i][j] == 'up':
                i -= 1
            else:
                j -= 1
        
        if subsequence_positions:
            start = min(subsequence_positions)
            end = max(subsequence_positions) + 1
            return (start, end)
        
        return None
    
    def _deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate matches and keep the best ones."""
        # Group matches by position
        position_groups = defaultdict(list)
        
        for match in matches:
            key = (match['start'], match['end'])
            position_groups[key].append(match)
        
        # Keep the best match from each group
        unique_matches = []
        for group in position_groups.values():
            best_match = max(group, key=lambda x: x['score'])
            unique_matches.append(best_match)
        
        return unique_matches
    
    def highlight_matches(self, text: str, matches: List[Dict[str, Any]], 
                         highlight_format: str = "**{text}**") -> str:
        """
        Highlight matches in text with Kintsugi-style formatting.
        
        Args:
            text (str): Original text
            matches (List[Dict[str, Any]]): List of matches to highlight
            highlight_format (str): Format string for highlighting
            
        Returns:
            str: Text with highlighted matches
        """
        if not matches:
            return text
        
        # Sort matches by position (descending) to avoid index issues
        sorted_matches = sorted(matches, key=lambda x: x['start'], reverse=True)
        
        highlighted_text = text
        
        for match in sorted_matches:
            start = match['start']
            end = match['end']
            matched_text = match['matched_text']
            
            # Create Kintsugi-style highlight
            kintsugi_highlight = self._create_kintsugi_highlight(
                matched_text, match['kintsugi_quality'])
            
            highlighted_text = (highlighted_text[:start] + 
                              kintsugi_highlight + 
                              highlighted_text[end:])
        
        return highlighted_text
    
    def _create_kintsugi_highlight(self, text: str, quality: str) -> str:
        """
        Create Kintsugi-style highlighting based on match quality.
        
        Args:
            text (str): Text to highlight
            quality (str): Quality of the match
            
        Returns:
            str: Highlighted text
        """
        quality_styles = {
            'perfect': f"✨{text}✨",
            'excellent': f"🌟{text}🌟",
            'good': f"⭐{text}⭐",
            'fair': f"💫{text}💫",
            'poor': f"✨{text}✨"
        }
        
        return quality_styles.get(quality, f"✨{text}✨")
    
    def get_match_summary(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of matches with Kintsugi insights.
        
        Args:
            matches (List[Dict[str, Any]]): List of matches
            
        Returns:
            Dict[str, Any]: Summary of matches
        """
        if not matches:
            return {
                'total_matches': 0,
                'kintsugi_insights': 'No matches found - the query may need repair',
                'match_types': {},
                'average_quality': 'none'
            }
        
        # Count match types
        type_counts = defaultdict(int)
        quality_counts = defaultdict(int)
        
        for match in matches:
            type_counts[match['type']] += 1
            quality_counts[match['kintsugi_quality']] += 1
        
        # Calculate average score
        avg_score = sum(match['score'] for match in matches) / len(matches)
        
        # Generate Kintsugi insights
        insights = self._generate_kintsugi_insights(matches, type_counts, quality_counts)
        
        return {
            'total_matches': len(matches),
            'average_score': avg_score,
            'match_types': dict(type_counts),
            'quality_distribution': dict(quality_counts),
            'kintsugi_insights': insights,
            'best_match': max(matches, key=lambda x: x['score']) if matches else None
        }
    
    def _generate_kintsugi_insights(self, matches: List[Dict[str, Any]], 
                                  type_counts: Dict[str, int], 
                                  quality_counts: Dict[str, int]) -> str:
        """Generate Kintsugi-inspired insights about the matches."""
        insights = []
        
        if 'exact' in type_counts:
            insights.append("Found perfect matches - no repair needed!")
        
        if 'kintsugi_fuzzy' in type_counts:
            insights.append(f"Found {type_counts['kintsugi_fuzzy']} fuzzy matches - "
                          "imperfect queries can still find valuable results!")
        
        if 'kintsugi_partial' in type_counts:
            insights.append(f"Found {type_counts['kintsugi_partial']} partial matches - "
                          "even broken queries reveal hidden treasures!")
        
        if 'kintsugi_phonetic' in type_counts:
            insights.append(f"Found {type_counts['kintsugi_phonetic']} phonetic matches - "
                          "sounds can guide us to the right place!")
        
        if quality_counts.get('excellent', 0) > 0:
            insights.append("High-quality matches found - the golden seams are strong!")
        
        if not insights:
            insights.append("Some matches found - every crack tells a story!")
        
        return " | ".join(insights)


def main():
    """
    Demo function to test the fuzzy matcher.
    """
    matcher = KintsugiFuzzyMatcher()
    
    # Test with sample queries
    test_cases = [
        ("iphone", "Apple iPhone 14 Pro Max 256GB Space Black"),
        ("samsng", "Samsung Galaxy S23 Ultra 512GB Phantom Black"),
        ("noise cancelling", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones"),
        ("laptop i7", "Dell XPS 13 Laptop Intel i7 16GB RAM 512GB SSD"),
        ("nike shoes", "Nike Air Max 270 Men's Running Shoes Size 10")
    ]
    
    print("=== Kintsugi Fuzzy Matcher Demo ===")
    
    for query, text in test_cases:
        print(f"\nQuery: '{query}'")
        print(f"Text: '{text}'")
        
        matches = matcher.find_matches(query, text, threshold=0.5)
        
        if matches:
            print(f"Found {len(matches)} matches:")
            for i, match in enumerate(matches[:3]):  # Show top 3
                print(f"  {i+1}. {match['description']} (score: {match['score']:.2f})")
                print(f"     Matched: '{match['matched_text']}'")
                print(f"     Quality: {match['kintsugi_quality']}")
        else:
            print("  No matches found")
        
        # Test highlighting
        highlighted = matcher.highlight_matches(text, matches)
        print(f"  Highlighted: {highlighted}")
        
        # Get summary
        summary = matcher.get_match_summary(matches)
        print(f"  Insights: {summary['kintsugi_insights']}")


if __name__ == "__main__":
    main()
