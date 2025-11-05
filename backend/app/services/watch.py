"""
Gmail Watch Service
Gmail push notifications and polling fallback
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import json
from app.models.user import User
from app.models.watch import GmailWatch, NotificationQueue
from app.services.gmail import GmailService, GmailAPIError, handle_gmail_api_error
from app.services.auth import decrypt_token
from sqlalchemy.orm import Session
from app.config import settings

logger = logging.getLogger(__name__)

# Gmail Watch expiration (max 7 days)
MAX_WATCH_EXPIRATION_DAYS = 7
DEFAULT_WATCH_EXPIRATION_SECONDS = 7 * 24 * 60 * 60  # 7 days in seconds

# Polling intervals (fallback)
POLLING_INTERVALS = {
    "fast": 60,      # 1 minute
    "normal": 300,   # 5 minutes
    "slow": 900,     # 15 minutes
}


class WatchService:
    """Service for managing Gmail watch subscriptions"""
    
    def __init__(self, user: User, db: Session):
        """Initialize watch service for user"""
        self.user = user
        self.db = db
        self.gmail_service = GmailService(user, db)
    
    def start_watch(self, topic_name: Optional[str] = None, 
                   label_ids: Optional[List[str]] = None,
                   label_filter_action: str = "include") -> Dict[str, Any]:
        """
        Start watching Gmail for changes
        
        Args:
            topic_name: Pub/Sub topic name (for push notifications)
            label_ids: List of label IDs to watch (None = all)
            label_filter_action: "include" or "exclude" labels
        
        Returns:
            Watch response with expiration and history_id
        """
        try:
            # If no topic_name provided, use polling mode
            if not topic_name:
                # Create polling watch (no topic needed)
                watch = self.db.query(GmailWatch).filter(
                    GmailWatch.user_id == self.user.id,
                    GmailWatch.is_active == True
                ).first()
                
                profile = self.gmail_service.get_profile()
                history_id = profile.get('historyId')
                
                if watch:
                    watch.history_id = history_id
                    watch.watch_type = "polling"
                    watch.updated_at = datetime.utcnow()
                else:
                    watch = GmailWatch(
                        user_id=self.user.id,
                        history_id=history_id,
                        expiration=datetime.utcnow() + timedelta(days=365),  # Polling doesn't expire
                        label_ids=json.dumps(label_ids) if label_ids else None,
                        label_filter_action=label_filter_action,
                        is_active=True,
                        watch_type="polling"
                    )
                    self.db.add(watch)
                
                self.db.commit()
                self.db.refresh(watch)
                
                return {
                    "historyId": history_id,
                    "expiration": watch.expiration.isoformat(),
                    "watch_id": watch.id,
                    "watch_type": "polling"
                }
            
            # Push notification mode (requires topic_name)
            watch_request = {
                'topicName': topic_name,
                'labelIds': label_ids or [],
                'labelFilterAction': label_filter_action
            }
            
            request = self.gmail_service.service.users().watch(
                userId='me',
                body=watch_request
            )
            
            response = self.gmail_service._execute_with_retry(
                request, 
                operation_type="write"
            )
            
            # Get current history ID
            profile = self.gmail_service.get_profile()
            history_id = profile.get('historyId')
            
            # Create or update watch record
            watch = self.db.query(GmailWatch).filter(
                GmailWatch.user_id == self.user.id,
                GmailWatch.is_active == True
            ).first()
            
            expiration = datetime.utcnow() + timedelta(seconds=response.get('expiration', DEFAULT_WATCH_EXPIRATION_SECONDS) / 1000)
            
            if watch:
                watch.expiration = expiration
                watch.history_id = history_id
                watch.topic_name = topic_name
                watch.label_ids = json.dumps(label_ids) if label_ids else None
                watch.label_filter_action = label_filter_action
                watch.updated_at = datetime.utcnow()
            else:
                watch = GmailWatch(
                    user_id=self.user.id,
                    topic_name=topic_name,
                    history_id=history_id,
                    expiration=expiration,
                    label_ids=json.dumps(label_ids) if label_ids else None,
                    label_filter_action=label_filter_action,
                    is_active=True,
                    watch_type="push" if topic_name else "polling"
                )
                self.db.add(watch)
            
            self.db.commit()
            self.db.refresh(watch)
            
            return {
                "historyId": history_id,
                "expiration": expiration.isoformat(),
                "watch_id": watch.id
            }
            
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def stop_watch(self) -> bool:
        """Stop watching Gmail"""
        try:
            request = self.gmail_service.service.users().stop(
                userId='me'
            )
            self.gmail_service._execute_with_retry(request, operation_type="write")
            
            # Deactivate watch record
            watch = self.db.query(GmailWatch).filter(
                GmailWatch.user_id == self.user.id,
                GmailWatch.is_active == True
            ).first()
            
            if watch:
                watch.is_active = False
                self.db.commit()
            
            return True
            
        except HttpError as error:
            # If watch doesn't exist, that's okay
            if error.resp.status == 404:
                logger.info(f"No active watch found for user {self.user.id}")
                return True
            raise handle_gmail_api_error(error)
    
    def get_history(self, start_history_id: str, max_results: int = 100) -> Dict[str, Any]:
        """Get Gmail history since a history ID"""
        try:
            request = self.gmail_service.service.users().history().list(
                userId='me',
                startHistoryId=start_history_id,
                maxResults=max_results
            )
            return self.gmail_service._execute_with_retry(request, operation_type="read")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def process_history(self, history_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process history response and extract new messages"""
        messages = []
        history = history_response.get('history', [])
        
        for record in history:
            # Check for new messages
            messages_added = record.get('messagesAdded', [])
            for msg_added in messages_added:
                message = msg_added.get('message', {})
                messages.append({
                    'message_id': message.get('id'),
                    'thread_id': message.get('threadId'),
                    'label_ids': message.get('labelIds', []),
                    'history_id': record.get('id')
                })
            
            # Check for label changes
            labels_added = record.get('labelsAdded', [])
            labels_removed = record.get('labelsRemoved', [])
            
            if labels_added or labels_removed:
                # This could be relevant for project grouping updates
                pass
        
        return messages
    
    def queue_notification(self, notification_type: str, message_id: Optional[str] = None,
                          thread_id: Optional[str] = None, history_id: Optional[str] = None,
                          notification_data: Optional[Dict] = None) -> NotificationQueue:
        """Queue a notification for processing"""
        queue_item = NotificationQueue(
            user_id=self.user.id,
            notification_type=notification_type,
            message_id=message_id,
            thread_id=thread_id,
            history_id=history_id,
            notification_data=json.dumps(notification_data) if notification_data else None,
            status="pending"
        )
        self.db.add(queue_item)
        self.db.commit()
        self.db.refresh(queue_item)
        return queue_item


