"""
Watch and Notification Schemas
Pydantic models for Gmail watch and notifications
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class WatchStartRequest(BaseModel):
    """Request to start watching Gmail"""
    topic_name: Optional[str] = None
    label_ids: Optional[List[str]] = None
    label_filter_action: Optional[str] = "include"  # include or exclude


class WatchStartResponse(BaseModel):
    """Response from starting watch"""
    history_id: str
    expiration: str
    watch_id: int


class WatchStopResponse(BaseModel):
    """Response from stopping watch"""
    message: str = "Watch stopped successfully"


class PollingRequest(BaseModel):
    """Request to poll for changes"""
    interval: Optional[str] = "normal"  # fast, normal, slow


class PollingResponse(BaseModel):
    """Response from polling"""
    new_messages: int
    messages: List[Dict[str, Any]]


class NotificationQueueItem(BaseModel):
    """Notification queue item"""
    id: int
    user_id: int
    notification_type: str
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    status: str
    retry_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationQueueResponse(BaseModel):
    """Response for notification queue operations"""
    total: int
    pending: int
    processing: int
    completed: int
    failed: int
    items: List[NotificationQueueItem]


class WebhookNotification(BaseModel):
    """Gmail webhook notification payload"""
    message: Dict[str, Any]
    subscription: Optional[str] = None


class HistoryResponse(BaseModel):
    """Gmail history response"""
    history: List[Dict[str, Any]]
    history_id: str
    next_page_token: Optional[str] = None

