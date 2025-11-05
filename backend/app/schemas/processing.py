"""
AI Processing Schemas
Pydantic models for AI processing requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProcessingQueueItem(BaseModel):
    """Processing queue item"""
    id: int
    user_id: int
    task_type: str
    email_id: Optional[str] = None
    status: str
    priority: int
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BatchJobRequest(BaseModel):
    """Request to create batch processing job"""
    date_start: datetime
    date_end: datetime
    batch_size: int = 50


class BatchJobResponse(BaseModel):
    """Response for batch processing job"""
    id: int
    user_id: int
    job_type: str
    status: str
    total_items: int
    processed_items: int
    failed_items: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfidenceThresholds(BaseModel):
    """Confidence thresholds configuration"""
    auto_grouping: float = Field(default=0.8, ge=0.0, le=1.0)
    high_confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    low_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    manual_review: float = Field(default=0.6, ge=0.0, le=1.0)
    project_creation: float = Field(default=0.7, ge=0.0, le=1.0)


class CorrectionRequest(BaseModel):
    """Request to record user correction"""
    correction_type: str  # project_assignment, merge, split, rename
    original_result: Dict[str, Any]
    corrected_result: Dict[str, Any]
    email_id: Optional[str] = None
    project_id: Optional[str] = None
    correction_reason: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Request to submit feedback"""
    feedback_type: str  # accuracy, false_positive, false_negative, suggestion
    category: Optional[str] = None
    feedback_text: Optional[str] = None
    feedback_data: Optional[Dict[str, Any]] = None
    email_ids: Optional[List[str]] = None
    project_ids: Optional[List[str]] = None
    impact_score: Optional[int] = Field(None, ge=1, le=10)