class PollingService:
    """Service for polling Gmail when push notifications aren't available"""
    
    def __init__(self, user: User, db: Session):
        """Initialize polling service"""
        self.user = user
        self.db = db
        self.watch_service = WatchService(user, db)
    
    def poll_for_changes(self) -> List[Dict[str, Any]]:
        """Poll Gmail for new messages"""
        try:
            # Get active watch record
            watch = self.db.query(GmailWatch).filter(
                GmailWatch.user_id == self.user.id,
                GmailWatch.is_active == True,
                GmailWatch.watch_type == "polling"
            ).first()
            
            if not watch or not watch.history_id:
                # No watch or history ID, get current state
                profile = self.watch_service.gmail_service.get_profile()
                history_id = profile.get('historyId')
                
                if not watch:
                    watch = GmailWatch(
                        user_id=self.user.id,
                        history_id=history_id,
                        is_active=True,
                        watch_type="polling",
                        expiration=datetime.utcnow() + timedelta(days=365)  # Polling doesn't expire
                    )
                    self.db.add(watch)
                else:
                    watch.history_id = history_id
                
                self.db.commit()
                return []  # First poll, no new messages yet
            
            # Get history since last check
            history_response = self.watch_service.get_history(watch.history_id)
            messages = self.watch_service.process_history(history_response)
            
            # Update history ID
            if history_response.get('historyId'):
                watch.history_id = history_response.get('historyId')
                watch.last_notification_at = datetime.utcnow()
                self.db.commit()
            
            # Queue notifications for processing
            for msg in messages:
                self.watch_service.queue_notification(
                    notification_type="email",
                    message_id=msg.get('message_id'),
                    thread_id=msg.get('thread_id'),
                    history_id=msg.get('history_id'),
                    notification_data=msg
                )
            
            return messages
            
        except Exception as e:
            logger.error(f"Error polling for changes for user {self.user.id}: {e}")
            raise


class NotificationProcessor:
    """Process notifications from queue"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_queue_item(self, queue_item: NotificationQueue) -> bool:
        """Process a single notification queue item"""
        try:
            queue_item.status = "processing"
            self.db.commit()
            
            user = queue_item.user
            gmail_service = GmailService(user, self.db)
            
            if queue_item.notification_type == "email" and queue_item.message_id:
                # Process new email
                # This will be integrated with project grouping in TASK-012
                logger.info(f"Processing email notification: {queue_item.message_id}")
                
                # For now, just mark as completed
                # In TASK-012, this will trigger AI grouping
                queue_item.status = "completed"
                queue_item.processed_at = datetime.utcnow()
                self.db.commit()
                return True
            
            queue_item.status = "completed"
            queue_item.processed_at = datetime.utcnow()
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error processing queue item {queue_item.id}: {e}")
            queue_item.status = "failed"
            queue_item.error_message = str(e)
            queue_item.retry_count += 1
            
            if queue_item.retry_count >= queue_item.max_retries:
                queue_item.status = "failed_max_retries"
            
            self.db.commit()
            return False
    
    def process_pending_notifications(self, limit: int = 100) -> Dict[str, int]:
        """Process pending notifications from queue"""
        pending = self.db.query(NotificationQueue).filter(
            NotificationQueue.status == "pending"
        ).order_by(NotificationQueue.created_at).limit(limit).all()
        
        results = {"processed": 0, "failed": 0, "total": len(pending)}
        
        for item in pending:
            if self.process_queue_item(item):
                results["processed"] += 1
            else:
                results["failed"] += 1
        
        return results


def get_watch_service(user: User, db: Session) -> WatchService:
    """Factory function to create watch service"""
    return WatchService(user, db)


def get_polling_service(user: User, db: Session) -> PollingService:
    """Factory function to create polling service"""
    return PollingService(user, db)

