"""
Email Scanning Schemas
Pydantic models for email scanning requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScanConfigurationResponse(BaseModel):
    """Scan configuration response"""
    id: int
    user_id: int
    is_enabled: bool
    scan_frequency: str
    included_labels: Optional[List[str]] = None
    excluded_labels: Optional[List[str]] = None
    excluded_senders: Optional[List[str]] = None
    excluded_domains: Optional[List[str]] = None
    last_scan_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScanConfigurationUpdate(BaseModel):
    """Update scan configuration request"""
    is_enabled: Optional[bool] = None
    scan_frequency: Optional[str] = None
    included_labels: Optional[List[str]] = None
    excluded_labels: Optional[List[str]] = None
    excluded_senders: Optional[List[str]] = None
    excluded_domains: Optional[List[str]] = None


class ScanRequest(BaseModel):
    """Request to perform email scan"""
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    label_ids: Optional[List[str]] = None


class RetroactiveScanRequest(BaseModel):
    """Request for retroactive scan"""
    date_start: datetime
    date_end: datetime
    limit: Optional[int] = Field(default=1000, ge=1, le=10000)


class ScheduledScanRequest(BaseModel):
    """Request to create scheduled scan"""
    schedule_type: str  # daily, weekly
    schedule_time: Optional[str] = None  # HH:MM format
    schedule_day: Optional[str] = None  # For weekly


class AttachmentMetadataResponse(BaseModel):
    """Attachment metadata response"""
    attachment_id: str
    filename: str
    mime_type: Optional[str] = None
    size: int
    file_extension: Optional[str] = None
    file_type_category: Optional[str] = None
    project_indicators: Optional[Dict[str, Any]] = None


class AttachmentAssociationRequest(BaseModel):
    """Request to associate attachment with project"""
    project_id: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    method: str = "manual"  # manual, filename, email_content, ai


class DriveUploadRequest(BaseModel):
    """Request to upload attachment to Drive"""
    drive_folder_id: Optional[str] = None

