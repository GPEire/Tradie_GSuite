"""
AI Model Learning Models
Database models for storing user corrections and feedback for model improvement
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserCorrection(Base):
    """User corrections to AI grouping decisions"""
    __tablename__ = "user_corrections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Correction details
    correction_type = Column(String, nullable=False, index=True)  # project_assignment, project_merge, project_split, project_rename
    original_result = Column(JSON, nullable=False)  # Original AI result
    corrected_result = Column(JSON, nullable=False)  # User's correction
    
    # Context
    email_id = Column(String, nullable=True, index=True)
    project_id = Column(String, nullable=True, index=True)
    original_confidence = Column(String, nullable=True)  # Original confidence score
    
    # Learning data
    learning_features = Column(JSON, nullable=True)  # Features extracted for learning
    correction_reason = Column(Text, nullable=True)  # User's reason for correction (optional)
    
    # Status
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="corrections")

    def __repr__(self):
        return f"<UserCorrection user_id={self.user_id} type={self.correction_type} email_id={self.email_id}>"


class ModelFeedback(Base):
    """Feedback for model improvement"""
    __tablename__ = "model_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Feedback details
    feedback_type = Column(String, nullable=False)  # accuracy, false_positive, false_negative, suggestion
    category = Column(String, nullable=True)  # project_naming, address_detection, grouping, etc.
    
    # Feedback content
    feedback_text = Column(Text, nullable=True)
    feedback_data = Column(JSON, nullable=True)  # Structured feedback data
    
    # Context
    email_ids = Column(JSON, nullable=True)  # Related email IDs
    project_ids = Column(JSON, nullable=True)  # Related project IDs
    
    # Learning data
    features = Column(JSON, nullable=True)  # Features for learning
    impact_score = Column(Integer, nullable=True)  # 1-10, how important this feedback is
    
    # Status
    is_reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="feedback")

    def __repr__(self):
        return f"<ModelFeedback user_id={self.user_id} type={self.feedback_type} category={self.category}>"


class LearningPattern(Base):
    """Learned patterns from user corrections"""
    __tablename__ = "learning_patterns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Pattern details
    pattern_type = Column(String, nullable=False, index=True)  # project_name_variation, address_format, etc.
    pattern_key = Column(String, nullable=False, index=True)  # Pattern identifier
    pattern_data = Column(JSON, nullable=False)  # Pattern data
    
    # Learning metrics
    confidence_score = Column(String, nullable=True)  # Confidence in this pattern
    usage_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    
    # User context (optional)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_global = Column(Boolean, default=False, nullable=False)  # Apply to all users
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="learning_patterns")

    def __repr__(self):
        return f"<LearningPattern type={self.pattern_type} key={self.pattern_key} active={self.is_active}>"

