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
    LabelCreateRequest, LabelUpdateRequest, LabelResponse,
    ModifyMessageRequest, BatchModifyMessagesRequest,
    ThreadModifyRequest, GmailProfileResponse, QuotaInfoResponse
)
from app.schemas.email import (
    ParsedEmailResponse, EmailFetchRequest, EmailFetchResponse,
    EmailListResponse, EmailMetadata
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


@router.get("/labels/{label_id}", response_model=LabelResponse)
async def get_label(
    label_id: str,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Get a specific label by ID"""
    try:
        label = gmail_service.get_label(label_id)
        return LabelResponse(**label)
    except GmailRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": str(e.retry_after) if e.retry_after else "60"}
        )
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_404_NOT_FOUND if e.status_code == 404 else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.patch("/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: str,
    request: LabelUpdateRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Update an existing Gmail label"""
    try:
        label = gmail_service.update_label(
            label_id=label_id,
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


@router.delete("/labels/{label_id}")
async def delete_label(
    label_id: str,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Delete a Gmail label"""
    try:
        gmail_service.delete_label(label_id)
        return {"message": "Label deleted successfully"}
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
                detail="Cannot delete system labels (INBOX, SENT, etc.)"
            )
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/labels/find-or-create", response_model=LabelResponse)
async def find_or_create_label(
    request: LabelCreateRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Find existing label by name or create if it doesn't exist"""
    try:
        label = gmail_service.find_or_create_label(request.name)
        return LabelResponse(**label)
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


@router.post("/messages/batch-modify")
async def batch_modify_messages(
    request: BatchModifyMessagesRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Modify labels for multiple messages at once"""
    try:
        result = gmail_service.batch_modify_messages(
            message_ids=request.message_ids,
            add_label_ids=request.add_label_ids,
            remove_label_ids=request.remove_label_ids
        )
        return {"message": "Messages modified successfully", "count": len(request.message_ids)}
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


@router.post("/threads/{thread_id}/apply-label")
async def apply_label_to_thread(
    thread_id: str,
    label_id: str,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Apply a label to all messages in a thread"""
    try:
        result = gmail_service.apply_label_to_thread(thread_id, label_id)
        return {"message": "Label applied to thread successfully"}
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


@router.post("/threads/{thread_id}/remove-label")
async def remove_label_from_thread(
    thread_id: str,
    label_id: str,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Remove a label from all messages in a thread"""
    try:
        result = gmail_service.remove_label_from_thread(thread_id, label_id)
        return {"message": "Label removed from thread successfully"}
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


@router.post("/emails/fetch", response_model=EmailFetchResponse)
async def fetch_emails_parsed(
    request: EmailFetchRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Fetch and parse emails with metadata extraction"""
    try:
        result = gmail_service.fetch_messages_parsed(
            query=request.query,
            max_results=request.max_results,
            page_token=request.page_token,
            include_body=request.include_body
        )
        
        # Convert to response format
        parsed_emails = []
        for email_data in result["emails"]:
            # Build metadata
            metadata = EmailMetadata(
                id=email_data["id"],
                thread_id=email_data["thread_id"],
                label_ids=email_data["label_ids"],
                snippet=email_data["snippet"],
                subject=email_data["subject"],
                from_address=email_data["from"],
                to_addresses=email_data["to"],
                cc_addresses=email_data.get("cc", []),
                bcc_addresses=email_data.get("bcc", []),
                reply_to=email_data.get("reply_to"),
                date=email_data.get("date"),
                internal_date=email_data.get("internal_date"),
                size_estimate=email_data.get("size_estimate", 0),
                history_id=email_data.get("history_id", ""),
                in_reply_to=email_data.get("in_reply_to"),
                references=email_data.get("references")
            )
            
            parsed_email = ParsedEmailResponse(
                metadata=metadata,
                body_text=email_data.get("body_text", ""),
                body_html=email_data.get("body_html"),
                attachments=email_data.get("attachments", [])
            )
            parsed_emails.append(parsed_email)
        
        return EmailFetchResponse(
            emails=parsed_emails,
            next_page_token=result.get("next_page_token"),
            result_size_estimate=result.get("result_size_estimate", 0)
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


@router.get("/emails/{message_id}/parsed", response_model=ParsedEmailResponse)
async def get_email_parsed(
    message_id: str,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """Get a specific email with full parsing (metadata + body + attachments)"""
    try:
        email_data = gmail_service.fetch_message_parsed(message_id)
        
        # Build metadata
        metadata = EmailMetadata(
            id=email_data["id"],
            thread_id=email_data["thread_id"],
            label_ids=email_data["label_ids"],
            snippet=email_data["snippet"],
            subject=email_data["subject"],
            from_address=email_data["from"],
            to_addresses=email_data["to"],
            cc_addresses=email_data.get("cc", []),
            bcc_addresses=email_data.get("bcc", []),
            reply_to=email_data.get("reply_to"),
            date=email_data.get("date"),
            internal_date=email_data.get("internal_date"),
            size_estimate=email_data.get("size_estimate", 0),
            history_id=email_data.get("history_id", ""),
            in_reply_to=email_data.get("in_reply_to"),
            references=email_data.get("references")
        )
        
        return ParsedEmailResponse(
            metadata=metadata,
            body_text=email_data.get("body_text", ""),
            body_html=email_data.get("body_html"),
            attachments=email_data.get("attachments", [])
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
            status_code=e.status_code or status.HTTP_404_NOT_FOUND if e.status_code == 404 else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/emails/list", response_model=EmailListResponse)
async def list_emails_metadata(
    request: EmailFetchRequest,
    gmail_service: GmailService = Depends(get_gmail_service_for_user)
):
    """List emails with metadata only (no body content)"""
    try:
        result = gmail_service.fetch_messages_parsed(
            query=request.query,
            max_results=request.max_results,
            page_token=request.page_token,
            include_body=False  # Only metadata
        )
        
        # Convert to metadata-only format
        email_metadata_list = []
        for email_data in result["emails"]:
            metadata = EmailMetadata(
                id=email_data["id"],
                thread_id=email_data["thread_id"],
                label_ids=email_data["label_ids"],
                snippet=email_data["snippet"],
                subject=email_data["subject"],
                from_address=email_data["from"],
                to_addresses=email_data["to"],
                cc_addresses=email_data.get("cc", []),
                bcc_addresses=email_data.get("bcc", []),
                reply_to=email_data.get("reply_to"),
                date=email_data.get("date"),
                internal_date=email_data.get("internal_date"),
                size_estimate=email_data.get("size_estimate", 0),
                history_id=email_data.get("history_id", ""),
                in_reply_to=email_data.get("in_reply_to"),
                references=email_data.get("references")
            )
            email_metadata_list.append(metadata)
        
        return EmailListResponse(
            emails=email_metadata_list,
            next_page_token=result.get("next_page_token"),
            result_size_estimate=result.get("result_size_estimate", 0)
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

