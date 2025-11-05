"""
Email Scanning API Routes
Endpoints for email scanning, configuration, and attachment handling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.email_scanning import get_email_scanning_service
from app.services.scan_config import get_scan_configuration_service
from app.services.attachment_processing import get_attachment_processing_service
from app.schemas.scanning import (
    ScanConfigurationResponse, ScanConfigurationUpdate,
    ScanRequest, RetroactiveScanRequest, ScheduledScanRequest,
    AttachmentMetadataResponse, AttachmentAssociationRequest, DriveUploadRequest
)
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scanning", tags=["scanning"])


# TASK-016: Email Scanning Endpoints

@router.post("/start")
async def start_realtime_scanning(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start real-time email scanning (TASK-016)"""
    try:
        scanning_service = get_email_scanning_service(current_user, db)
        result = scanning_service.scan_realtime()
        return result
    except Exception as e:
        logger.error(f"Error starting real-time scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start real-time scanning: {str(e)}"
        )


@router.post("/scan", response_model=Dict)
async def scan_on_demand(
    request: ScanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger on-demand manual email scan (TASK-016)"""
    try:
        scanning_service = get_email_scanning_service(current_user, db)
        result = scanning_service.scan_on_demand(
            limit=request.limit,
            label_ids=request.label_ids
        )
        return result
    except Exception as e:
        logger.error(f"Error in on-demand scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform scan: {str(e)}"
        )


@router.post("/retroactive")
async def scan_retroactive(
    request: RetroactiveScanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Perform retroactive scan with date range (TASK-016)"""
    try:
        scanning_service = get_email_scanning_service(current_user, db)
        result = scanning_service.scan_retroactive(
            date_start=request.date_start,
            date_end=request.date_end,
            limit=request.limit
        )
        return result
    except Exception as e:
        logger.error(f"Error in retroactive scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform retroactive scan: {str(e)}"
        )


@router.post("/schedule")
async def create_scheduled_scan(
    request: ScheduledScanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a scheduled scan (daily/weekly) (TASK-016)"""
    try:
        scanning_service = get_email_scanning_service(current_user, db)
        scheduled_scan = scanning_service.create_scheduled_scan(
            schedule_type=request.schedule_type,
            schedule_time=request.schedule_time,
            schedule_day=request.schedule_day
        )
        return {
            "id": scheduled_scan.id,
            "schedule_type": scheduled_scan.schedule_type,
            "next_run_at": scheduled_scan.next_run_at.isoformat() if scheduled_scan.next_run_at else None
        }
    except Exception as e:
        logger.error(f"Error creating scheduled scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scheduled scan: {str(e)}"
        )


# TASK-017: Configuration Endpoints

@router.get("/config", response_model=ScanConfigurationResponse)
async def get_scan_configuration(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get email scanning configuration (TASK-017)"""
    try:
        config_service = get_scan_configuration_service(current_user, db)
        config = config_service.get_configuration()
        return ScanConfigurationResponse(
            id=config.id,
            user_id=config.user_id,
            is_enabled=config.is_enabled,
            scan_frequency=config.scan_frequency,
            included_labels=config.included_labels,
            excluded_labels=config.excluded_labels,
            excluded_senders=config.excluded_senders,
            excluded_domains=config.excluded_domains,
            last_scan_at=config.last_scan_at
        )
    except Exception as e:
        logger.error(f"Error getting scan configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}"
        )


@router.put("/config", response_model=ScanConfigurationResponse)
async def update_scan_configuration(
    request: ScanConfigurationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update email scanning configuration (TASK-017)"""
    try:
        config_service = get_scan_configuration_service(current_user, db)
        config = config_service.update_configuration(**request.dict(exclude_unset=True))
        return ScanConfigurationResponse(
            id=config.id,
            user_id=config.user_id,
            is_enabled=config.is_enabled,
            scan_frequency=config.scan_frequency,
            included_labels=config.included_labels,
            excluded_labels=config.excluded_labels,
            excluded_senders=config.excluded_senders,
            excluded_domains=config.excluded_domains,
            last_scan_at=config.last_scan_at
        )
    except Exception as e:
        logger.error(f"Error updating scan configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.post("/config/labels")
async def set_label_filters(
    included_labels: Optional[List[str]] = None,
    excluded_labels: Optional[List[str]] = None,
    filter_action: str = "include",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set label/folder filters (TASK-017)"""
    try:
        config_service = get_scan_configuration_service(current_user, db)
        config = config_service.set_label_filters(
            included_labels=included_labels,
            excluded_labels=excluded_labels,
            filter_action=filter_action
        )
        return {"message": "Label filters updated"}
    except Exception as e:
        logger.error(f"Error setting label filters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set label filters: {str(e)}"
        )


@router.post("/config/exclude-sender")
async def add_excluded_sender(
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add sender to exclusion list (TASK-017)"""
    try:
        config_service = get_scan_configuration_service(current_user, db)
        config_service.add_excluded_sender(email)
        return {"message": f"Sender {email} added to exclusion list"}
    except Exception as e:
        logger.error(f"Error adding excluded sender: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add excluded sender: {str(e)}"
        )


@router.delete("/config/exclude-sender")
async def remove_excluded_sender(
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove sender from exclusion list (TASK-017)"""
    try:
        config_service = get_scan_configuration_service(current_user, db)
        config_service.remove_excluded_sender(email)
        return {"message": f"Sender {email} removed from exclusion list"}
    except Exception as e:
        logger.error(f"Error removing excluded sender: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove excluded sender: {str(e)}"
        )


@router.post("/config/exclude-domain")
async def add_excluded_domain(
    domain: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add domain to exclusion list (TASK-017)"""
    try:
        config_service = get_scan_configuration_service(current_user, db)
        config_service.add_excluded_domain(domain)
        return {"message": f"Domain {domain} added to exclusion list"}
    except Exception as e:
        logger.error(f"Error adding excluded domain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add excluded domain: {str(e)}"
        )


# TASK-018: Attachment Handling Endpoints

@router.get("/attachments/{email_id}", response_model=List[AttachmentMetadataResponse])
async def get_email_attachments(
    email_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Extract attachment metadata from email (TASK-018)"""
    try:
        attachment_service = get_attachment_processing_service(current_user, db)
        metadata_list = attachment_service.extract_attachment_metadata(email_id)
        
        return [
            AttachmentMetadataResponse(
                attachment_id=m.get("attachment_id", ""),
                filename=m.get("filename", ""),
                mime_type=m.get("mime_type"),
                size=m.get("size", 0),
                file_extension=m.get("file_extension"),
                file_type_category=m.get("file_type_category"),
                project_indicators=m.get("project_indicators")
            )
            for m in metadata_list
        ]
    except Exception as e:
        logger.error(f"Error extracting attachment metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract attachment metadata: {str(e)}"
        )


@router.get("/attachments/project/{project_id}")
async def get_project_attachments(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all attachments for a project (TASK-018)"""
    try:
        attachment_service = get_attachment_processing_service(current_user, db)
        attachments = attachment_service.aggregate_attachments_by_project(project_id)
        
        return [
            {
                "id": att.id,
                "email_id": att.email_id,
                "filename": att.filename,
                "size": att.size,
                "file_type_category": att.file_type_category,
                "drive_url": att.drive_url,
                "is_uploaded_to_drive": att.is_uploaded_to_drive
            }
            for att in attachments
        ]
    except Exception as e:
        logger.error(f"Error getting project attachments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project attachments: {str(e)}"
        )


@router.post("/attachments/{attachment_id}/associate")
async def associate_attachment_with_project(
    attachment_id: int,
    request: AttachmentAssociationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Associate attachment with project (TASK-018)"""
    try:
        attachment_service = get_attachment_processing_service(current_user, db)
        mapping = attachment_service.associate_attachment_with_project(
            attachment_id=attachment_id,
            project_id=request.project_id,
            confidence=request.confidence,
            method=request.method
        )
        return {"mapping_id": mapping.id, "message": "Attachment associated with project"}
    except Exception as e:
        logger.error(f"Error associating attachment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to associate attachment: {str(e)}"
        )


@router.post("/attachments/{email_id}/{attachment_id}/upload-drive")
async def upload_attachment_to_drive(
    email_id: str,
    attachment_id: str,
    request: DriveUploadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload attachment to Google Drive (TASK-018)"""
    try:
        attachment_service = get_attachment_processing_service(current_user, db)
        result = attachment_service.upload_to_drive(
            email_id=email_id,
            attachment_id=attachment_id,
            drive_folder_id=request.drive_folder_id
        )
        return result
    except Exception as e:
        logger.error(f"Error uploading to Drive: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to Drive: {str(e)}"
        )

