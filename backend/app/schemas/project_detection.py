"""
Project Detection Schemas
Pydantic models for project detection and management
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectResponse(BaseModel):
    """Project response model"""
    id: int
    project_id: str
    project_name: str
    project_name_aliases: Optional[List[str]] = None
    address: Optional[str] = None
    street: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    project_type: Optional[str] = None
    job_numbers: Optional[List[str]] = None
    status: str
    email_count: int
    last_email_at: Optional[datetime] = None
    confidence_score: Optional[str] = None
    needs_review: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectCreateRequest(BaseModel):
    """Request to create a project"""
    project_name: str
    address: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    project_type: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    """Request to update a project"""
    project_name: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    project_name_aliases: Optional[List[str]] = None


class EmailCategorizationRequest(BaseModel):
    """Request to categorize email"""
    email_data: Dict[str, Any]
    existing_project: Optional[Dict[str, Any]] = None


class EmailCategorizationResponse(BaseModel):
    """Email categorization response"""
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    indicators: List[str] = []
    is_new_inquiry: bool
    is_ongoing: bool
    requires_action: bool


class MultiSenderGroupingRequest(BaseModel):
    """Request for multi-sender grouping"""
    emails: List[Dict[str, Any]]


class MultiSenderGroupingResponse(BaseModel):
    """Multi-sender grouping response"""
    projects_created: int
    emails_assigned: int
    assignments: List[Dict[str, Any]]

