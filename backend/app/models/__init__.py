"""
Database Models
"""

from app.models.user import User, UserRole
from app.models.watch import GmailWatch, NotificationQueue
from app.models.ai_processing import AIProcessingQueue, BatchProcessingJob
from app.models.learning import UserCorrection, ModelFeedback, LearningPattern

__all__ = [
    "User", "UserRole", "GmailWatch", "NotificationQueue",
    "AIProcessingQueue", "BatchProcessingJob",
    "UserCorrection", "ModelFeedback", "LearningPattern"
]

