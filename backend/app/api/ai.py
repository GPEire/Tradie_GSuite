"""
AI Service API Routes
Endpoints for project detection and email grouping using AI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.ai import AIService, AIServiceError, get_ai_service
from app.schemas.ai import (
    ProjectNameExtractionRequest, ProjectNameExtractionResponse,
    EntityExtractionRequest, EntityExtractionResponse,
    EmailSimilarityRequest, EmailSimilarityResponse,
    EmailGroupingRequest, EmailGroupingResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


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


@router.post("/extract/project-name", response_model=ProjectNameExtractionResponse)
async def extract_project_name(
    request: ProjectNameExtractionRequest,
    ai_service: AIService = Depends(get_ai_service_for_user)
):
    """Extract project name from email content"""
    try:
        result = ai_service.extract_project_name(
            email_content=request.email_content,
            email_subject=request.email_subject,
            sender_email=request.sender_email,
            existing_projects=request.existing_projects
        )
        return ProjectNameExtractionResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error extracting project name: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract project name: {str(e)}"
        )


@router.post("/extract/address")
async def extract_address(
    email_content: str,
    email_subject: str,
    ai_service: AIService = Depends(get_ai_service_for_user)
):
    """Extract property address from email"""
    try:
        result = ai_service.extract_address(
            email_content=email_content,
            email_subject=email_subject
        )
        return result
    except AIServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/extract/job-number")
async def extract_job_number(
    email_content: str,
    email_subject: str,
    ai_service: AIService = Depends(get_ai_service_for_user)
):
    """Extract job numbers and reference codes from email"""
    try:
        result = ai_service.extract_job_number(
            email_content=email_content,
            email_subject=email_subject
        )
        return result
    except AIServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/extract/entities", response_model=EntityExtractionResponse)
async def extract_entities(
    request: EntityExtractionRequest,
    ai_service: AIService = Depends(get_ai_service_for_user)
):
    """Comprehensive entity extraction from email (project name, address, job numbers, client info, etc.)"""
    try:
        result = ai_service.extract_entities(
            email_content=request.email_content,
            email_subject=request.email_subject,
            sender_email=request.sender_email,
            sender_name=request.sender_name
        )
        return EntityExtractionResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract entities: {str(e)}"
        )


@router.post("/compare/emails", response_model=EmailSimilarityResponse)
async def compare_emails(
    request: EmailSimilarityRequest,
    ai_service: AIService = Depends(get_ai_service_for_user)
):
    """Compare two emails to determine if they belong to the same project"""
    try:
        result = ai_service.compare_emails(
            email1=request.email1,
            email2=request.email2,
            existing_projects=request.existing_projects
        )
        return EmailSimilarityResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error comparing emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare emails: {str(e)}"
        )


@router.post("/group/emails", response_model=EmailGroupingResponse)
async def group_emails(
    request: EmailGroupingRequest,
    ai_service: AIService = Depends(get_ai_service_for_user)
):
    """Group multiple emails into projects"""
    try:
        result = ai_service.group_emails(
            emails=request.emails,
            existing_projects=request.existing_projects
        )
        return EmailGroupingResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error grouping emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to group emails: {str(e)}"
        )

