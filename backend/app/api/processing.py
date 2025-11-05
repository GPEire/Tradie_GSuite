"""
AI Processing API Routes
Endpoints for AI processing queue, batch jobs, confidence scoring, and learning
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.ai_processing import get_ai_processing_service, get_batch_processing_service
from app.services.confidence_scoring import get_confidence_scoring_service
from app.services.learning import get_learning_service
from app.models.ai_processing import BatchProcessingJob
from app.schemas.processing import (
    ProcessingQueueItem, BatchJobRequest, BatchJobResponse,
    ConfidenceThresholds, CorrectionRequest, FeedbackRequest
)
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


# TASK-013: AI Processing Queue Endpoints

@router.post("/queue/email")
async def queue_email_processing(
    email_id: str,
    thread_id: Optional[str] = None,
    priority: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Queue an email for AI processing (TASK-013)"""
    try:
        processing_service = get_ai_processing_service(db)
        queue_item = processing_service.queue_email_processing(
            user_id=current_user.id,
            email_id=email_id,
            thread_id=thread_id,
            priority=priority
        )
        return {"queue_item_id": queue_item.id, "status": queue_item.status}
    except Exception as e:
        logger.error(f"Error queueing email processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue email processing: {str(e)}"
        )


@router.post("/queue/process")
async def process_pending_queue(
    limit: int = 50,
    priority_threshold: int = 0,
    db: Session = Depends(get_db)
):
    """Process pending items from queue (TASK-013)"""
    try:
        processing_service = get_ai_processing_service(db)
        results = processing_service.process_pending_queue(
            limit=limit,
            priority_threshold=priority_threshold
        )
        return results
    except Exception as e:
        logger.error(f"Error processing queue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process queue: {str(e)}"
        )


@router.post("/batch/create", response_model=BatchJobResponse)
async def create_batch_job(
    request: BatchJobRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a retroactive scan batch job (TASK-013)"""
    try:
        batch_service = get_batch_processing_service(db)
        job = batch_service.create_retroactive_scan_job(
            user_id=current_user.id,
            date_start=request.date_start,
            date_end=request.date_end,
            batch_size=request.batch_size
        )
        return BatchJobResponse(
            id=job.id,
            user_id=job.user_id,
            job_type=job.job_type,
            status=job.status,
            total_items=job.total_items,
            processed_items=job.processed_items,
            failed_items=job.failed_items,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at
        )
    except Exception as e:
        logger.error(f"Error creating batch job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch job: {str(e)}"
        )


@router.post("/batch/{job_id}/execute")
async def execute_batch_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute a batch processing job (TASK-013)"""
    try:
        batch_service = get_batch_processing_service(db)
        result = batch_service.execute_retroactive_scan(
            db.query(BatchProcessingJob).filter(BatchProcessingJob.id == job_id).first()
        )
        return result
    except Exception as e:
        logger.error(f"Error executing batch job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute batch job: {str(e)}"
        )


# TASK-014: Confidence Scoring Endpoints

@router.get("/confidence/thresholds")
async def get_confidence_thresholds():
    """Get current confidence thresholds (TASK-014)"""
    scoring_service = get_confidence_scoring_service()
    return scoring_service.get_thresholds()


@router.post("/confidence/thresholds")
async def update_confidence_thresholds(
    thresholds: ConfidenceThresholds,
    current_user: User = Depends(get_current_active_user)
):
    """Update confidence thresholds (TASK-014)"""
    try:
        scoring_service = get_confidence_scoring_service()
        scoring_service.update_thresholds(thresholds.dict())
        return {"message": "Thresholds updated successfully"}
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update thresholds: {str(e)}"
        )


@router.post("/confidence/evaluate")
async def evaluate_confidence(
    grouping_result: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Evaluate confidence for a grouping result (TASK-014)"""
    try:
        scoring_service = get_confidence_scoring_service()
        evaluation = scoring_service.evaluate_grouping_confidence(grouping_result)
        return evaluation
    except Exception as e:
        logger.error(f"Error evaluating confidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate confidence: {str(e)}"
        )


# TASK-015: Learning System Endpoints

@router.post("/learning/correction")
async def record_correction(
    request: CorrectionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a user correction to AI grouping (TASK-015)"""
    try:
        learning_service = get_learning_service(db)
        correction = learning_service.record_correction(
            user_id=current_user.id,
            correction_type=request.correction_type,
            original_result=request.original_result,
            corrected_result=request.corrected_result,
            email_id=request.email_id,
            project_id=request.project_id,
            correction_reason=request.correction_reason
        )
        return {"correction_id": correction.id, "message": "Correction recorded"}
    except Exception as e:
        logger.error(f"Error recording correction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record correction: {str(e)}"
        )


@router.post("/learning/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for model improvement (TASK-015)"""
    try:
        learning_service = get_learning_service(db)
        feedback = learning_service.submit_feedback(
            user_id=current_user.id,
            feedback_type=request.feedback_type,
            category=request.category,
            feedback_text=request.feedback_text,
            feedback_data=request.feedback_data,
            email_ids=request.email_ids,
            project_ids=request.project_ids,
            impact_score=request.impact_score
        )
        return {"feedback_id": feedback.id, "message": "Feedback submitted"}
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/learning/analyze")
async def analyze_corrections(
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze user corrections to identify patterns (TASK-015)"""
    try:
        learning_service = get_learning_service(db)
        analysis = learning_service.analyze_corrections(
            user_id=current_user.id,
            limit=limit
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing corrections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze corrections: {str(e)}"
        )

