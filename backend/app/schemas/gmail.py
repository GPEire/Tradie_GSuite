"""
Gmail API Schemas
Pydantic models for Gmail API requests and responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageListRequest(BaseModel):
    """Request schema for listing messages"""
    query: Optional[str] = ""
    max_results: int = 10
    page_token: Optional[str] = None


class MessageListResponse(BaseModel):
    """Response schema for message list"""
    messages: List[Dict[str, str]]
    next_page_token: Optional[str] = None
    result_size_estimate: int


class MessageRequest(BaseModel):
    """Request schema for getting a message"""
    message_id: str
    format: Optional[str] = "full"


class MessageResponse(BaseModel):
    """Response schema for message details"""
    id: str
    thread_id: str
    label_ids: List[str]
    snippet: str
    payload: Dict[str, Any]
    size_estimate: int
    history_id: str
    internal_date: Optional[str] = None


class LabelCreateRequest(BaseModel):
    """Request schema for creating a label"""
    name: str
    label_list_visibility: Optional[str] = "labelShow"
    message_list_visibility: Optional[str] = "show"


class LabelResponse(BaseModel):
    """Response schema for label"""
    id: str
    name: str
    message_list_visibility: Optional[str] = None
    label_list_visibility: Optional[str] = None
    type: Optional[str] = None


class ModifyMessageRequest(BaseModel):
    """Request schema for modifying message labels"""
    message_id: str
    add_label_ids: Optional[List[str]] = None
    remove_label_ids: Optional[List[str]] = None


class GmailProfileResponse(BaseModel):
    """Response schema for Gmail profile"""
    email_address: str
    messages_total: int
    threads_total: int
    history_id: str


class QuotaInfoResponse(BaseModel):
    """Response schema for quota information"""
    quota_limits: Dict[str, Any]
    rate_limit_status: Dict[str, Any]

