"""
AI Service Schemas
Pydantic models for AI service requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectNameExtractionRequest(BaseModel):
    """Request for project name extraction"""
    email_content: str
    email_subject: str
    sender_email: str
    existing_projects: Optional[List[str]] = None


class ProjectNameExtractionResponse(BaseModel):
    """Response from project name extraction"""
    project_name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    alternative_names: List[str] = []
    project_type: Optional[str] = None
    keywords: List[str] = []


class AddressExtractionResponse(BaseModel):
    """Response from address extraction"""
    addresses: List[Dict[str, Any]] = []
    location_keywords: List[str] = []
    site_description: Optional[str] = None


class JobNumberExtractionResponse(BaseModel):
    """Response from job number extraction"""
    job_numbers: List[Dict[str, Any]] = []
    project_codes: List[str] = []
    invoice_numbers: List[str] = []


class EntityExtractionRequest(BaseModel):
    """Request for comprehensive entity extraction"""
    email_content: str
    email_subject: str
    sender_email: str
    sender_name: Optional[str] = None


class EntityExtractionResponse(BaseModel):
    """Response from entity extraction"""
    project_name: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    job_numbers: List[str] = []
    client_info: Optional[Dict[str, Any]] = None
    project_type: Optional[str] = None
    key_dates: Optional[Dict[str, Any]] = None
    project_keywords: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class EmailSimilarityRequest(BaseModel):
    """Request for email similarity comparison"""
    email1: Dict[str, Any]
    email2: Dict[str, Any]
    existing_projects: Optional[List[Dict[str, Any]]] = None


class EmailSimilarityResponse(BaseModel):
    """Response from email similarity comparison"""
    same_project: bool
    confidence: float = Field(ge=0.0, le=1.0)
    matching_indicators: Dict[str, str]
    suggested_project_name: Optional[str] = None
    reasoning: str


class EmailGroupingRequest(BaseModel):
    """Request for batch email grouping"""
    emails: List[Dict[str, Any]]
    existing_projects: Optional[List[Dict[str, Any]]] = None


class ProjectGroup(BaseModel):
    """A group of emails representing a project"""
    project_name: str
    project_id: str
    email_ids: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    key_indicators: List[str] = []
    address: Optional[str] = None
    client: Optional[str] = None
    project_type: Optional[str] = None


class EmailGroupingResponse(BaseModel):
    """Response from batch email grouping"""
    project_groups: List[ProjectGroup] = []
    unmatched_emails: List[str] = []
    reasoning: str

