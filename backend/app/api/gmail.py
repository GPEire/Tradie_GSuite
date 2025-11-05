"""
Gmail API Routes
Gmail API integration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.schemas.gmail import (
    MessageListRequest, MessageListResponse, MessageRequest,
    LabelCreateRequest, LabelResponse, ModifyMessageRequest,
    GmailProfileResponse, QuotaInfoResponse
)
from app.services.gmail import (
    GmailService, get_gmail_service,
    GmailAPIError, GmailRateLimitError, GmailQuotaExceededError
)
from app.database import get_db

router = APIRouter(prefix="/api/v1/gmail", tags=["gmail"])


def get_gmail_service_for_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> GmailService:
    """Dependency to get Gmail service for current user"""
    try:
        return get_gmail_service(current_user, db)
    except GmailAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Cannot access Gmail: {e.message}"
        )


@router.get("/profile", response_model=GmailProfileResponse)
async def get_gmail_profile(
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Get Gmail profile information"""
    try:
        profile = gmail_service.get_profile()
        return GmailProfileResponse(**profile)
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/messages/list", response_model=MessageListResponse)
async def list_messages(
    request: MessageListRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """List Gmail messages with optional query"""
    try:
        response = gmail_service.list_messages(
            query=request.query,
            max_results=request.max_results,
            page_token=request.page_token
        )
        return MessageListResponse(
            messages=response.get('messages', []),
            next_page_token=response.get('nextPageToken'),
            result_size_estimate=response.get('resultSizeEstimate', 0)
        )
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.get("/messages/{message_id}")
async def get_message(
    message_id: str,
    format: str = "full",
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Get a specific Gmail message by ID"""
    try:
        message = gmail_service.get_message(message_id, format=format)
        return message
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_404_NOT_FOUND if e.status_code == 404 else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.get("/labels", response_model=List[LabelResponse])
async def list_labels(
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """List all Gmail labels"""
    try:
        labels = gmail_service.list_labels()
        return [LabelResponse(**label) for label in labels]
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/labels", response_model=LabelResponse)
async def create_label(
    request: LabelCreateRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Create a new Gmail label"""
    try:
        label = gmail_service.create_label(
            label_name=request.name,
            label_list_visibility=request.label_list_visibility,
            message_list_visibility=request.message_list_visibility
        )
        return LabelResponse(**label)
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailAPIError as e:
        if e.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/messages/{message_id}/modify")
async def modify_message(
    message_id: str,
    request: ModifyMessageRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Modify message labels (add or remove)"""
    try:
        result = gmail_service.modify_message(
            message_id=message_id,
            add_label_ids=request.add_label_ids,
            remove_label_ids=request.remove_label_ids
        )
        return result
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.get("/quota", response_model=QuotaInfoResponse)
async def get_quota_info(
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Get Gmail API quota and rate limit information"""
    try:
        quota_info = gmail_service.get_quota_info()
        return QuotaInfoResponse(**quota_info)
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )

