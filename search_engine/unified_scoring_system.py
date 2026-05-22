"""
Unified Scoring System for Kintsugi Search + Recommendation Engine
================================================================

This module implements a comprehensive scoring system that blends all ranking factors:
- Text-based search scores (TF-IDF + cosine similarity)
- Vector search scores (semantic similarity)
- PageRank-inspired scores (product relationships)
- Polya Urn Model scores (click-based boosting)
- Granovetter Cascade scores (viral recommendations)
- Kintsugi repair scores (quality improvements)

The system embodies the Kintsugi philosophy by treating each scoring component
as a "golden seam" that makes the overall result more beautiful and valuable.

Author: Search Engine Implementation
Date: 2025
"""

import logging
import json
import math
import time
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
from pathlib import Path
import numpy as np

# Import our custom modules
from polya_urn_model import PolyaUrnModel
from granovetter_cascade import GranovetterCascadeModel
from kintsugi_repair_system import KintsugiRepairSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedScoringSystem:
    """
    Unified scoring system that blends all ranking factors.
    
    This class implements a comprehensive scoring system that combines
    multiple ranking signals to provide the best possible search and
    recommendation results.
    """
    
    def __init__(self):
        """Initialize the unified scoring system."""
        # Scoring weights for different components
        self.scoring_weights = {
            'text_search': 0.25,      # TF-IDF + cosine similarity
            'vector_search': 0.20,    # Semantic similarity
            'pagerank': 0.15,         # Product relationships
            'polya_urn': 0.15,        # Click-based boosting
            'cascade': 0.10,          # Viral recommendations
            'kintsugi_repair': 0.10,  # Quality improvements
            'freshness': 0.05         # Recency bonus
        }
        
        # Component instances
        self.polya_urn = PolyaUrnModel()
        self.cascade_model = GranovetterCascadeModel()
        self.repair_system = KintsugiRepairSystem()
        
        # Scoring history and statistics
        self.scoring_history = []
        self.score_statistics = defaultdict(list)
        
        # Kintsugi metadata
        self.kintsugi_notes = []
    
    def calculate_unified_score(self, 
                              text_score: float,
                              vector_score: float,
                              pagerank_score: float,
                              polya_urn_score: float,
                              cascade_score: float,
                              repair_score: float,
                              freshness_score: float = 0.0,
                              custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate unified score by blending all ranking factors.
        
        Args:
            text_score (float): Text-based search score
            vector_score (float): Vector search score
            pagerank_score (float): PageRank score
            polya_urn_score (float): Polya Urn Model score
            cascade_score (float): Cascade model score
            repair_score (float): Kintsugi repair score
            freshness_score (float): Freshness bonus score
            custom_weights (Optional[Dict[str, float]]): Custom scoring weights
            
        Returns:
            Dict[str, Any]: Unified score with component breakdown
        """
        # Use custom weights if provided, otherwise use default
        weights = custom_weights if custom_weights else self.scoring_weights
        
        # Normalize weights to ensure they sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted score
        unified_score = (
            text_score * weights['text_search'] +
            vector_score * weights['vector_search'] +
            pagerank_score * weights['pagerank'] +
            polya_urn_score * weights['polya_urn'] +
            cascade_score * weights['cascade'] +
            repair_score * weights['kintsugi_repair'] +
            freshness_score * weights['freshness']
        )
        
        # Calculate component contributions
        component_scores = {
            'text_search': text_score * weights['text_search'],
            'vector_search': vector_score * weights['vector_search'],
            'pagerank': pagerank_score * weights['pagerank'],
            'polya_urn': polya_urn_score * weights['polya_urn'],
            'cascade': cascade_score * weights['cascade'],
            'kintsugi_repair': repair_score * weights['kintsugi_repair'],
            'freshness': freshness_score * weights['freshness']
        }
        
        # Calculate score quality metrics
        score_quality = self._calculate_score_quality(unified_score, component_scores)
        
        # Generate Kintsugi insights
        kintsugi_insights = self._generate_scoring_insights(component_scores, unified_score)
        
        # Record scoring event
        self._record_scoring_event(component_scores, unified_score, score_quality)
        
        return {
            'unified_score': unified_score,
            'component_scores': component_scores,
            'weights_used': weights,
            'score_quality': score_quality,
            'kintsugi_insights': kintsugi_insights,
            'timestamp': time.time()
        }
    
    def _calculate_score_quality(self, unified_score: float, 
                               component_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate quality metrics for the unified score."""
        # Score magnitude
        magnitude = 'high' if unified_score > 0.7 else 'medium' if unified_score > 0.4 else 'low'
        
        # Score balance (how evenly distributed the components are)
        component_values = list(component_scores.values())
        if component_values:
            balance = 1.0 - (max(component_values) - min(component_values))
        else:
            balance = 0.0
        
        # Score diversity (how many components contribute significantly)
        significant_components = sum(1 for score in component_values if score > 0.1)
        diversity = significant_components / len(component_values)
        
        # Overall quality assessment
        if unified_score > 0.8 and balance > 0.6 and diversity > 0.5:
            quality_level = 'excellent'
        elif unified_score > 0.6 and balance > 0.4 and diversity > 0.3:
            quality_level = 'good'
        elif unified_score > 0.4:
            quality_level = 'fair'
        else:
            quality_level = 'poor'
        
        return {
            'magnitude': magnitude,
            'balance': balance,
            'diversity': diversity,
            'quality_level': quality_level,
            'significant_components': significant_components
        }
    
    def _generate_scoring_insights(self, component_scores: Dict[str, float], 
                                 unified_score: float) -> List[str]:
        """Generate Kintsugi insights about the scoring process."""
        insights = []
        
        # Analyze dominant components
        dominant_components = [k for k, v in component_scores.items() if v > 0.2]
        if dominant_components:
            insights.append(f"🌟 Dominant signals: {', '.join(dominant_components)}")
        
        # Analyze score strength
        if unified_score > 0.8:
            insights.append("✨ Strong unified score - all components working in harmony")
        elif unified_score > 0.6:
            insights.append("🔧 Good unified score - most components contributing well")
        elif unified_score > 0.4:
            insights.append("⚖️ Moderate unified score - some components need strengthening")
        else:
            insights.append("🔨 Weak unified score - components need repair and enhancement")
        
        # Analyze component balance
        component_values = list(component_scores.values())
        if component_values:
            max_component = max(component_values)
            min_component = min(component_values)
            
            if max_component - min_component < 0.1:
                insights.append("🎨 Well-balanced scoring - all components contributing evenly")
            elif max_component > 0.5:
                insights.append("🎯 Focused scoring - one component dominates")
            else:
                insights.append("🔀 Distributed scoring - multiple components contributing")
        
        # Kintsugi philosophy
        insights.append("💫 Every score component is a golden seam in the final result")
        
        return insights
    
    def _record_scoring_event(self, component_scores: Dict[str, float], 
                            unified_score: float, score_quality: Dict[str, Any]) -> None:
        """Record a scoring event for analysis."""
        scoring_event = {
            'component_scores': component_scores,
            'unified_score': unified_score,
            'score_quality': score_quality,
            'timestamp': time.time()
        }
        
        self.scoring_history.append(scoring_event)
        
        # Update statistics
        self.score_statistics['unified_scores'].append(unified_score)
        for component, score in component_scores.items():
            self.score_statistics[f'{component}_scores'].append(score)
    
    def rank_results(self, results: List[Dict[str, Any]], 
                    user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Rank search results using the unified scoring system.
        
        Args:
            results (List[Dict[str, Any]]): List of search results
            user_id (Optional[str]): User identifier for personalization
            
        Returns:
            List[Dict[str, Any]]: Ranked results with unified scores
        """
        ranked_results = []
        
        for result in results:
            # Extract component scores
            text_score = result.get('text_score', 0.0)
            vector_score = result.get('vector_score', 0.0)
            pagerank_score = result.get('pagerank_score', 0.0)
            
            # Get Polya Urn score
            product_id = result.get('doc_id', result.get('product_id', 0))
            polya_urn_score = self.polya_urn.get_product_probability(product_id)
            
            # Get cascade score
            cascade_score = self.cascade_model.get_viral_products(1)
            if cascade_score and cascade_score[0][0] == product_id:
                cascade_score = cascade_score[0][1]
            else:
                cascade_score = 0.0
            
            # Get repair score
            repair_score = self._calculate_repair_score(result)
            
            # Get freshness score
            freshness_score = self._calculate_freshness_score(result)
            
            # Calculate unified score
            scoring_result = self.calculate_unified_score(
                text_score, vector_score, pagerank_score,
                polya_urn_score, cascade_score, repair_score, freshness_score
            )
            
            # Add unified score to result
            result['unified_score'] = scoring_result['unified_score']
            result['component_scores'] = scoring_result['component_scores']
            result['score_quality'] = scoring_result['score_quality']
            result['kintsugi_insights'] = scoring_result['kintsugi_insights']
            
            ranked_results.append(result)
        
        # Sort by unified score
        ranked_results.sort(key=lambda x: x['unified_score'], reverse=True)
        
        return ranked_results
    
    def _calculate_repair_score(self, result: Dict[str, Any]) -> float:
        """Calculate Kintsugi repair score for a result."""
        # Check if result has repair metadata
        if 'repair_notes' in result:
            repair_count = len(result['repair_notes'])
            return min(1.0, repair_count * 0.2)  # 0.2 per repair, max 1.0
        
        # Check for quality indicators
        quality = result.get('kintsugi_quality', 'poor')
        quality_scores = {
            'perfect': 1.0,
            'excellent': 0.8,
            'good': 0.6,
            'fair': 0.4,
            'poor': 0.2
        }
        
        return quality_scores.get(quality, 0.2)
    
    def _calculate_freshness_score(self, result: Dict[str, Any]) -> float:
        """Calculate freshness score for a result."""
        # Check for timestamp in result
        if 'timestamp' in result:
            age_hours = (time.time() - result['timestamp']) / 3600
            if age_hours < 1:
                return 1.0
            elif age_hours < 24:
                return 0.8
            elif age_hours < 168:  # 1 week
                return 0.6
            else:
                return 0.4
        
        # Default freshness score
        return 0.5
    
    def optimize_weights(self, training_data: List[Dict[str, Any]], 
                        target_metric: str = 'relevance') -> Dict[str, float]:
        """
        Optimize scoring weights based on training data.
        
        Args:
            training_data (List[Dict[str, Any]]): Training data with known relevance
            target_metric (str): Target metric to optimize for
            
        Returns:
            Dict[str, float]: Optimized weights
        """
        # Simple optimization using grid search
        best_weights = self.scoring_weights.copy()
        best_score = 0.0
        
        # Define weight ranges for optimization
        weight_ranges = {
            'text_search': [0.1, 0.2, 0.3, 0.4, 0.5],
            'vector_search': [0.1, 0.2, 0.3, 0.4, 0.5],
            'pagerank': [0.05, 0.1, 0.15, 0.2, 0.25],
            'polya_urn': [0.05, 0.1, 0.15, 0.2, 0.25],
            'cascade': [0.05, 0.1, 0.15, 0.2],
            'kintsugi_repair': [0.05, 0.1, 0.15, 0.2],
            'freshness': [0.02, 0.05, 0.1, 0.15]
        }
        
        # Grid search optimization
        for text_w in weight_ranges['text_search']:
            for vector_w in weight_ranges['vector_search']:
                for pagerank_w in weight_ranges['pagerank']:
                    for polya_w in weight_ranges['polya_urn']:
                        for cascade_w in weight_ranges['cascade']:
                            for repair_w in weight_ranges['kintsugi_repair']:
                                for freshness_w in weight_ranges['freshness']:
                                    # Ensure weights sum to 1.0
                                    total = text_w + vector_w + pagerank_w + polya_w + cascade_w + repair_w + freshness_w
                                    if abs(total - 1.0) < 0.01:  # Allow small floating point errors
                                        weights = {
                                            'text_search': text_w,
                                            'vector_search': vector_w,
                                            'pagerank': pagerank_w,
                                            'polya_urn': polya_w,
                                            'cascade': cascade_w,
                                            'kintsugi_repair': repair_w,
                                            'freshness': freshness_w
                                        }
                                        
                                        # Evaluate weights on training data
                                        score = self._evaluate_weights(weights, training_data, target_metric)
                                        
                                        if score > best_score:
                                            best_score = score
                                            best_weights = weights
        
        self.scoring_weights = best_weights
        self.kintsugi_notes.append(f"🔧 Optimized scoring weights with score {best_score:.3f}")
        
        return best_weights
    
    def _evaluate_weights(self, weights: Dict[str, float], 
                         training_data: List[Dict[str, Any]], 
                         target_metric: str) -> float:
        """Evaluate weights on training data."""
        # Simple evaluation - in practice, this would be more sophisticated
        total_score = 0.0
        
        for data_point in training_data:
            # Calculate unified score with given weights
            unified_score = self.calculate_unified_score(
                data_point.get('text_score', 0.0),
                data_point.get('vector_score', 0.0),
                data_point.get('pagerank_score', 0.0),
                data_point.get('polya_urn_score', 0.0),
                data_point.get('cascade_score', 0.0),
                data_point.get('repair_score', 0.0),
                data_point.get('freshness_score', 0.0),
                weights
            )['unified_score']
            
            # Compare with target relevance
            target_relevance = data_point.get('relevance', 0.0)
            score = 1.0 - abs(unified_score - target_relevance)
            total_score += score
        
        return total_score / len(training_data) if training_data else 0.0
    
    def get_scoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scoring statistics."""
        stats = {}
        
        for component, scores in self.score_statistics.items():
            if scores:
                stats[component] = {
                    'mean': np.mean(scores),
                    'std': np.std(scores),
                    'min': np.min(scores),
                    'max': np.max(scores),
                    'count': len(scores)
                }
        
        # Overall statistics
        if 'unified_scores' in self.score_statistics:
            unified_scores = self.score_statistics['unified_scores']
            stats['overall'] = {
                'mean_unified_score': np.mean(unified_scores),
                'score_distribution': {
                    'high': sum(1 for s in unified_scores if s > 0.7),
                    'medium': sum(1 for s in unified_scores if 0.4 <= s <= 0.7),
                    'low': sum(1 for s in unified_scores if s < 0.4)
                }
            }
        
        return stats
    
    def get_kintsugi_insights(self) -> List[str]:
        """Get Kintsugi insights about the scoring system."""
        insights = []
        
        stats = self.get_scoring_statistics()
        
        if 'overall' in stats:
            overall = stats['overall']
            insights.append(f"📊 Mean unified score: {overall['mean_unified_score']:.3f}")
            
            dist = overall['score_distribution']
            total = dist['high'] + dist['medium'] + dist['low']
            if total > 0:
                high_pct = (dist['high'] / total) * 100
                insights.append(f"🌟 {high_pct:.1f}% of scores are high quality")
        
        # Analyze component contributions
        component_means = {}
        for component, comp_stats in stats.items():
            if component != 'overall' and 'mean' in comp_stats:
                component_means[component] = comp_stats['mean']
        
        if component_means:
            dominant_component = max(component_means.items(), key=lambda x: x[1])
            insights.append(f"🎯 Dominant component: {dominant_component[0]} ({dominant_component[1]:.3f})")
        
        # Kintsugi philosophy
        insights.append("💫 Every scoring component contributes to the golden result")
        insights.append("🔧 The unified score is greater than the sum of its parts")
        
        return insights
    
    def save_scoring_system(self, filepath: str) -> None:
        """Save the scoring system to file."""
        data = {
            'scoring_weights': self.scoring_weights,
            'scoring_history': self.scoring_history[-1000:],  # Keep last 1000 events
            'score_statistics': dict(self.score_statistics),
            'kintsugi_notes': self.kintsugi_notes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Scoring system saved to {filepath}")
    
    def load_scoring_system(self, filepath: str) -> None:
        """Load the scoring system from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.scoring_weights = data.get('scoring_weights', self.scoring_weights)
        self.scoring_history = data.get('scoring_history', [])
        self.score_statistics = defaultdict(list, data.get('score_statistics', {}))
        self.kintsugi_notes = data.get('kintsugi_notes', [])
        
        logger.info(f"Scoring system loaded from {filepath}")


def main():
    """Demo function to test the unified scoring system."""
    print("=== Unified Scoring System Demo ===")
    
    scoring_system = UnifiedScoringSystem()
    
    # Test unified scoring
    test_scores = {
        'text_score': 0.8,
        'vector_score': 0.7,
        'pagerank_score': 0.6,
        'polya_urn_score': 0.5,
        'cascade_score': 0.4,
        'repair_score': 0.9,
        'freshness_score': 0.3
    }
    
    result = scoring_system.calculate_unified_score(**test_scores)
    
    print(f"Unified Score: {result['unified_score']:.3f}")
    print(f"Score Quality: {result['score_quality']['quality_level']}")
    print(f"Component Scores:")
    for component, score in result['component_scores'].items():
        print(f"  {component}: {score:.3f}")
    
    print(f"\nKintsugi Insights:")
    for insight in result['kintsugi_insights']:
        print(f"  {insight}")
    
    # Test ranking
    test_results = [
        {'doc_id': 1, 'text_score': 0.8, 'vector_score': 0.7, 'pagerank_score': 0.6},
        {'doc_id': 2, 'text_score': 0.6, 'vector_score': 0.8, 'pagerank_score': 0.7},
        {'doc_id': 3, 'text_score': 0.7, 'vector_score': 0.6, 'pagerank_score': 0.8}
    ]
    
    ranked_results = scoring_system.rank_results(test_results)
    
    print(f"\nRanked Results:")
    for i, result in enumerate(ranked_results):
        print(f"  {i+1}. Doc {result['doc_id']}: {result['unified_score']:.3f}")


if __name__ == "__main__":
    main()
