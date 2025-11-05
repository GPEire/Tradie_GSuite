"""
Project Grouping API Routes
Endpoints for entity extraction, similarity analysis, and project grouping
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.ai import AIService, AIServiceError, get_ai_service
from app.services.entity_extraction import EntityExtractionService, get_entity_extraction_service
from app.services.similarity import SimilarityService, get_similarity_service
from app.services.project_grouping import ProjectGroupingService, get_project_grouping_service
from app.schemas.project import (
    EntityExtractionRequest, EntityExtractionResult,
    SimilarityComparisonRequest, SimilarityComparisonResult,
    ProjectGroupingRequest, ProjectGroupingResponse,
    BatchEntityExtractionRequest, BatchEntityExtractionResponse
)
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/project", tags=["project"])


def get_ai_service_for_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AIService:
    """Dependency to get AI service for current user"""
    try:
        return get_ai_service()
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


# TASK-010: Entity Extraction Endpoints

@router.post("/extract/entity", response_model=EntityExtractionResult)
async def extract_entity(
    request: EntityExtractionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Extract entities from a single email (TASK-010)"""
    try:
        ai_service = get_ai_service()
        entity_service = get_entity_extraction_service(ai_service)
        
        result = entity_service.extract_from_email(request.email_data)
        
        return EntityExtractionResult(
            email_id=result.get('email_id', ''),
            project_name=result.get('project_name'),
            address=result.get('address'),
            job_numbers=result.get('job_numbers', []),
            client_info=result.get('client_info'),
            project_type=result.get('project_type'),
            key_dates=result.get('key_dates'),
            project_keywords=result.get('project_keywords', []),
            confidence=result.get('confidence', 0.0),
            reasoning=result.get('reasoning')
        )
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract entities: {str(e)}"
        )


@router.post("/extract/batch", response_model=BatchEntityExtractionResponse)
async def extract_entities_batch(
    request: BatchEntityExtractionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Extract entities from multiple emails (TASK-010)"""
    try:
        ai_service = get_ai_service()
        entity_service = get_entity_extraction_service(ai_service)
        
        results = entity_service.extract_batch(request.emails)
        
        # Convert to response format
        response_results = []
        successful = 0
        failed = 0
        
        for result in results:
            if result.get('error'):
                failed += 1
                response_results.append(EntityExtractionResult(
                    email_id=result.get('email_id', ''),
                    confidence=0.0,
                    error=result.get('error')
                ))
            else:
                successful += 1
                response_results.append(EntityExtractionResult(
                    email_id=result.get('email_id', ''),
                    project_name=result.get('project_name'),
                    address=result.get('address'),
                    job_numbers=result.get('job_numbers', []),
                    client_info=result.get('client_info'),
                    project_type=result.get('project_type'),
                    key_dates=result.get('key_dates'),
                    project_keywords=result.get('project_keywords', []),
                    confidence=result.get('confidence', 0.0),
                    reasoning=result.get('reasoning')
                ))
        
        return BatchEntityExtractionResponse(
            results=response_results,
            total_processed=len(results),
            successful=successful,
            failed=failed
        )
    except Exception as e:
        logger.error(f"Error in batch entity extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract entities: {str(e)}"
        )


# TASK-011: Similarity Analysis Endpoints

@router.post("/similarity/compare", response_model=SimilarityComparisonResult)
async def compare_emails(
    request: SimilarityComparisonRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Compare two emails to determine if they belong to the same project (TASK-011)"""
    try:
        ai_service = get_ai_service()
        similarity_service = get_similarity_service(ai_service)
        
        result = similarity_service.compare_emails(
            email1=request.email1,
            email2=request.email2,
            existing_projects=request.existing_projects
        )
        
        return SimilarityComparisonResult(**result)
    except Exception as e:
        logger.error(f"Error comparing emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare emails: {str(e)}"
        )


@router.post("/similarity/find-match")
async def find_matching_project(
    email: Dict[str, Any],
    existing_projects: List[Dict[str, Any]],
    threshold: float = 0.7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Find matching project for an email from existing projects (TASK-011)"""
    try:
        ai_service = get_ai_service()
        similarity_service = get_similarity_service(ai_service)
        
        match = similarity_service.find_matching_project(
            email=email,
            existing_projects=existing_projects,
            threshold=threshold
        )
        
        return match if match else {"match": None}
    except Exception as e:
        logger.error(f"Error finding matching project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find matching project: {str(e)}"
        )


# TASK-012: Project Grouping Endpoints

@router.post("/group", response_model=ProjectGroupingResponse)
async def group_emails(
    request: ProjectGroupingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Group emails into projects (TASK-012)"""
    try:
        ai_service = get_ai_service()
        grouping_service = get_project_grouping_service(ai_service)
        
        # Group emails
        result = grouping_service.group_emails(
            emails=request.emails,
            existing_projects=request.existing_projects
        )
        
        # Handle multi-sender grouping if requested
        if request.handle_multi_sender:
            multi_sender_groups = grouping_service.handle_multi_sender_grouping(request.emails)
            # Merge with existing groups
            result['project_groups'].extend(multi_sender_groups)
        
        # Handle edge cases if requested
        if request.handle_edge_cases:
            result['project_groups'] = grouping_service.handle_edge_cases(
                request.emails,
                result['project_groups']
            )
        
        # Convert to response format
        project_groups = []
        for group in result['project_groups']:
            project_groups.append({
                'project_id': group.get('project_id', ''),
                'project_name': group.get('project_name', ''),
                'email_ids': group.get('email_ids', []),
                'confidence': group.get('confidence', 0.0),
                'key_indicators': group.get('key_indicators', []),
                'address': group.get('address'),
                'client': group.get('client'),
                'project_type': group.get('project_type'),
                'job_numbers': group.get('job_numbers', []),
                'thread_ids': group.get('thread_ids', []),
                'senders': group.get('senders'),
                'flags': group.get('flags'),
                'needs_review': group.get('needs_review', False)
            })
        
        return ProjectGroupingResponse(
            project_groups=project_groups,
            unmatched_emails=result.get('unmatched_emails', []),
            total_emails=result.get('total_emails', 0),
            total_projects=len(project_groups)
        )
    except Exception as e:
        logger.error(f"Error grouping emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to group emails: {str(e)}"
        )


@router.post("/group/multi-sender")
async def group_multi_sender(
    emails: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Group emails from multiple senders that belong to the same project (TASK-012)"""
    try:
        ai_service = get_ai_service()
        grouping_service = get_project_grouping_service(ai_service)
        
        groups = grouping_service.handle_multi_sender_grouping(emails)
        
        return {"project_groups": groups}
    except Exception as e:
        logger.error(f"Error in multi-sender grouping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to group multi-sender emails: {str(e)}"
        )

