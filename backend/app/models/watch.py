"""
Watch Model
Database model for Gmail watch subscriptions
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class GmailWatch(Base):
    """Gmail watch subscription model"""
    __tablename__ = "gmail_watches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Watch details
    topic_name = Column(String, nullable=True)  # Pub/Sub topic name (if using push)
    history_id = Column(String, nullable=True)  # Last processed history ID
    expiration = Column(DateTime, nullable=False)  # Watch expiration time
    
    # Watch configuration
    label_ids = Column(Text, nullable=True)  # JSON array of label IDs to watch
    label_filter_action = Column(String, default="include")  # include or exclude
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    watch_type = Column(String, default="push")  # push or polling
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_notification_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="gmail_watches")

    def __repr__(self):
        return f"<GmailWatch user_id={self.user_id} watch_type={self.watch_type} active={self.is_active}>"


class NotificationQueue(Base):
    """Queue for processing email notifications"""
    __tablename__ = "notification_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    watch_id = Column(Integer, ForeignKey("gmail_watches.id"), nullable=True, index=True)
    
    # Notification details
    notification_type = Column(String, nullable=False)  # email, history, etc.
    history_id = Column(String, nullable=True)
    message_id = Column(String, nullable=True, index=True)
    thread_id = Column(String, nullable=True, index=True)
    
    # Processing status
    status = Column(String, default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notification data (JSON)
    notification_data = Column(Text, nullable=True)  # Store full notification payload
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="notifications")
    watch = relationship("GmailWatch", backref="notifications")

    def __repr__(self):
        return f"<NotificationQueue user_id={self.user_id} status={self.status} message_id={self.message_id}>"

