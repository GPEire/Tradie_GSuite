"""
Attachment Models
Database models for email attachments and Google Drive integration
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class EmailAttachment(Base):
    """Email attachment metadata"""
    __tablename__ = "email_attachments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Email reference
    email_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=True, index=True)
    
    # Attachment details
    attachment_id = Column(String, nullable=False)  # Gmail attachment ID
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    size = Column(BigInteger, nullable=False)  # Size in bytes
    
    # Project association
    project_id = Column(String, nullable=True, index=True)  # Associated project
    
    # File analysis
    file_extension = Column(String, nullable=True)
    file_type_category = Column(String, nullable=True)  # document, image, spreadsheet, etc.
    project_indicators = Column(JSON, nullable=True)  # Extracted project indicators from filename
    
    # Google Drive integration
    drive_file_id = Column(String, nullable=True, index=True)  # Google Drive file ID if uploaded
    drive_url = Column(String, nullable=True)
    is_uploaded_to_drive = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="attachments")

    def __repr__(self):
        return f"<EmailAttachment email_id={self.email_id} filename={self.filename} project_id={self.project_id}>"


class AttachmentProjectMapping(Base):
    """Mapping of attachments to projects"""
    __tablename__ = "attachment_project_mappings"

    id = Column(Integer, primary_key=True, index=True)
    attachment_id = Column(Integer, ForeignKey("email_attachments.id"), nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    
    # Association details
    confidence = Column(String, nullable=True)  # Confidence score for association
    association_method = Column(String, nullable=True)  # filename, email_content, manual, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    attachment = relationship("EmailAttachment", backref="project_mappings")

    def __repr__(self):
        return f"<AttachmentProjectMapping attachment_id={self.attachment_id} project_id={self.project_id}>"

