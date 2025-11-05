"""
Project Detection API Routes
Endpoints for project detection, multi-sender grouping, and email categorization
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.project_detection import get_project_detection_service
from app.services.multi_sender_grouping import get_multi_sender_grouping_service
from app.services.email_categorization import get_email_categorization_service
from app.schemas.project_detection import (
    ProjectResponse, ProjectCreateRequest, ProjectUpdateRequest,
    EmailCategorizationRequest, EmailCategorizationResponse,
    MultiSenderGroupingRequest, MultiSenderGroupingResponse
)
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


# TASK-019: Project Detection Endpoints

@router.post("/detect", response_model=ProjectResponse)
async def detect_project_for_email(
    email_data: Dict[str, Any],
    auto_create: bool = True,
    confidence_threshold: float = 0.7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Detect or create project for an email (TASK-019)"""
    try:
        detection_service = get_project_detection_service(current_user, db)
        project = detection_service.detect_project_for_email(
            email_data=email_data,
            auto_create=auto_create,
            confidence_threshold=confidence_threshold
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No project found and auto_create is disabled"
            )
        
        return ProjectResponse(
            id=project.id,
            project_id=project.project_id,
            project_name=project.project_name,
            project_name_aliases=project.project_name_aliases,
            address=project.address,
            street=project.street,
            suburb=project.suburb,
            state=project.state,
            postcode=project.postcode,
            client_name=project.client_name,
            client_email=project.client_email,
            project_type=project.project_type,
            job_numbers=project.job_numbers,
            status=project.status,
            email_count=project.email_count,
            last_email_at=project.last_email_at,
            confidence_score=project.confidence_score,
            needs_review=project.needs_review,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except Exception as e:
        logger.error(f"Error detecting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect project: {str(e)}"
        )


@router.get("", response_model=List[ProjectResponse])
async def get_all_projects(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all projects for user (TASK-019)"""
    try:
        detection_service = get_project_detection_service(current_user, db)
        projects = detection_service.get_all_projects(status=status)
        
        return [
            ProjectResponse(
                id=p.id,
                project_id=p.project_id,
                project_name=p.project_name,
                project_name_aliases=p.project_name_aliases,
                address=p.address,
                street=p.street,
                suburb=p.suburb,
                state=p.state,
                postcode=p.postcode,
                client_name=p.client_name,
                client_email=p.client_email,
                project_type=p.project_type,
                job_numbers=p.job_numbers,
                status=p.status,
                email_count=p.email_count,
                last_email_at=p.last_email_at,
                confidence_score=p.confidence_score,
                needs_review=p.needs_review,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in projects
        ]
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get projects: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get project by ID (TASK-019)"""
    try:
        detection_service = get_project_detection_service(current_user, db)
        project = detection_service.get_project_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        return ProjectResponse(
            id=project.id,
            project_id=project.project_id,
            project_name=project.project_name,
            project_name_aliases=project.project_name_aliases,
            address=project.address,
            street=project.street,
            suburb=project.suburb,
            state=project.state,
            postcode=project.postcode,
            client_name=project.client_name,
            client_email=project.client_email,
            project_type=project.project_type,
            job_numbers=project.job_numbers,
            status=project.status,
            email_count=project.email_count,
            last_email_at=project.last_email_at,
            confidence_score=project.confidence_score,
            needs_review=project.needs_review,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.post("/{project_id}/aliases")
async def add_project_alias(
    project_id: str,
    alias: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add alias to project for name variations (TASK-019)"""
    try:
        detection_service = get_project_detection_service(current_user, db)
        project = detection_service.get_project_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        project = detection_service.add_project_alias(project, alias)
        return {"message": f"Alias '{alias}' added to project", "aliases": project.project_name_aliases}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding alias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add alias: {str(e)}"
        )


@router.post("/{project_id}/emails")
async def add_email_to_project(
    project_id: str,
    email_id: str,
    thread_id: Optional[str] = None,
    confidence: Optional[float] = None,
    method: str = "manual",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add email to project (TASK-019)"""
    try:
        detection_service = get_project_detection_service(current_user, db)
        project = detection_service.get_project_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        mapping = detection_service.add_email_to_project(
            email_id=email_id,
            project=project,
            thread_id=thread_id,
            confidence=confidence,
            method=method
        )
        
        return {"mapping_id": mapping.id, "message": "Email added to project"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding email to project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add email to project: {str(e)}"
        )


# TASK-020: Multi-Sender Grouping Endpoints

@router.post("/group/multi-sender", response_model=MultiSenderGroupingResponse)
async def group_multi_sender_emails(
    request: MultiSenderGroupingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Group emails from multiple senders into projects (TASK-020)"""
    try:
        grouping_service = get_multi_sender_grouping_service(current_user, db)
        result = grouping_service.group_multi_sender_emails(request.emails)
        
        return MultiSenderGroupingResponse(
            projects_created=result["projects_created"],
            emails_assigned=result["emails_assigned"],
            assignments=result["assignments"]
        )
    except Exception as e:
        logger.error(f"Error in multi-sender grouping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to group multi-sender emails: {str(e)}"
        )


# TASK-021: Email Categorization Endpoints

@router.post("/categorize", response_model=EmailCategorizationResponse)
async def categorize_email(
    request: EmailCategorizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Categorize email by type (TASK-021)"""
    try:
        categorization_service = get_email_categorization_service(current_user, db)
        result = categorization_service.categorize_email(
            email_data=request.email_data,
            existing_project=request.existing_project
        )
        
        return EmailCategorizationResponse(**result)
    except Exception as e:
        logger.error(f"Error categorizing email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to categorize email: {str(e)}"
        )


@router.post("/categorize/batch")
async def categorize_emails_batch(
    emails: List[Dict[str, Any]],
    existing_projects: Optional[Dict[str, str]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Categorize multiple emails (TASK-021)"""
    try:
        categorization_service = get_email_categorization_service(current_user, db)
        results = categorization_service.categorize_batch(
            emails=emails,
            existing_projects=existing_projects
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in batch categorization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to categorize emails: {str(e)}"
        )

