"""
Audit Log API Routes
TASK-041: Query and export audit logs
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.database import get_db
from app.middleware.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.audit_log import AuditLog, AuditActionType
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs (TASK-041)
    
    Users can only see their own logs. Admins can see all logs.
    """
    try:
        query = db.query(AuditLog)
        
        # Filter by user (unless admin)
        if current_user.role.value != "admin":
            query = query.filter(AuditLog.user_id == current_user.id)
        
        # Apply filters
        if action_type:
            try:
                action_enum = AuditActionType(action_type)
                query = query.filter(AuditLog.action_type == action_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid action_type: {action_type}"
                )
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action_type": log.action_type.value,
                    "action_description": log.action_description,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "status": log.status,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]
        }
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )


@router.get("/logs/{log_id}")
async def get_audit_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed audit log entry
    """
    try:
        log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found"
            )
        
        # Check access (user can only see their own logs)
        if log.user_id != current_user.id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "id": log.id,
            "user_id": log.user_id,
            "action_type": log.action_type.value,
            "action_description": log.action_description,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_metadata": log.resource_metadata,
            "changes": log.changes,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "status": log.status,
            "error_message": log.error_message,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "request_method": log.request_method,
            "request_path": log.request_path,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit log: {str(e)}"
        )


@router.get("/export")
async def export_audit_logs(
    format: str = Query(default="json"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Export audit logs (Admin only)
    """
    try:
        query = db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        logs = query.order_by(desc(AuditLog.created_at)).all()
        
        if format == "json":
            import json
            from fastapi.responses import JSONResponse
            
            return JSONResponse(
                content={
                    "export_date": datetime.utcnow().isoformat(),
                    "total_logs": len(logs),
                    "logs": [
                        {
                            "id": log.id,
                            "user_id": log.user_id,
                            "action_type": log.action_type.value,
                            "action_description": log.action_description,
                            "resource_type": log.resource_type,
                            "resource_id": log.resource_id,
                            "status": log.status,
                            "ip_address": log.ip_address,
                            "created_at": log.created_at.isoformat() if log.created_at else None,
                        }
                        for log in logs
                    ]
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'json'"
            )
    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export audit logs: {str(e)}"
        )

