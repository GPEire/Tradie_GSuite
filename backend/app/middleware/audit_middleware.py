"""
Audit Middleware
TASK-041: Automatically log API requests
"""

from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.audit_logging import AuditLoggingService, get_audit_logging_service
from app.models.audit_log import AuditActionType
import logging
import time

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests and responses"""
    
    # Paths to exclude from audit logging
    EXCLUDED_PATHS = [
        "/health",
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/auth/me",  # Frequent health checks
    ]
    
    # Paths that require special handling
    SENSITIVE_PATHS = [
        "/api/v1/auth/",
        "/api/v1/data/",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log audit trail"""
        start_time = time.time()
        
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)
        
        # Get user from request state (set by auth middleware)
        user: Optional[User] = request.state.user if hasattr(request.state, 'user') else None
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log audit trail (async, don't block response)
        try:
            # Get database session
            db_gen = get_db()
            db: Session = next(db_gen)
            
            audit_service = get_audit_logging_service(db)
            
            # Determine action type based on request
            action_type = self._determine_action_type(request.method, request.url.path)
            
            if action_type and user:
                # Create audit log entry
                audit_service.log_action(
                    user=user,
                    action_type=action_type,
                    description=f"{request.method} {request.url.path}",
                    status="success" if response.status_code < 400 else "error",
                    request=request
                )
            
            db.close()
        except Exception as e:
            # Don't fail the request if audit logging fails
            logger.error(f"Failed to create audit log: {e}")
        
        return response
    
    def _determine_action_type(self, method: str, path: str) -> Optional[AuditActionType]:
        """Determine audit action type from request"""
        # Email actions
        if "/emails/" in path or "/gmail/messages" in path:
            if method == "POST":
                return AuditActionType.EMAIL_ASSIGNED
            elif method == "DELETE":
                return AuditActionType.EMAIL_REMOVED
            elif method == "GET":
                return AuditActionType.EMAIL_VIEWED
        
        # Project actions
        elif "/projects/" in path:
            if method == "POST":
                return AuditActionType.PROJECT_CREATED
            elif method == "PATCH" or method == "PUT":
                return AuditActionType.PROJECT_UPDATED
            elif method == "DELETE":
                return AuditActionType.PROJECT_DELETED
        
        # Configuration actions
        elif "/config" in path:
            if method == "PUT" or method == "PATCH":
                return AuditActionType.CONFIG_UPDATED
        
        # Scanning actions
        elif "/scanning/" in path:
            if method == "POST":
                return AuditActionType.SCAN_STARTED
        
        # Data export/deletion
        elif "/data/" in path:
            if method == "GET" and "/export" in path:
                return AuditActionType.DATA_EXPORTED
            elif method == "DELETE":
                return AuditActionType.DATA_DELETED
        
        # Authentication (handled separately in auth endpoints)
        elif "/auth/" in path:
            if "login" in path:
                return AuditActionType.USER_LOGIN
            elif "logout" in path:
                return AuditActionType.USER_LOGOUT
        
        return None

