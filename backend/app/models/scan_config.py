"""
Email Scanning Configuration Models
Database models for email scanning configuration and filters
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ScanConfiguration(Base):
    """Email scanning configuration per user"""
    __tablename__ = "scan_configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Scanning settings
    is_enabled = Column(Boolean, default=True, nullable=False)
    scan_frequency = Column(String, default="realtime", nullable=False)  # realtime, hourly, daily, weekly, manual
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    
    # Label/folder selection
    included_labels = Column(JSON, nullable=True)  # List of label IDs to scan
    excluded_labels = Column(JSON, nullable=True)  # List of label IDs to exclude
    label_filter_action = Column(String, default="include")  # include or exclude
    
    # Sender filters
    excluded_senders = Column(JSON, nullable=True)  # List of email addresses to exclude
    excluded_domains = Column(JSON, nullable=True)  # List of domains to exclude
    
    # Scanning options
    scan_retroactive = Column(Boolean, default=False, nullable=False)
    retroactive_date_start = Column(DateTime(timezone=True), nullable=True)
    retroactive_date_end = Column(DateTime(timezone=True), nullable=True)
    
    # Advanced options
    scan_options = Column(JSON, nullable=True)  # Additional scanning options
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="scan_configuration")

    def __repr__(self):
        return f"<ScanConfiguration user_id={self.user_id} enabled={self.is_enabled} frequency={self.scan_frequency}>"


class ScheduledScan(Base):
    """Scheduled scanning jobs"""
    __tablename__ = "scheduled_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Schedule details
    schedule_type = Column(String, nullable=False)  # daily, weekly, custom
    schedule_time = Column(String, nullable=True)  # Time of day (HH:MM format)
    schedule_day = Column(String, nullable=True)  # Day of week (for weekly)
    schedule_cron = Column(String, nullable=True)  # Cron expression for custom
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Results
    run_count = Column(Integer, default=0, nullable=False)
    last_run_result = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="scheduled_scans")

    def __repr__(self):
        return f"<ScheduledScan user_id={self.user_id} type={self.schedule_type} active={self.is_active}>"

