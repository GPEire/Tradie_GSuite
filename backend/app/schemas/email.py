"""
Email Schemas
Pydantic models for parsed email data
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class EmailAddress(BaseModel):
    """Email address with optional name"""
    name: str = ""
    email: str


class EmailMetadata(BaseModel):
    """Email metadata"""
    id: str
    thread_id: str
    label_ids: List[str]
    snippet: str
    subject: str
    from_address: EmailAddress
    to_addresses: List[EmailAddress]
    cc_addresses: List[EmailAddress] = []
    bcc_addresses: List[EmailAddress] = []
    reply_to: Optional[EmailAddress] = None
    date: Optional[str] = None
    internal_date: Optional[str] = None
    size_estimate: int
    history_id: str
    in_reply_to: Optional[str] = None
    references: Optional[str] = None


class EmailAttachment(BaseModel):
    """Email attachment information"""
    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None


class ParsedEmailResponse(BaseModel):
    """Complete parsed email response"""
    metadata: EmailMetadata
    body_text: str
    body_html: Optional[str] = None
    attachments: List[EmailAttachment] = []


class EmailListResponse(BaseModel):
    """Response for email list"""
    emails: List[EmailMetadata]
    next_page_token: Optional[str] = None
    result_size_estimate: int


class EmailFetchRequest(BaseModel):
    """Request to fetch emails"""
    query: Optional[str] = ""
    max_results: int = 10
    page_token: Optional[str] = None
    include_body: bool = True


class EmailFetchResponse(BaseModel):
    """Response for email fetch"""
    emails: List[ParsedEmailResponse]
    next_page_token: Optional[str] = None
    result_size_estimate: int

