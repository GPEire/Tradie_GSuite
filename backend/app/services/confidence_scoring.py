"""
Confidence Scoring and Threshold System
Calculate confidence scores and apply thresholds for auto-grouping
"""

from typing import Dict, List, Optional, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Default confidence thresholds
DEFAULT_THRESHOLDS = {
    "auto_grouping": 0.8,  # 80% confidence for auto-grouping
    "high_confidence": 0.9,  # 90% confidence for high-confidence grouping
    "low_confidence": 0.5,  # 50% below this is low confidence
    "manual_review": 0.6,  # 60% below this requires manual review
    "project_creation": 0.7,  # 70% confidence to create new project
}


class ConfidenceScoringService:
    """Service for calculating and evaluating confidence scores"""
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """Initialize confidence scoring service with custom thresholds"""
        self.thresholds = thresholds or DEFAULT_THRESHOLDS.copy()
        # Allow override from environment variables
        if hasattr(settings, 'confidence_thresholds'):
            self.thresholds.update(settings.confidence_thresholds)
    
    def calculate_weighted_confidence(self, entity_scores: Dict[str, float],
                                     weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate weighted confidence score from multiple entity scores
        
        Args:
            entity_scores: Dictionary of entity type -> confidence score
            weights: Optional weights for each entity type (default: equal weights)
        
        Returns:
            Weighted confidence score (0.0-1.0)
        """
        if not entity_scores:
            return 0.0
        
        # Default weights (address is most important, then job number, then project name)
        default_weights = {
            "address": 0.4,
            "job_number": 0.3,
            "project_name": 0.2,
            "client_match": 0.1
        }
        
        weights = weights or default_weights
        
        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for entity_type, score in entity_scores.items():
            weight = weights.get(entity_type, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def evaluate_grouping_confidence(self, grouping_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate confidence for a grouping result
        
        Args:
            grouping_result: Result from project grouping service
        
        Returns:
            Enhanced result with confidence evaluation
        """
        confidence = grouping_result.get('confidence', 0.0)
        
        evaluation = {
            "confidence": confidence,
            "can_auto_group": confidence >= self.thresholds["auto_grouping"],
            "is_high_confidence": confidence >= self.thresholds["high_confidence"],
            "is_low_confidence": confidence < self.thresholds["low_confidence"],
            "needs_manual_review": confidence < self.thresholds["manual_review"],
            "can_create_project": confidence >= self.thresholds["project_creation"],
            "confidence_level": self._get_confidence_level(confidence)
        }
        
        return {**grouping_result, **evaluation}
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level category"""
        if confidence >= self.thresholds["high_confidence"]:
            return "high"
        elif confidence >= self.thresholds["auto_grouping"]:
            return "medium_high"
        elif confidence >= self.thresholds["manual_review"]:
            return "medium"
        elif confidence >= self.thresholds["low_confidence"]:
            return "low_medium"
        else:
            return "low"
    
    def should_auto_group(self, confidence: float) -> bool:
        """Check if confidence is high enough for auto-grouping"""
        return confidence >= self.thresholds["auto_grouping"]
    
    def should_flag_for_review(self, confidence: float) -> bool:
        """Check if confidence is low enough to flag for manual review"""
        return confidence < self.thresholds["manual_review"]
    
    def evaluate_entity_extraction(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate confidence for entity extraction result
        
        Args:
            extraction_result: Result from entity extraction
        
        Returns:
            Enhanced result with confidence evaluation
        """
        confidence = extraction_result.get('confidence', 0.0)
        
        evaluation = {
            "confidence": confidence,
            "is_high_confidence": confidence >= self.thresholds["high_confidence"],
            "is_low_confidence": confidence < self.thresholds["low_confidence"],
            "needs_manual_review": confidence < self.thresholds["manual_review"],
            "confidence_level": self._get_confidence_level(confidence)
        }
        
        return {**extraction_result, **evaluation}
    
    def combine_confidence_scores(self, scores: List[float], method: str = "average") -> float:
        """
        Combine multiple confidence scores
        
        Args:
            scores: List of confidence scores
            method: Combination method ("average", "max", "min", "weighted")
        
        Returns:
            Combined confidence score
        """
        if not scores:
            return 0.0
        
        if method == "average":
            return sum(scores) / len(scores)
        elif method == "max":
            return max(scores)
        elif method == "min":
            return min(scores)
        elif method == "weighted":
            # Weight recent scores more heavily
            weights = [i + 1 for i in range(len(scores))]
            total_weight = sum(weights)
            return sum(score * weight for score, weight in zip(scores, weights)) / total_weight
        else:
            return sum(scores) / len(scores)
    
    def adjust_confidence_for_indicators(self, base_confidence: float,
                                       indicators: Dict[str, Any]) -> float:
        """
        Adjust confidence based on matching indicators
        
        Args:
            base_confidence: Base confidence score
            indicators: Dictionary of matching indicators (e.g., address_match, job_number_match)
        
        Returns:
            Adjusted confidence score
        """
        adjustment = 0.0
        
        # Positive adjustments
        if indicators.get("address_match") and "same" in str(indicators.get("address_match", "")).lower():
            adjustment += 0.15
        
        if indicators.get("job_number_match") and "same" in str(indicators.get("job_number_match", "")).lower():
            adjustment += 0.10
        
        if indicators.get("project_name_match") and "same" in str(indicators.get("project_name_match", "")).lower():
            adjustment += 0.05
        
        # Negative adjustments
        if indicators.get("address_match") and "different" in str(indicators.get("address_match", "")).lower():
            adjustment -= 0.20
        
        if indicators.get("client_match") and "different" in str(indicators.get("client_match", "")).lower():
            adjustment -= 0.10
        
        # Apply adjustment (clamp between 0.0 and 1.0)
        adjusted = base_confidence + adjustment
        return max(0.0, min(1.0, adjusted))
    
    def flag_low_confidence_groups(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Flag groups with low confidence for review
        
        Args:
            groups: List of project groups
        
        Returns:
            Groups with flags added for low-confidence items
        """
        flagged_groups = []
        
        for group in groups:
            confidence = group.get('confidence', 0.0)
            
            if self.should_flag_for_review(confidence):
                group['flags'] = group.get('flags', [])
                group['flags'].append('low_confidence')
                group['needs_review'] = True
            
            if confidence < self.thresholds["low_confidence"]:
                group['flags'] = group.get('flags', [])
                group['flags'].append('very_low_confidence')
                group['needs_review'] = True
            
            flagged_groups.append(group)
        
        return flagged_groups
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current confidence thresholds"""
        return self.thresholds.copy()
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update confidence thresholds"""
        self.thresholds.update(new_thresholds)
        logger.info(f"Updated confidence thresholds: {new_thresholds}")


def get_confidence_scoring_service(thresholds: Optional[Dict[str, float]] = None) -> ConfidenceScoringService:
    """Factory function to create confidence scoring service"""
    return ConfidenceScoringService(thresholds)

