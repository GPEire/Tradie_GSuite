"""
AI Processing Models
Database models for AI processing queue and batch jobs
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AIProcessingQueue(Base):
    """Queue for AI processing tasks"""
    __tablename__ = "ai_processing_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Task details
    task_type = Column(String, nullable=False, index=True)  # email_grouping, entity_extraction, batch_scan
    email_id = Column(String, nullable=True, index=True)
    thread_id = Column(String, nullable=True, index=True)
    
    # Processing status
    status = Column(String, default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    priority = Column(Integer, default=5, nullable=False)  # 1-10, higher = more priority
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Results
    result_data = Column(JSON, nullable=True)  # Store processing results
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Task metadata
    task_metadata = Column(JSON, nullable=True)  # Additional task parameters
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # For scheduled processing

    # Relationships
    user = relationship("User", backref="ai_processing_tasks")

    def __repr__(self):
        return f"<AIProcessingQueue user_id={self.user_id} task_type={self.task_type} status={self.status}>"


class BatchProcessingJob(Base):
    """Batch processing job for retroactive scans"""
    __tablename__ = "batch_processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    job_type = Column(String, nullable=False)  # retroactive_scan, full_scan, label_application
    date_range_start = Column(DateTime(timezone=True), nullable=True)
    date_range_end = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    status = Column(String, default="pending", nullable=False, index=True)  # pending, running, paused, completed, failed
    total_items = Column(Integer, default=0, nullable=False)
    processed_items = Column(Integer, default=0, nullable=False)
    failed_items = Column(Integer, default=0, nullable=False)
    
    # Configuration
    batch_size = Column(Integer, default=50, nullable=False)
    processing_config = Column(JSON, nullable=True)  # Job-specific configuration
    
    # Results
    result_summary = Column(JSON, nullable=True)  # Summary of processing results
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="batch_jobs")

    def __repr__(self):
        return f"<BatchProcessingJob user_id={self.user_id} job_type={self.job_type} status={self.status}>"

