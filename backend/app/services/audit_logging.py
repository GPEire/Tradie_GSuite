"""
Audit Logging Service
TASK-041: Log all access and modifications
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.audit_log import AuditLog, AuditActionType
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class AuditLoggingService:
    """Service for creating audit log entries"""
    
    def __init__(self, db: Session):
        """Initialize audit logging service"""
        self.db = db
    
    def log_action(
        self,
        user: User,
        action_type: AuditActionType,
        description: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_metadata: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Create an audit log entry
        
        Args:
            user: User performing the action
            action_type: Type of action
            description: Human-readable description
            resource_type: Type of resource (email, project, etc.)
            resource_id: ID of the resource
            resource_metadata: Additional resource details
            changes: Changes made (for updates)
            old_values: Previous values
            new_values: New values
            status: Action status (success, error, partial)
            error_message: Error message if failed
            request: FastAPI request object for IP/UA
            
        Returns:
            Created AuditLog entry
        """
        # Extract request details if provided
        ip_address = None
        user_agent = None
        request_method = None
        request_path = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            request_method = request.method
            request_path = str(request.url.path)
        
        audit_log = AuditLog(
            user_id=user.id,
            action_type=action_type,
            action_description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_metadata=resource_metadata,
            changes=changes,
            old_values=old_values,
            new_values=new_values,
            status=status,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        logger.info(f"Audit log created: {action_type.value} by user {user.id}")
        
        return audit_log
    
    def log_email_action(
        self,
        user: User,
        action_type: AuditActionType,
        email_id: str,
        description: str,
        project_id: Optional[str] = None,
        status: str = "success",
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log email-related action"""
        return self.log_action(
            user=user,
            action_type=action_type,
            description=description,
            resource_type="email",
            resource_id=email_id,
            resource_metadata={"project_id": project_id} if project_id else None,
            status=status,
            request=request
        )
    
    def log_project_action(
        self,
        user: User,
        action_type: AuditActionType,
        project_id: str,
        description: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        status: str = "success",
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log project-related action"""
        return self.log_action(
            user=user,
            action_type=action_type,
            description=description,
            resource_type="project",
            resource_id=project_id,
            old_values=old_values,
            new_values=new_values,
            status=status,
            request=request
        )
    
    def log_config_action(
        self,
        user: User,
        action_type: AuditActionType,
        description: str,
        config_type: str,
        changes: Optional[Dict[str, Any]] = None,
        status: str = "success",
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log configuration-related action"""
        return self.log_action(
            user=user,
            action_type=action_type,
            description=description,
            resource_type="config",
            resource_id=config_type,
            changes=changes,
            status=status,
            request=request
        )
    
    def log_auth_action(
        self,
        user: User,
        action_type: AuditActionType,
        description: str,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log authentication-related action"""
        return self.log_action(
            user=user,
            action_type=action_type,
            description=description,
            resource_type="auth",
            status=status,
            error_message=error_message,
            request=request
        )
    
    def log_data_action(
        self,
        user: User,
        action_type: AuditActionType,
        description: str,
        export_format: Optional[str] = None,
        status: str = "success",
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log data export/deletion action"""
        return self.log_action(
            user=user,
            action_type=action_type,
            description=description,
            resource_type="data",
            resource_metadata={"export_format": export_format} if export_format else None,
            status=status,
            request=request
        )


def get_audit_logging_service(db: Session) -> AuditLoggingService:
    """Get audit logging service instance"""
    return AuditLoggingService(db)

