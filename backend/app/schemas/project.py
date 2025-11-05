"""
Project Grouping Schemas
Pydantic models for project grouping requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EntityExtractionRequest(BaseModel):
    """Request for entity extraction from email"""
    email_data: Dict[str, Any]


class EntityExtractionResult(BaseModel):
    """Result of entity extraction"""
    email_id: str
    project_name: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    job_numbers: List[str] = []
    client_info: Optional[Dict[str, Any]] = None
    project_type: Optional[str] = None
    key_dates: Optional[Dict[str, Any]] = None
    project_keywords: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    error: Optional[str] = None


class SimilarityComparisonRequest(BaseModel):
    """Request for email similarity comparison"""
    email1: Dict[str, Any]
    email2: Dict[str, Any]
    existing_projects: Optional[List[Dict[str, Any]]] = None


class SimilarityComparisonResult(BaseModel):
    """Result of similarity comparison"""
    same_project: bool
    confidence: float = Field(ge=0.0, le=1.0)
    matching_indicators: Dict[str, str]
    suggested_project_name: Optional[str] = None
    reasoning: str
    email1_id: str
    email2_id: str


class ProjectGroup(BaseModel):
    """A group of emails representing a project"""
    project_id: str
    project_name: str
    email_ids: List[str]
    emails: Optional[List[Dict[str, Any]]] = None
    confidence: float = Field(ge=0.0, le=1.0)
    key_indicators: List[str] = []
    address: Optional[str] = None
    client: Optional[str] = None
    project_type: Optional[str] = None
    job_numbers: List[str] = []
    thread_ids: List[str] = []
    senders: Optional[List[str]] = None
    flags: Optional[List[str]] = None
    needs_review: Optional[bool] = False


class ProjectGroupingRequest(BaseModel):
    """Request to group emails into projects"""
    emails: List[Dict[str, Any]]
    existing_projects: Optional[List[Dict[str, Any]]] = None
    handle_multi_sender: bool = True
    handle_edge_cases: bool = True


class ProjectGroupingResponse(BaseModel):
    """Response from project grouping"""
    project_groups: List[ProjectGroup]
    unmatched_emails: List[str] = []
    total_emails: int
    total_projects: int


class BatchEntityExtractionRequest(BaseModel):
    """Request for batch entity extraction"""
    emails: List[Dict[str, Any]]


class BatchEntityExtractionResponse(BaseModel):
    """Response from batch entity extraction"""
    results: List[EntityExtractionResult]
    total_processed: int
    successful: int
    failed: int

