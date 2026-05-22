"""
Inverted Index Module for E-commerce Search Engine
=================================================

This module implements an inverted index for fast text searching
with support for fuzzy matching and Kintsugi-inspired approximate
search capabilities.

Author: Search Engine Implementation
Date: 2025
"""

import logging
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, Counter
import math
import json
from pathlib import Path

from preprocessor import TextPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvertedIndex:
    """
    Advanced inverted index with fuzzy matching capabilities.
    
    This class implements an inverted index that supports both exact
    and approximate matching, embodying the Kintsugi concept by
    treating partial matches as valuable rather than discarding them.
    """
    
    def __init__(self):
        """Initialize the inverted index."""
        self.preprocessor = TextPreprocessor()
        
        # Core index structures
        self.term_to_docs: Dict[str, Set[int]] = defaultdict(set)
        self.doc_to_terms: Dict[int, Set[str]] = defaultdict(set)
        self.term_frequencies: Dict[Tuple[str, int], int] = defaultdict(int)
        self.document_frequencies: Dict[str, int] = defaultdict(int)
        
        # Document metadata
        self.documents: Dict[int, Dict[str, Any]] = {}
        self.document_lengths: Dict[int, int] = {}
        self.total_documents = 0
        
        # Fuzzy matching cache
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        
        # Field-specific indexes for better precision
        self.field_indexes: Dict[str, Dict[str, Set[int]]] = defaultdict(lambda: defaultdict(set))
    
    def add_document(self, doc_id: int, document: Dict[str, Any]) -> None:
        """
        Add a document to the index.
        
        Args:
            doc_id (int): Unique document identifier
            document (Dict[str, Any]): Document data
        """
        # Store document metadata
        self.documents[doc_id] = document
        self.total_documents += 1
        
        # Preprocess the document
        preprocessed = self.preprocessor.preprocess_product(document)
        
        # Create searchable text
        searchable_text = self.preprocessor.create_searchable_text(document)
        all_tokens = self.preprocessor.tokenize(searchable_text)
        
        # Index all tokens
        self._index_tokens(doc_id, all_tokens, 'all')
        
        # Index field-specific content
        for field, value in preprocessed.items():
            if isinstance(value, dict) and 'tokens' in value:
                self._index_tokens(doc_id, value['tokens'], field)
                self._index_tokens(doc_id, value['bigrams'], f"{field}_bigrams")
                self._index_tokens(doc_id, value['trigrams'], f"{field}_trigrams")
    
    def _index_tokens(self, doc_id: int, tokens: List[str], field: str = 'all') -> None:
        """
        Index a list of tokens for a document.
        
        Args:
            doc_id (int): Document ID
            tokens (List[str]): List of tokens to index
            field (str): Field name for field-specific indexing
        """
        # Count term frequencies
        term_counts = Counter(tokens)
        doc_length = len(tokens)
        self.document_lengths[doc_id] = doc_length
        
        for term, count in term_counts.items():
            if not term:  # Skip empty terms
                continue
            
            # Add to main index
            self.term_to_docs[term].add(doc_id)
            self.doc_to_terms[doc_id].add(term)
            self.term_frequencies[(term, doc_id)] = count
            
            # Add to field-specific index
            self.field_indexes[field][term].add(doc_id)
        
        # Update document frequencies
        for term in set(tokens):
            if term:
                self.document_frequencies[term] = len(self.term_to_docs[term])
    
    def search_exact(self, query: str, field: Optional[str] = None) -> List[Tuple[int, float]]:
        """
        Perform exact search for terms with phrase matching and proximity scoring.
        
        Args:
            query (str): Search query
            field (Optional[str]): Specific field to search in
            
        Returns:
            List[Tuple[int, float]]: List of (doc_id, score) tuples
        """
        query_tokens = self.preprocessor.tokenize(query)
        if not query_tokens:
            return []
        
        # First try phrase matching for multi-word queries
        if len(query_tokens) > 1:
            phrase_scores = self._search_phrase(query, field)
            if phrase_scores:
                return phrase_scores
        
        # Get relevant documents for individual terms
        if field and field in self.field_indexes:
            relevant_docs = self._get_docs_for_tokens(query_tokens, field)
        else:
            relevant_docs = self._get_docs_for_tokens(query_tokens, 'all')
        
        if not relevant_docs:
            return []
        
        # Calculate scores using TF-IDF with proximity bonus
        scores = self._calculate_tfidf_scores_with_proximity(query_tokens, relevant_docs, field)
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def search_fuzzy(self, query: str, field: Optional[str] = None, 
                    threshold: float = 0.7) -> List[Tuple[int, float, str]]:
        """
        Perform fuzzy search with Kintsugi-inspired matching and phrase support.
        
        Args:
            query (str): Search query
            field (Optional[str]): Specific field to search in
            threshold (float): Similarity threshold for fuzzy matching
            
        Returns:
            List[Tuple[int, float, str]]: List of (doc_id, score, match_type) tuples
        """
        query_tokens = self.preprocessor.tokenize(query)
        if not query_tokens:
            return []
        
        # First try fuzzy phrase matching for multi-word queries
        if len(query_tokens) > 1:
            fuzzy_phrase_scores = self._search_fuzzy_phrase(query, field, threshold)
            if fuzzy_phrase_scores:
                return fuzzy_phrase_scores
        
        # Get all terms in the index
        if field and field in self.field_indexes:
            index_terms = set(self.field_indexes[field].keys())
        else:
            index_terms = set(self.term_to_docs.keys())
        
        # Find similar terms (limit to top matches)
        similar_terms = self._find_similar_terms(query_tokens, index_terms, threshold)
        
        if not similar_terms:
            return []
        
        # Limit similar terms to avoid too many results
        similar_terms = similar_terms[:100]  # Limit to top 100 similar terms
        
        # Get documents containing similar terms
        relevant_docs = set()
        for term, similarity in similar_terms:
            if field and field in self.field_indexes:
                docs = self.field_indexes[field][term]
            else:
                docs = self.term_to_docs[term]
            relevant_docs.update(docs)
            
            # Limit documents to avoid too many results
            if len(relevant_docs) > 1000:
                break
        
        if not relevant_docs:
            return []
        
        # Calculate fuzzy scores with proximity
        scores = self._calculate_fuzzy_scores_with_proximity(query_tokens, similar_terms, 
                                                           list(relevant_docs), field)
        
        # Return top results only
        return sorted(scores, key=lambda x: x[1], reverse=True)[:500]
    
    def _get_docs_for_tokens(self, tokens: List[str], field: str) -> Set[int]:
        """
        Get documents that contain all the given tokens.
        
        Args:
            tokens (List[str]): List of tokens to search for
            field (str): Field to search in
            
        Returns:
            Set[int]: Set of document IDs
        """
        if not tokens:
            return set()
        
        # Start with documents containing the first token
        if field in self.field_indexes:
            docs = self.field_indexes[field][tokens[0]].copy()
        else:
            docs = self.term_to_docs[tokens[0]].copy()
        
        # Intersect with documents containing other tokens
        for token in tokens[1:]:
            if field in self.field_indexes:
                token_docs = self.field_indexes[field][token]
            else:
                token_docs = self.term_to_docs[token]
            
            docs = docs.intersection(token_docs)
            
            if not docs:  # Early termination if no common docs
                break
        
        return docs
    
    def _find_similar_terms(self, query_tokens: List[str], 
                          index_terms: Set[str], threshold: float) -> List[Tuple[str, float]]:
        """
        Find terms in the index that are similar to query tokens.
        
        Args:
            query_tokens (List[str]): Query tokens
            index_terms (Set[str]): Terms in the index
            threshold (float): Similarity threshold
            
        Returns:
            List[Tuple[str, float]]: List of (term, similarity) tuples
        """
        similar_terms = []
        
        for query_token in query_tokens:
            for index_term in index_terms:
                # Check cache first
                cache_key = (query_token, index_term)
                if cache_key in self.similarity_cache:
                    similarity = self.similarity_cache[cache_key]
                else:
                    similarity = self._calculate_similarity(
                        query_token, index_term)
                    self.similarity_cache[cache_key] = similarity
                
                if similarity >= threshold:
                    similar_terms.append((index_term, similarity))
        
        return similar_terms
    
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
    
    def _search_phrase(self, query: str, field: Optional[str] = None) -> List[Tuple[int, float]]:
        """
        Search for exact phrase matches.
        
        Args:
            query (str): Search query
            field (Optional[str]): Specific field to search in
            
        Returns:
            List[Tuple[int, float]]: List of (doc_id, score) tuples
        """
        phrase_scores = []
        query_lower = query.lower()
        
        # Search in all documents
        for doc_id, document in self.documents.items():
            # Create searchable text
            searchable_text = self.preprocessor.create_searchable_text(document)
            searchable_lower = searchable_text.lower()
            
            # Check for exact phrase match
            if query_lower in searchable_lower:
                # Calculate phrase score (higher than individual terms)
                phrase_count = searchable_lower.count(query_lower)
                base_score = phrase_count * 10.0  # High base score for phrase matches
                
                # Add position bonus (earlier in text = higher score)
                position = searchable_lower.find(query_lower)
                position_bonus = max(0, 1.0 - (position / len(searchable_lower)))
                final_score = base_score * (1.0 + position_bonus)
                
                phrase_scores.append((doc_id, final_score))
        
        return sorted(phrase_scores, key=lambda x: x[1], reverse=True)
    
    def _calculate_tfidf_scores_with_proximity(self, query_tokens: List[str], 
                                             doc_ids: Set[int], field: Optional[str] = None) -> List[Tuple[int, float]]:
        """
        Calculate TF-IDF scores with proximity bonuses for multi-word queries.
        
        Args:
            query_tokens (List[str]): Query tokens
            doc_ids (Set[int]): Document IDs to score
            field (Optional[str]): Field to consider for scoring
            
        Returns:
            List[Tuple[int, float]]: List of (doc_id, score) tuples
        """
        scores = []
        
        for doc_id in doc_ids:
            score = 0.0
            matched_tokens = 0
            
            # Calculate base TF-IDF score
            for token in query_tokens:
                tf = self.term_frequencies.get((token, doc_id), 0)
                if tf == 0:
                    continue
                
                df = self.document_frequencies.get(token, 0)
                if df == 0:
                    continue
                
                idf = math.log(self.total_documents / df)
                score += tf * idf
                matched_tokens += 1
            
            if matched_tokens > 0:
                # Apply match ratio penalty
                match_ratio = matched_tokens / len(query_tokens)
                score *= match_ratio
                
                # Add proximity bonus for multi-word queries
                if len(query_tokens) > 1 and matched_tokens > 1:
                    proximity_bonus = self._calculate_proximity_bonus(query_tokens, doc_id)
                    score *= (1.0 + proximity_bonus)
                
                scores.append((doc_id, score))
        
        return scores
    
    def _calculate_proximity_bonus(self, query_tokens: List[str], doc_id: int) -> float:
        """
        Calculate proximity bonus for documents where query terms appear close together.
        
        Args:
            query_tokens (List[str]): Query tokens
            doc_id (int): Document ID
            
        Returns:
            float: Proximity bonus multiplier (0.0 to 1.0)
        """
        document = self.documents.get(doc_id)
        if not document:
            return 0.0
        
        searchable_text = self.preprocessor.create_searchable_text(document)
        searchable_lower = searchable_text.lower()
        
        # Find positions of each query token
        token_positions = {}
        for token in query_tokens:
            positions = []
            start = 0
            while True:
                pos = searchable_lower.find(token.lower(), start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            if positions:
                token_positions[token] = positions
        
        if len(token_positions) < 2:
            return 0.0
        
        # Calculate minimum distance between any two tokens
        min_distance = float('inf')
        tokens = list(token_positions.keys())
        
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                token1_positions = token_positions[tokens[i]]
                token2_positions = token_positions[tokens[j]]
                
                for pos1 in token1_positions:
                    for pos2 in token2_positions:
                        distance = abs(pos1 - pos2)
                        min_distance = min(min_distance, distance)
        
        if min_distance == float('inf'):
            return 0.0
        
        # Convert distance to bonus (closer = higher bonus)
        # Maximum bonus of 0.5 for very close terms
        max_distance = 100  # Consider terms within 100 characters as "close"
        if min_distance <= max_distance:
            bonus = 0.5 * (1.0 - min_distance / max_distance)
            return bonus
        
        return 0.0
    
    def _search_fuzzy_phrase(self, query: str, field: Optional[str] = None, 
                           threshold: float = 0.7) -> List[Tuple[int, float, str]]:
        """
        Search for fuzzy phrase matches.
        
        Args:
            query (str): Search query
            field (Optional[str]): Specific field to search in
            threshold (float): Similarity threshold
            
        Returns:
            List[Tuple[int, float, str]]: List of (doc_id, score, match_type) tuples
        """
        fuzzy_phrase_scores = []
        query_lower = query.lower()
        
        # Search in all documents
        for doc_id, document in self.documents.items():
            searchable_text = self.preprocessor.create_searchable_text(document)
            searchable_lower = searchable_text.lower()
            
            # Check for fuzzy phrase match using similarity
            similarity = self._calculate_phrase_similarity(query_lower, searchable_lower)
            
            if similarity >= threshold:
                # Calculate fuzzy phrase score
                phrase_count = self._count_fuzzy_phrase_occurrences(query_lower, searchable_lower, threshold)
                base_score = phrase_count * 8.0  # High base score for fuzzy phrase matches
                
                # Add position bonus
                position = searchable_lower.find(query_lower)
                if position == -1:
                    # Find best fuzzy match position
                    position = self._find_best_fuzzy_position(query_lower, searchable_lower, threshold)
                
                if position >= 0:
                    position_bonus = max(0, 1.0 - (position / len(searchable_lower)))
                    final_score = base_score * (1.0 + position_bonus) * similarity
                    
                    fuzzy_phrase_scores.append((doc_id, final_score, "kintsugi_fuzzy_phrase"))
        
        return sorted(fuzzy_phrase_scores, key=lambda x: x[1], reverse=True)
    
    def _calculate_phrase_similarity(self, phrase1: str, phrase2: str) -> float:
        """
        Calculate similarity between two phrases.
        
        Args:
            phrase1 (str): First phrase
            phrase2 (str): Second phrase
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not phrase1 or not phrase2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(phrase1)
        set2 = set(phrase2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _count_fuzzy_phrase_occurrences(self, query: str, text: str, threshold: float) -> int:
        """
        Count fuzzy occurrences of a phrase in text.
        
        Args:
            query (str): Query phrase
            text (str): Text to search in
            threshold (float): Similarity threshold
            
        Returns:
            int: Number of fuzzy occurrences
        """
        count = 0
        query_len = len(query)
        text_len = len(text)
        
        # Slide through the text looking for fuzzy matches
        for i in range(text_len - query_len + 1):
            substring = text[i:i + query_len]
            similarity = self._calculate_phrase_similarity(query, substring)
            if similarity >= threshold:
                count += 1
        
        return count
    
    def _find_best_fuzzy_position(self, query: str, text: str, threshold: float) -> int:
        """
        Find the position of the best fuzzy match.
        
        Args:
            query (str): Query phrase
            text (str): Text to search in
            threshold (float): Similarity threshold
            
        Returns:
            int: Position of best match, or -1 if not found
        """
        best_position = -1
        best_similarity = 0.0
        query_len = len(query)
        text_len = len(text)
        
        for i in range(text_len - query_len + 1):
            substring = text[i:i + query_len]
            similarity = self._calculate_phrase_similarity(query, substring)
            if similarity >= threshold and similarity > best_similarity:
                best_similarity = similarity
                best_position = i
        
        return best_position
    
    def _calculate_fuzzy_scores_with_proximity(self, query_tokens: List[str], 
                                             similar_terms: List[Tuple[str, float]], 
                                             doc_ids: List[int], field: Optional[str] = None) -> List[Tuple[int, float, str]]:
        """
        Calculate fuzzy scores with proximity bonuses.
        
        Args:
            query_tokens (List[str]): Query tokens
            similar_terms: List of (term, similarity) tuples
            doc_ids (List[int]): Document IDs to score
            field (Optional[str]): Field to consider for scoring
            
        Returns:
            List[Tuple[int, float, str]]: List of (doc_id, score, match_type) tuples
        """
        scores = []
        
        # Create a mapping from terms to similarities
        term_similarities = {term: sim for term, sim in similar_terms}
        
        for doc_id in doc_ids:
            score = 0.0
            match_types = []
            matched_tokens = 0
            
            for query_token in query_tokens:
                best_match = None
                best_similarity = 0.0
                
                # Find the best matching term in this document
                for term, similarity in similar_terms:
                    if (term, doc_id) in self.term_frequencies:
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = term
                
                if best_match and best_similarity > 0:
                    # Apply graduated scoring based on similarity
                    similarity_multiplier = self._get_similarity_multiplier(best_similarity)
                    
                    # Skip very low quality matches
                    if similarity_multiplier < 0.1:
                        continue
                    
                    # Calculate weighted score
                    tf = self.term_frequencies.get((best_match, doc_id), 0)
                    df = self.document_frequencies.get(best_match, 0)
                    
                    if df > 0:
                        idf = math.log(self.total_documents / df)
                        weighted_score = tf * idf * similarity_multiplier
                        score += weighted_score
                        matched_tokens += 1
                        
                        if best_similarity >= 0.9:
                            match_types.append("exact")
                        elif best_similarity >= 0.8:
                            match_types.append("near_exact")
                        elif best_similarity >= 0.6:
                            match_types.append("fuzzy")
                        else:
                            match_types.append("poor")
            
            # Only include documents that actually matched at least one query token
            if matched_tokens > 0:
                # Apply penalty for partial matches
                match_ratio = matched_tokens / len(query_tokens)
                score *= match_ratio
                
                # Add proximity bonus for multi-word queries
                if len(query_tokens) > 1 and matched_tokens > 1:
                    proximity_bonus = self._calculate_proximity_bonus(query_tokens, doc_id)
                    score *= (1.0 + proximity_bonus)
                
                # Determine overall match type
                if "exact" in match_types:
                    match_type = "kintsugi_exact"
                elif "near_exact" in match_types:
                    match_type = "kintsugi_near"
                elif "fuzzy" in match_types:
                    match_type = "kintsugi_fuzzy"
                else:
                    match_type = "kintsugi_poor"
                
                scores.append((doc_id, score, match_type))
        
        return scores
    
    def _calculate_tfidf_scores(self, query_tokens: List[str], 
                              doc_ids: Set[int], field: Optional[str] = None) -> List[Tuple[int, float]]:
        """
        Calculate TF-IDF scores for documents.
        
        Args:
            query_tokens (List[str]): Query tokens
            doc_ids (Set[int]): Document IDs to score
            field (Optional[str]): Field to consider for scoring
            
        Returns:
            List[Tuple[int, float]]: List of (doc_id, score) tuples
        """
        scores = []
        
        for doc_id in doc_ids:
            score = 0.0
            matched_tokens = 0  # Track how many query tokens actually matched
            
            for token in query_tokens:
                # Calculate TF
                tf = self.term_frequencies.get((token, doc_id), 0)
                if tf == 0:
                    continue
                
                # Calculate IDF
                df = self.document_frequencies.get(token, 0)
                if df == 0:
                    continue
                
                idf = math.log(self.total_documents / df)
                
                # Add to score
                score += tf * idf
                matched_tokens += 1
            
            # Only include documents that actually matched at least one query token
            # and apply a penalty for partial matches
            if matched_tokens > 0:
                # Apply a penalty for partial matches to boost documents with more matches
                match_ratio = matched_tokens / len(query_tokens)
                score *= match_ratio
                scores.append((doc_id, score))
        
        return scores
    
    def _calculate_fuzzy_scores(self, query_tokens: List[str], 
                              similar_terms: List[Tuple[str, float]], 
                              doc_ids: List[int], field: Optional[str] = None) -> List[Tuple[int, float, str]]:
        """
        Calculate fuzzy scores for documents with graduated scoring system.
        
        Args:
            query_tokens (List[str]): Query tokens
            similar_terms: List of (term, similarity) tuples
            doc_ids (List[int]): Document IDs to score
            field (Optional[str]): Field to consider for scoring
            
        Returns:
            List[Tuple[int, float, str]]: List of (doc_id, score, match_type) tuples
        """
        scores = []
        
        # Create a mapping from terms to similarities
        term_similarities = {term: sim for term, sim in similar_terms}
        
        for doc_id in doc_ids:
            score = 0.0
            match_types = []
            matched_tokens = 0
            
            for query_token in query_tokens:
                best_match = None
                best_similarity = 0.0
                
                # Find the best matching term in this document
                for term, similarity in similar_terms:
                    if (term, doc_id) in self.term_frequencies:
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = term
                
                if best_match and best_similarity > 0:
                    # Apply graduated scoring based on similarity
                    similarity_multiplier = self._get_similarity_multiplier(best_similarity)
                    
                    # Skip very low quality matches
                    if similarity_multiplier < 0.1:
                        continue
                    
                    # Calculate weighted score
                    tf = self.term_frequencies.get((best_match, doc_id), 0)
                    df = self.document_frequencies.get(best_match, 0)
                    
                    if df > 0:
                        idf = math.log(self.total_documents / df)
                        weighted_score = tf * idf * similarity_multiplier
                        score += weighted_score
                        matched_tokens += 1
                        
                        if best_similarity >= 0.9:
                            match_types.append("exact")
                        elif best_similarity >= 0.8:
                            match_types.append("near_exact")
                        elif best_similarity >= 0.6:
                            match_types.append("fuzzy")
                        else:
                            match_types.append("poor")
            
            # Only include documents that actually matched at least one query token
            if matched_tokens > 0:
                # Apply penalty for partial matches
                match_ratio = matched_tokens / len(query_tokens)
                score *= match_ratio
                
                # Determine overall match type
                if "exact" in match_types:
                    match_type = "kintsugi_exact"
                elif "near_exact" in match_types:
                    match_type = "kintsugi_near"
                elif "fuzzy" in match_types:
                    match_type = "kintsugi_fuzzy"
                else:
                    match_type = "kintsugi_poor"
                
                scores.append((doc_id, score, match_type))
        
        return scores
    
    def _get_similarity_multiplier(self, similarity: float) -> float:
        """
        Get graduated scoring multiplier based on similarity.
        
        Args:
            similarity (float): Similarity score between 0 and 1
            
        Returns:
            float: Multiplier for scoring (0 to 1)
        """
        if similarity >= 0.95:
            return 1.0  # Perfect match - 100% score
        elif similarity >= 0.9:
            return 0.9  # Near perfect - 90% score
        elif similarity >= 0.8:
            return 0.7  # Good match - 70% score
        elif similarity >= 0.7:
            return 0.5  # Fair match - 50% score
        elif similarity >= 0.6:
            return 0.3  # Poor match - 30% score
        elif similarity >= 0.5:
            return 0.1  # Very poor match - 10% score
        else:
            return 0.0  # Discard very low quality matches
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.
        
        Args:
            doc_id (int): Document ID
            
        Returns:
            Optional[Dict[str, Any]]: Document data if found
        """
        return self.documents.get(doc_id)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dict[str, Any]: Index statistics
        """
        return {
            "total_documents": self.total_documents,
            "total_terms": len(self.term_to_docs),
            "average_doc_length": sum(self.document_lengths.values()) / len(self.document_lengths) if self.document_lengths else 0,
            "field_indexes": {field: len(terms) for field, terms in self.field_indexes.items()},
            "cache_size": len(self.similarity_cache)
        }
    
    def save_index(self, filepath: str) -> None:
        """
        Save the index to a file.
        
        Args:
            filepath (str): Path to save the index
        """
        index_data = {
            "term_to_docs": {term: list(docs) for term, docs in self.term_to_docs.items()},
            "doc_to_terms": {str(doc_id): list(terms) for doc_id, terms in self.doc_to_terms.items()},
            "term_frequencies": {f"{term}|{doc_id}": freq for (term, doc_id), freq in self.term_frequencies.items()},
            "document_frequencies": dict(self.document_frequencies),
            "documents": {str(doc_id): doc for doc_id, doc in self.documents.items()},
            "document_lengths": {str(doc_id): length for doc_id, length in self.document_lengths.items()},
            "field_indexes": {field: {term: list(docs) for term, docs in terms.items()} 
                            for field, terms in self.field_indexes.items()}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Index saved to {filepath}")
    
    def load_index(self, filepath: str) -> None:
        """
        Load the index from a file.
        
        Args:
            filepath (str): Path to load the index from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Reconstruct the index
        self.term_to_docs = {term: set(docs) for term, docs in index_data["term_to_docs"].items()}
        self.doc_to_terms = {int(doc_id): set(terms) for doc_id, terms in index_data["doc_to_terms"].items()}
        self.term_frequencies = {(term.split('|')[0], int(term.split('|')[1])): freq 
                               for term, freq in index_data["term_frequencies"].items()}
        self.document_frequencies = index_data["document_frequencies"]
        self.documents = {int(doc_id): doc for doc_id, doc in index_data["documents"].items()}
        self.document_lengths = {int(doc_id): length for doc_id, length in index_data["document_lengths"].items()}
        
        # Reconstruct field indexes
        self.field_indexes = {}
        for field, terms in index_data["field_indexes"].items():
            self.field_indexes[field] = {term: set(docs) for term, docs in terms.items()}
        
        self.total_documents = len(self.documents)
        logger.info(f"Index loaded from {filepath}")


def main():
    """
    Demo function to test the indexer.
    """
    # This would be used with actual data in the full implementation
    print("=== Inverted Index Demo ===")
    print("This module provides the core indexing functionality.")
    print("Use it with the search engine for full functionality.")


if __name__ == "__main__":
    main()
