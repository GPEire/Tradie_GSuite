"""
Project Models
Database models for projects and email-project associations
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    """Project/job entity"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Project identification
    project_id = Column(String, unique=True, nullable=False, index=True)  # Unique project identifier
    project_name = Column(String, nullable=False, index=True)
    project_name_aliases = Column(JSON, nullable=True)  # Alternative names for this project
    
    # Project details
    address = Column(Text, nullable=True)  # Property address
    street = Column(String, nullable=True)
    suburb = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    
    # Client information
    client_name = Column(String, nullable=True, index=True)
    client_email = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    client_company = Column(String, nullable=True)
    
    # Project metadata
    project_type = Column(String, nullable=True)  # renovation, new_build, maintenance, etc.
    job_numbers = Column(JSON, nullable=True)  # List of job numbers
    status = Column(String, default="active", nullable=False)  # active, completed, on_hold, archived
    
    # Statistics
    email_count = Column(Integer, default=0, nullable=False)
    last_email_at = Column(DateTime(timezone=True), nullable=True)
    created_from_email_id = Column(String, nullable=True)  # First email that created this project
    
    # Confidence and quality
    confidence_score = Column(String, nullable=True)  # Initial confidence when created
    needs_review = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="projects")
    email_mappings = relationship("EmailProjectMapping", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project project_id={self.project_id} name={self.project_name} user_id={self.user_id}>"


class EmailProjectMapping(Base):
    """Mapping of emails to projects"""
    __tablename__ = "email_project_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    email_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=True, index=True)
    
    # Association details
    confidence = Column(String, nullable=True)  # Confidence score for association
    association_method = Column(String, nullable=True)  # auto, manual, ai, similarity
    is_primary = Column(Boolean, default=True, nullable=False)  # True if email is primary for this project
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="email_project_mappings")
    project = relationship("Project", back_populates="email_mappings")

    def __repr__(self):
        return f"<EmailProjectMapping email_id={self.email_id} project_id={self.project_id} method={self.association_method}>"

