"""
Data Export Service
TASK-039: Export user data for GDPR/APP compliance
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json
import logging
from app.models.user import User
from app.models.project import Project, EmailProjectMapping
from app.models.learning import UserCorrection, ModelFeedback
from app.models.scan_config import ScanConfiguration
from app.models.attachment import EmailAttachment
from app.models.ai_processing import AIProcessingQueue, BatchProcessingJob
from app.dal.project_dal import ProjectDAL, EmailProjectMappingDAL

logger = logging.getLogger(__name__)


class DataExportService:
    """Service for exporting user data"""
    
    def __init__(self, user: User, db: Session):
        """Initialize data export service"""
        self.user = user
        self.db = db
        self.project_dal = ProjectDAL(Project, db)
        self.mapping_dal = EmailProjectMappingDAL(EmailProjectMapping, db)
    
    def export_all_data(self) -> Dict[str, Any]:
        """
        Export all user data
        
        Returns:
            Dictionary containing all user data
        """
        export_data = {
            'export_date': datetime.utcnow().isoformat(),
            'user_id': self.user.id,
            'user_email': self.user.email,
            'user_name': self.user.name,
            'data': {
                'profile': self._export_profile(),
                'projects': self._export_projects(),
                'email_mappings': self._export_email_mappings(),
                'corrections': self._export_corrections(),
                'feedback': self._export_feedback(),
                'configurations': self._export_configurations(),
                'attachments': self._export_attachments(),
                'processing_history': self._export_processing_history(),
            }
        }
        
        return export_data
    
    def _export_profile(self) -> Dict[str, Any]:
        """Export user profile data"""
        return {
            'email': self.user.email,
            'name': self.user.name,
            'picture': self.user.picture,
            'role': self.user.role.value if self.user.role else None,
            'created_at': self.user.created_at.isoformat() if self.user.created_at else None,
            'last_login': self.user.last_login.isoformat() if self.user.last_login else None,
        }
    
    def _export_projects(self) -> List[Dict[str, Any]]:
        """Export all projects"""
        projects = self.project_dal.get_user_projects(self.user.id)
        
        return [
            {
                'project_id': p.project_id,
                'project_name': p.project_name,
                'address': p.address,
                'client_name': p.client_name,
                'client_email': p.client_email,
                'client_phone': p.client_phone,
                'project_type': p.project_type,
                'status': p.status,
                'email_count': p.email_count,
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in projects
        ]
    
    def _export_email_mappings(self) -> List[Dict[str, Any]]:
        """Export email-project mappings"""
        mappings = self.mapping_dal.get_all(user_id=self.user.id)
        
        return [
            {
                'email_id': m.email_id,
                'project_id': m.project_id,
                'thread_id': m.thread_id,
                'association_method': m.association_method,
                'confidence': m.confidence,
                'created_at': m.created_at.isoformat() if m.created_at else None,
            }
            for m in mappings
        ]
    
    def _export_corrections(self) -> List[Dict[str, Any]]:
        """Export user corrections"""
        corrections = self.db.query(UserCorrection).filter(
            UserCorrection.user_id == self.user.id
        ).all()
        
        return [
            {
                'correction_type': c.correction_type,
                'email_id': c.email_id,
                'project_id': c.project_id,
                'correction_reason': c.correction_reason,
                'created_at': c.created_at.isoformat() if c.created_at else None,
            }
            for c in corrections
        ]
    
    def _export_feedback(self) -> List[Dict[str, Any]]:
        """Export user feedback"""
        feedback = self.db.query(ModelFeedback).filter(
            ModelFeedback.user_id == self.user.id
        ).all()
        
        return [
            {
                'feedback_type': f.feedback_type,
                'rating': f.rating,
                'comment': f.comment,
                'created_at': f.created_at.isoformat() if f.created_at else None,
            }
            for f in feedback
        ]
    
    def _export_configurations(self) -> Dict[str, Any]:
        """Export scan configurations"""
        config = self.db.query(ScanConfiguration).filter(
            ScanConfiguration.user_id == self.user.id
        ).first()
        
        if not config:
            return {}
        
        return {
            'is_enabled': config.is_enabled,
            'scan_frequency': config.scan_frequency,
            'excluded_senders': config.excluded_senders,
            'excluded_domains': config.excluded_domains,
            'created_at': config.created_at.isoformat() if config.created_at else None,
        }
    
    def _export_attachments(self) -> List[Dict[str, Any]]:
        """Export attachment metadata"""
        attachments = self.db.query(EmailAttachment).filter(
            EmailAttachment.user_id == self.user.id
        ).all()
        
        return [
            {
                'email_id': a.email_id,
                'filename': a.filename,
                'mime_type': a.mime_type,
                'size': a.size,
                'project_id': a.project_id,
                'created_at': a.created_at.isoformat() if a.created_at else None,
            }
            for a in attachments
        ]
    
    def _export_processing_history(self) -> Dict[str, Any]:
        """Export processing history"""
        queue_items = self.db.query(AIProcessingQueue).filter(
            AIProcessingQueue.user_id == self.user.id
        ).limit(1000).all()
        
        batch_jobs = self.db.query(BatchProcessingJob).filter(
            BatchProcessingJob.user_id == self.user.id
        ).limit(100).all()
        
        return {
            'queue_items': [
                {
                    'task_type': q.task_type,
                    'status': q.status,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                }
                for q in queue_items
            ],
            'batch_jobs': [
                {
                    'job_type': b.job_type,
                    'status': b.status,
                    'total_items': b.total_items,
                    'processed_items': b.processed_items,
                    'created_at': b.created_at.isoformat() if b.created_at else None,
                }
                for b in batch_jobs
            ]
        }
    
    def export_to_json(self, pretty: bool = True) -> str:
        """Export data as JSON string"""
        data = self.export_all_data()
        if pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)
    
    def export_to_file(self, filepath: str) -> None:
        """Export data to JSON file"""
        json_data = self.export_to_json(pretty=True)
        with open(filepath, 'w') as f:
            f.write(json_data)
        logger.info(f"Exported user data to {filepath}")

