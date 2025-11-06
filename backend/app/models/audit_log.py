"""
Audit Log Models
TASK-041: Audit logging for all email actions
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class AuditActionType(str, enum.Enum):
    """Audit action types"""
    # Email actions
    EMAIL_VIEWED = "email_viewed"
    EMAIL_ASSIGNED = "email_assigned"
    EMAIL_REMOVED = "email_removed"
    EMAIL_LABELED = "email_labeled"
    
    # Project actions
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_MERGED = "project_merged"
    PROJECT_SPLIT = "project_split"
    PROJECT_RENAMED = "project_renamed"
    
    # Configuration actions
    CONFIG_UPDATED = "config_updated"
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    
    # Data actions
    DATA_EXPORTED = "data_exported"
    DATA_DELETED = "data_deleted"
    
    # Authentication actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    TOKEN_REFRESHED = "token_refreshed"
    
    # Administrative actions
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"


class AuditLog(Base):
    """Audit log for tracking all user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(Enum(AuditActionType), nullable=False, index=True)
    action_description = Column(Text, nullable=False)
    
    # Context
    resource_type = Column(String, nullable=True)  # email, project, config, etc.
    resource_id = Column(String, nullable=True, index=True)  # ID of the resource
    resource_metadata = Column(JSON, nullable=True)  # Additional resource details
    
    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_method = Column(String, nullable=True)  # GET, POST, DELETE, etc.
    request_path = Column(String, nullable=True)
    
    # Changes
    changes = Column(JSON, nullable=True)  # Before/after values for updates
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Result
    status = Column(String, nullable=True)  # success, error, partial
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog user_id={self.user_id} action={self.action_type.value} created_at={self.created_at}>"

