"""
AI Model Learning System
Feedback loop for user corrections and model improvement
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging
from app.models.learning import UserCorrection, ModelFeedback, LearningPattern
from app.models.user import User
from collections import Counter

logger = logging.getLogger(__name__)


class LearningService:
    """Service for managing AI model learning from user feedback"""
    
    def __init__(self, db: Session):
        """Initialize learning service"""
        self.db = db
    
    def record_correction(self, user_id: int, correction_type: str,
                         original_result: Dict[str, Any], corrected_result: Dict[str, Any],
                         email_id: Optional[str] = None, project_id: Optional[str] = None,
                         original_confidence: Optional[float] = None,
                         correction_reason: Optional[str] = None) -> UserCorrection:
        """
        Record a user correction to AI grouping
        
        Args:
            user_id: User making the correction
            correction_type: Type of correction (project_assignment, merge, split, rename)
            original_result: Original AI result
            corrected_result: User's correction
            email_id: Related email ID
            project_id: Related project ID
            original_confidence: Original confidence score
            correction_reason: Optional reason for correction
        """
        # Extract learning features
        learning_features = self._extract_learning_features(original_result, corrected_result)
        
        correction = UserCorrection(
            user_id=user_id,
            correction_type=correction_type,
            original_result=original_result,
            corrected_result=corrected_result,
            email_id=email_id,
            project_id=project_id,
            original_confidence=str(original_confidence) if original_confidence else None,
            learning_features=learning_features,
            correction_reason=correction_reason
        )
        
        self.db.add(correction)
        self.db.commit()
        self.db.refresh(correction)
        
        logger.info(f"Recorded correction {correction.id} for user {user_id}, type: {correction_type}")
        
        return correction
    
    def _extract_learning_features(self, original: Dict[str, Any], 
                                  corrected: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for learning from correction"""
        features = {
            "original_project_name": original.get("project_name"),
            "corrected_project_name": corrected.get("project_name"),
            "original_address": original.get("address"),
            "corrected_address": corrected.get("address"),
            "original_job_numbers": original.get("job_numbers", []),
            "corrected_job_numbers": corrected.get("job_numbers", []),
            "differences": self._find_differences(original, corrected)
        }
        return features
    
    def _find_differences(self, original: Dict[str, Any], 
                        corrected: Dict[str, Any]) -> Dict[str, Any]:
        """Find differences between original and corrected results"""
        differences = {}
        
        for key in ["project_name", "address", "client_info"]:
            if original.get(key) != corrected.get(key):
                differences[key] = {
                    "original": original.get(key),
                    "corrected": corrected.get(key)
                }
        
        return differences
    
    def submit_feedback(self, user_id: int, feedback_type: str,
                       category: Optional[str] = None, feedback_text: Optional[str] = None,
                       feedback_data: Optional[Dict[str, Any]] = None,
                       email_ids: Optional[List[str]] = None,
                       project_ids: Optional[List[str]] = None,
                       impact_score: Optional[int] = None) -> ModelFeedback:
        """Submit feedback for model improvement"""
        feedback = ModelFeedback(
            user_id=user_id,
            feedback_type=feedback_type,
            category=category,
            feedback_text=feedback_text,
            feedback_data=feedback_data,
            email_ids=email_ids,
            project_ids=project_ids,
            impact_score=impact_score
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        logger.info(f"Submitted feedback {feedback.id} for user {user_id}, type: {feedback_type}")
        
        return feedback
    
    def analyze_corrections(self, user_id: Optional[int] = None,
                           limit: int = 100) -> Dict[str, Any]:
        """
        Analyze user corrections to identify patterns
        
        Args:
            user_id: Optional user ID to filter by (None = all users)
            limit: Maximum number of corrections to analyze
        """
        query = self.db.query(UserCorrection).filter(
            UserCorrection.is_processed == False
        )
        
        if user_id:
            query = query.filter(UserCorrection.user_id == user_id)
        
        corrections = query.order_by(UserCorrection.created_at.desc()).limit(limit).all()
        
        if not corrections:
            return {"patterns": [], "summary": {}}
        
        # Analyze patterns
        correction_types = Counter([c.correction_type for c in corrections])
        
        # Extract common patterns
        project_name_variations = []
        address_patterns = []
        
        for correction in corrections:
            features = correction.learning_features or {}
            if features.get("original_project_name") and features.get("corrected_project_name"):
                project_name_variations.append({
                    "original": features["original_project_name"],
                    "corrected": features["corrected_project_name"]
                })
            
            if features.get("original_address") and features.get("corrected_address"):
                address_patterns.append({
                    "original": features["original_address"],
                    "corrected": features["corrected_address"]
                })
        
        return {
            "total_corrections": len(corrections),
            "correction_types": dict(correction_types),
            "project_name_variations": project_name_variations[:10],
            "address_patterns": address_patterns[:10],
            "patterns": self._identify_patterns(corrections)
        }
    
    def _identify_patterns(self, corrections: List[UserCorrection]) -> List[Dict[str, Any]]:
        """Identify learning patterns from corrections"""
        patterns = []
        
        # Group by correction type
        by_type = {}
        for correction in corrections:
            corr_type = correction.correction_type
            if corr_type not in by_type:
                by_type[corr_type] = []
            by_type[corr_type].append(correction)
        
        # Analyze each type
        for corr_type, corr_list in by_type.items():
            if len(corr_list) >= 3:  # Need at least 3 corrections to establish pattern
                pattern = {
                    "type": corr_type,
                    "frequency": len(corr_list),
                    "examples": [
                        {
                            "original": c.original_result.get("project_name"),
                            "corrected": c.corrected_result.get("project_name")
                        }
                        for c in corr_list[:3]
                    ]
                }
                patterns.append(pattern)
        
        return patterns
    
    def create_learning_pattern(self, pattern_type: str, pattern_key: str,
                               pattern_data: Dict[str, Any], user_id: Optional[int] = None,
                               is_global: bool = False) -> LearningPattern:
        """Create a learning pattern from identified corrections"""
        pattern = LearningPattern(
            pattern_type=pattern_type,
            pattern_key=pattern_key,
            pattern_data=pattern_data,
            user_id=user_id,
            is_global=is_global,
            is_active=True
        )
        
        self.db.add(pattern)
        self.db.commit()
        self.db.refresh(pattern)
        
        logger.info(f"Created learning pattern {pattern.id}, type: {pattern_type}")
        
        return pattern
    
    def apply_learning_patterns(self, email_data: Dict[str, Any],
                               user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Apply learned patterns to improve extraction
        
        Args:
            email_data: Email data to process
            user_id: Optional user ID for user-specific patterns
        
        Returns:
            Enhanced extraction with learned patterns applied
        """
        # Get active patterns
        query = self.db.query(LearningPattern).filter(
            LearningPattern.is_active == True
        ).filter(
            (LearningPattern.is_global == True) | (LearningPattern.user_id == user_id)
        )
        
        patterns = query.all()
        
        # Apply patterns (simplified - full implementation would match patterns)
        enhanced_data = email_data.copy()
        
        for pattern in patterns:
            if pattern.pattern_type == "project_name_variation":
                # Apply project name variations
                # This would match and apply learned variations
                pass
        
        return enhanced_data
    
    def mark_corrections_processed(self, correction_ids: List[int]) -> int:
        """Mark corrections as processed"""
        updated = self.db.query(UserCorrection).filter(
            UserCorrection.id.in_(correction_ids)
        ).update({
            UserCorrection.is_processed: True,
            UserCorrection.processed_at: datetime.utcnow()
        })
        
        self.db.commit()
        return updated


def get_learning_service(db: Session) -> LearningService:
    """Factory function to create learning service"""
    return LearningService(db)

