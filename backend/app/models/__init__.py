"""
Database Models
"""

from app.models.user import User, UserRole
from app.models.watch import GmailWatch, NotificationQueue
from app.models.ai_processing import AIProcessingQueue, BatchProcessingJob
from app.models.learning import UserCorrection, ModelFeedback, LearningPattern
from app.models.scan_config import ScanConfiguration, ScheduledScan
from app.models.attachment import EmailAttachment, AttachmentProjectMapping
from app.models.project import Project, EmailProjectMapping

__all__ = [
    "User", "UserRole", "GmailWatch", "NotificationQueue",
    "AIProcessingQueue", "BatchProcessingJob",
    "UserCorrection", "ModelFeedback", "LearningPattern",
    "ScanConfiguration", "ScheduledScan",
    "EmailAttachment", "AttachmentProjectMapping",
    "Project", "EmailProjectMapping"
]

