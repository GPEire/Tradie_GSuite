"""
Incremental Processing Service
TASK-043: Implement incremental processing for large inboxes
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging
from app.models.project import Project, EmailProjectMapping
from app.models.ai_processing import AIProcessingQueue
from app.services.email_scanning import EmailScanningService
from app.services.gmail import GmailService

logger = logging.getLogger(__name__)


class IncrementalProcessingService:
    """Service for incremental email processing"""
    
    def __init__(self, user, db: Session):
        """Initialize incremental processing service"""
        self.user = user
        self.db = db
        self.gmail_service = GmailService(user, db)
        self.scanning_service = EmailScanningService(user, db)
    
    def process_incremental(
        self,
        batch_size: int = 50,
        max_emails: Optional[int] = None,
        last_processed_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Process emails incrementally
        
        Args:
            batch_size: Number of emails to process per batch
            max_emails: Maximum total emails to process (None = all)
            last_processed_date: Only process emails after this date
            
        Returns:
            Processing summary
        """
        summary = {
            'total_processed': 0,
            'total_batches': 0,
            'projects_created': 0,
            'emails_grouped': 0,
            'errors': 0,
            'start_time': datetime.utcnow(),
            'end_time': None
        }
        
        try:
            # Get emails to process
            if last_processed_date:
                query = f'after:{int(last_processed_date.timestamp())}'
            else:
                query = ''
            
            # Fetch emails in batches
            all_message_ids = []
            page_token = None
            
            while True:
                if max_emails and len(all_message_ids) >= max_emails:
                    break
                
                # Fetch batch of message IDs
                messages_response = self.gmail_service.list_messages(
                    query=query,
                    max_results=min(batch_size, max_emails - len(all_message_ids) if max_emails else batch_size),
                    page_token=page_token
                )
                
                if not messages_response or 'messages' not in messages_response:
                    break
                
                message_ids = [msg['id'] for msg in messages_response['messages']]
                all_message_ids.extend(message_ids)
                
                # Check if more pages
                page_token = messages_response.get('nextPageToken')
                if not page_token:
                    break
            
            # Process in batches
            total_batches = (len(all_message_ids) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(all_message_ids))
                batch_ids = all_message_ids[start_idx:end_idx]
                
                logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_ids)} emails)")
                
                # Process batch
                batch_result = self._process_batch(batch_ids)
                
                summary['total_processed'] += batch_result['processed']
                summary['projects_created'] += batch_result['projects_created']
                summary['emails_grouped'] += batch_result['emails_grouped']
                summary['errors'] += batch_result['errors']
                summary['total_batches'] += 1
                
                # Check if we should continue
                if max_emails and summary['total_processed'] >= max_emails:
                    break
            
            summary['end_time'] = datetime.utcnow()
            summary['duration_seconds'] = (summary['end_time'] - summary['start_time']).total_seconds()
            
            logger.info(f"Incremental processing complete: {summary['total_processed']} emails processed")
            
        except Exception as e:
            logger.error(f"Error in incremental processing: {e}")
            summary['errors'] += 1
            summary['error_message'] = str(e)
        
        return summary
    
    def _process_batch(self, message_ids: List[str]) -> Dict[str, Any]:
        """Process a batch of email IDs"""
        result = {
            'processed': 0,
            'projects_created': 0,
            'emails_grouped': 0,
            'errors': 0
        }
        
        for message_id in message_ids:
            try:
                # Check if already processed
                existing = self.db.query(EmailProjectMapping).filter(
                    and_(
                        EmailProjectMapping.user_id == self.user.id,
                        EmailProjectMapping.email_id == message_id
                    )
                ).first()
                
                if existing:
                    continue  # Skip already processed emails
                
                # Fetch and parse email
                email_data = self.gmail_service.fetch_message_parsed(message_id)
                
                if not email_data:
                    result['errors'] += 1
                    continue
                
                # Queue for AI processing
                from app.services.ai_processing import AIProcessingService
                processing_service = AIProcessingService(self.user, self.db)
                
                queue_item = processing_service.queue_email_processing(
                    email_id=message_id,
                    priority=5  # Normal priority
                )
                
                result['processed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing email {message_id}: {e}")
                result['errors'] += 1
        
        return result
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current incremental processing status"""
        # Get last processed email timestamp
        last_mapping = self.db.query(EmailProjectMapping).filter(
            EmailProjectMapping.user_id == self.user.id
        ).order_by(EmailProjectMapping.created_at.desc()).first()
        
        # Get queue statistics
        queue_stats = self.db.query(
            func.count(AIProcessingQueue.id).label('total'),
            func.count(AIProcessingQueue.id).filter(
                AIProcessingQueue.status == 'pending'
            ).label('pending'),
            func.count(AIProcessingQueue.id).filter(
                AIProcessingQueue.status == 'processing'
            ).label('processing'),
            func.count(AIProcessingQueue.id).filter(
                AIProcessingQueue.status == 'completed'
            ).label('completed')
        ).filter(
            AIProcessingQueue.user_id == self.user.id
        ).first()
        
        return {
            'last_processed_at': last_mapping.created_at.isoformat() if last_mapping else None,
            'queue_total': queue_stats.total,
            'queue_pending': queue_stats.pending,
            'queue_processing': queue_stats.processing,
            'queue_completed': queue_stats.completed
        }


def get_incremental_processing_service(user, db: Session) -> IncrementalProcessingService:
    """Get incremental processing service instance"""
    return IncrementalProcessingService(user, db)

