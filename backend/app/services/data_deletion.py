"""
Data Deletion Service
TASK-039: GDPR/APP compliant data deletion
"""

from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
from app.models.user import User
from app.models.project import Project, EmailProjectMapping
from app.models.learning import UserCorrection, ModelFeedback, LearningPattern
from app.models.scan_config import ScanConfiguration, ScheduledScan
from app.models.attachment import EmailAttachment, AttachmentProjectMapping
from app.models.ai_processing import AIProcessingQueue, BatchProcessingJob
from app.models.watch import GmailWatch, NotificationQueue

logger = logging.getLogger(__name__)


class DataDeletionService:
    """Service for GDPR/APP compliant data deletion"""
    
    def __init__(self, user: User, db: Session):
        """Initialize data deletion service"""
        self.user = user
        self.db = db
    
    def delete_all_user_data(self, anonymize: bool = False) -> Dict[str, Any]:
        """
        Delete all user data
        
        Args:
            anonymize: If True, anonymize data instead of deleting (for compliance)
            
        Returns:
            Dictionary with deletion summary
        """
        deletion_summary = {
            'user_id': self.user.id,
            'anonymize': anonymize,
            'deleted_at': None,
            'items_deleted': {}
        }
        
        try:
            # Delete in order of dependencies
            deletion_summary['items_deleted'] = {
                'email_project_mappings': self._delete_email_mappings(),
                'attachment_project_mappings': self._delete_attachment_mappings(),
                'email_attachments': self._delete_attachments(),
                'projects': self._delete_projects(),
                'ai_processing_queue': self._delete_processing_queue(),
                'batch_jobs': self._delete_batch_jobs(),
                'user_corrections': self._delete_corrections(),
                'model_feedback': self._delete_feedback(),
                'learning_patterns': self._delete_learning_patterns(),
                'scan_configurations': self._delete_scan_configurations(),
                'scheduled_scans': self._delete_scheduled_scans(),
                'gmail_watches': self._delete_gmail_watches(),
                'notification_queues': self._delete_notification_queues(),
            }
            
            if anonymize:
                self._anonymize_user()
            else:
                self._delete_user()
            
            deletion_summary['deleted_at'] = datetime.utcnow().isoformat()
            self.db.commit()
            
            logger.info(f"Deleted all data for user {self.user.id}")
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            self.db.rollback()
            raise
        
        return deletion_summary
    
    def _delete_email_mappings(self) -> int:
        """Delete email-project mappings"""
        count = self.db.query(EmailProjectMapping).filter(
            EmailProjectMapping.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_attachment_mappings(self) -> int:
        """Delete attachment-project mappings"""
        # Get attachment IDs first
        attachment_ids = [
            a.id for a in self.db.query(EmailAttachment).filter(
                EmailAttachment.user_id == self.user.id
            ).all()
        ]
        
        if not attachment_ids:
            return 0
        
        count = self.db.query(AttachmentProjectMapping).filter(
            AttachmentProjectMapping.attachment_id.in_(attachment_ids)
        ).delete(synchronize_session=False)
        return count
    
    def _delete_attachments(self) -> int:
        """Delete email attachments"""
        count = self.db.query(EmailAttachment).filter(
            EmailAttachment.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_projects(self) -> int:
        """Delete projects"""
        count = self.db.query(Project).filter(
            Project.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_processing_queue(self) -> int:
        """Delete AI processing queue items"""
        count = self.db.query(AIProcessingQueue).filter(
            AIProcessingQueue.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_batch_jobs(self) -> int:
        """Delete batch processing jobs"""
        count = self.db.query(BatchProcessingJob).filter(
            BatchProcessingJob.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_corrections(self) -> int:
        """Delete user corrections"""
        count = self.db.query(UserCorrection).filter(
            UserCorrection.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_feedback(self) -> int:
        """Delete model feedback"""
        count = self.db.query(ModelFeedback).filter(
            ModelFeedback.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_learning_patterns(self) -> int:
        """Delete learning patterns"""
        count = self.db.query(LearningPattern).filter(
            LearningPattern.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_scan_configurations(self) -> int:
        """Delete scan configurations"""
        count = self.db.query(ScanConfiguration).filter(
            ScanConfiguration.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_scheduled_scans(self) -> int:
        """Delete scheduled scans"""
        count = self.db.query(ScheduledScan).filter(
            ScheduledScan.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_gmail_watches(self) -> int:
        """Delete Gmail watches"""
        count = self.db.query(GmailWatch).filter(
            GmailWatch.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _delete_notification_queues(self) -> int:
        """Delete notification queues"""
        count = self.db.query(NotificationQueue).filter(
            NotificationQueue.user_id == self.user.id
        ).delete(synchronize_session=False)
        return count
    
    def _anonymize_user(self) -> None:
        """Anonymize user data instead of deleting"""
        self.user.email = f"deleted_{self.user.id}@deleted.local"
        self.user.name = "Deleted User"
        self.user.picture = None
        self.user.google_id = None
        self.user.access_token = None
        self.user.refresh_token = None
        self.user.is_active = False
        self.user.updated_at = datetime.utcnow()
    
    def _delete_user(self) -> None:
        """Delete user account"""
        self.db.delete(self.user)

