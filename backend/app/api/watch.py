"""
Gmail Watch and Notifications API Routes
Gmail push notifications, polling, and webhook endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.schemas.watch import (
    WatchStartRequest, WatchStartResponse, WatchStopResponse,
    PollingRequest, PollingResponse, NotificationQueueResponse,
    WebhookNotification, HistoryResponse
)
from app.services.watch import (
    WatchService, PollingService, NotificationProcessor,
    get_watch_service, get_polling_service
)
from app.services.gmail import GmailAPIError, GmailRateLimitError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/gmail/watch", tags=["gmail-watch"])


def get_watch_service_for_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> WatchService:
    """Dependency to get watch service for current user"""
    return get_watch_service(current_user, db)


@router.post("/start", response_model=WatchStartResponse)
async def start_watch(
    request: WatchStartRequest,
    watch_service: WatchService = Depends(get_watch_service_for_user)
):
    """Start watching Gmail for changes (push notifications or polling)"""
    try:
        result = watch_service.start_watch(
            topic_name=request.topic_name,
            label_ids=request.label_ids,
            label_filter_action=request.label_filter_action
        )
        return WatchStartResponse(**result)
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


@router.post("/stop", response_model=WatchStopResponse)
async def stop_watch(
    watch_service: WatchService = Depends(get_watch_service_for_user)
):
    """Stop watching Gmail"""
    try:
        watch_service.stop_watch()
        return WatchStopResponse()
    except GmailAPIError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )


@router.post("/poll", response_model=PollingResponse)
async def poll_for_changes(
    request: PollingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Poll Gmail for new messages (fallback when push isn't available)"""
    try:
        polling_service = get_polling_service(current_user, db)
        messages = polling_service.poll_for_changes()
        
        return PollingResponse(
            new_messages=len(messages),
            messages=messages
        )
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


@router.get("/history")
async def get_history(
    start_history_id: str,
    max_results: int = 100,
    watch_service: WatchService = Depends(get_watch_service_for_user)
):
    """Get Gmail history since a history ID"""
    try:
        history_response = watch_service.get_history(start_history_id, max_results)
        return HistoryResponse(
            history=history_response.get('history', []),
            history_id=history_response.get('historyId', ''),
            next_page_token=history_response.get('nextPageToken')
        )
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


@router.post("/webhook")
async def gmail_webhook(
    request: Request,
    x_goog_channel_id: Optional[str] = Header(None),
    x_goog_channel_token: Optional[str] = Header(None),
    x_goog_message_number: Optional[str] = Header(None),
    x_goog_resource_id: Optional[str] = Header(None),
    x_goog_resource_state: Optional[str] = Header(None),
    x_goog_resource_uri: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Gmail webhook endpoint for push notifications
    
    This endpoint receives notifications from Gmail when emails change.
    Headers contain notification metadata.
    """
    try:
        # Parse notification headers
        notification_data = {
            "channel_id": x_goog_channel_id,
            "channel_token": x_goog_channel_token,
            "message_number": x_goog_message_number,
            "resource_id": x_goog_resource_id,
            "resource_state": x_goog_resource_state,
            "resource_uri": x_goog_resource_uri
        }
        
        # Get request body if present
        body = await request.json() if request.headers.get("content-type") == "application/json" else {}
        
        # Find user by channel token (in production, use secure token mapping)
        # For MVP, we'll need to store channel_id -> user_id mapping
        # For now, process based on resource_uri
        
        logger.info(f"Received Gmail webhook notification: {notification_data}")
        
        # TODO: Map channel_id to user and process notification
        # For now, return success
        return {
            "status": "received",
            "message": "Notification received and queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


@router.get("/queue", response_model=NotificationQueueResponse)
async def get_notification_queue(
    status_filter: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification queue items for current user"""
    from app.models.watch import NotificationQueue
    
    query = db.query(NotificationQueue).filter(
        NotificationQueue.user_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(NotificationQueue.status == status_filter)
    
    items = query.order_by(NotificationQueue.created_at.desc()).limit(limit).all()
    
    # Count by status
    counts = db.query(
        NotificationQueue.status,
        db.func.count(NotificationQueue.id)
    ).filter(
        NotificationQueue.user_id == current_user.id
    ).group_by(NotificationQueue.status).all()
    
    status_counts = {status: count for status, count in counts}
    
    return NotificationQueueResponse(
        total=len(items),
        pending=status_counts.get("pending", 0),
        processing=status_counts.get("processing", 0),
        completed=status_counts.get("completed", 0),
        failed=status_counts.get("failed", 0),
        items=items
    )


@router.post("/queue/process")
async def process_notification_queue(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Process pending notifications from queue"""
    try:
        processor = NotificationProcessor(db)
        results = processor.process_pending_notifications(limit=limit)
        
        return {
            "message": "Processing completed",
            **results
        }
    except Exception as e:
        logger.error(f"Error processing queue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing queue: {str(e)}"
        )

