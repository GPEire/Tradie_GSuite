"""
Data Export API Routes
TASK-039: GDPR/APP compliance endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.data_export import DataExportService
from app.services.data_deletion import DataDeletionService
from typing import Optional
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/data", tags=["data"])


@router.get("/export")
async def export_user_data(
    format: str = "json",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (TASK-039)
    
    Supports GDPR/APP data portability requirements
    """
    try:
        export_service = DataExportService(current_user, db)
        
        if format == "json":
            json_data = export_service.export_to_json(pretty=True)
            return JSONResponse(
                content=json.loads(json_data),
                headers={
                    "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.json"
                }
            )
        elif format == "file":
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                export_service.export_to_file(f.name)
                return FileResponse(
                    f.name,
                    filename=f"user_data_{current_user.id}.json",
                    media_type="application/json"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'json' or 'file'"
            )
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.delete("/delete")
async def delete_user_data(
    anonymize: bool = False,
    confirm: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete all user data (TASK-039)
    
    Supports GDPR/APP right to be forgotten
    Requires confirmation parameter
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion requires confirmation. Set confirm=true"
        )
    
    try:
        deletion_service = DataDeletionService(current_user, db)
        result = deletion_service.delete_all_user_data(anonymize=anonymize)
        
        return {
            "message": "User data deleted successfully",
            "anonymized": anonymize,
            "deletion_summary": result
        }
    except Exception as e:
        logger.error(f"Error deleting user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data: {str(e)}"
        )


@router.get("/export/preview")
async def preview_data_export(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Preview data export (summary only)
    """
    try:
        export_service = DataExportService(current_user, db)
        data = export_service.export_all_data()
        
        # Return summary
        return {
            "export_date": data['export_date'],
            "user_id": data['user_id'],
            "summary": {
                "projects_count": len(data['data']['projects']),
                "email_mappings_count": len(data['data']['email_mappings']),
                "corrections_count": len(data['data']['corrections']),
                "feedback_count": len(data['data']['feedback']),
                "attachments_count": len(data['data']['attachments']),
            }
        }
    except Exception as e:
        logger.error(f"Error previewing data export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview export: {str(e)}"
        )

