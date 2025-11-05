"""
AI Processing Service Architecture
Server-side processing pipeline with async queue and batch processing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.models.ai_processing import AIProcessingQueue, BatchProcessingJob
from app.models.user import User
from app.services.ai import AIService, get_ai_service
from app.services.gmail import GmailService, get_gmail_service
from app.services.entity_extraction import EntityExtractionService, get_entity_extraction_service
from app.services.project_grouping import ProjectGroupingService, get_project_grouping_service
from app.services.email_parser import parse_gmail_message

logger = logging.getLogger(__name__)

# Processing priorities
PRIORITY_REALTIME = 10
PRIORITY_HIGH = 7
PRIORITY_NORMAL = 5
PRIORITY_LOW = 3
PRIORITY_BATCH = 1


class AIProcessingService:
    """Service for managing AI processing pipeline"""
    
    def __init__(self, db: Session):
        """Initialize AI processing service"""
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def queue_email_processing(self, user_id: int, email_id: str, thread_id: Optional[str] = None,
                              priority: int = PRIORITY_NORMAL) -> AIProcessingQueue:
        """Queue an email for AI processing"""
        queue_item = AIProcessingQueue(
            user_id=user_id,
            task_type="email_grouping",
            email_id=email_id,
            thread_id=thread_id,
            status="pending",
            priority=priority
        )
        self.db.add(queue_item)
        self.db.commit()
        self.db.refresh(queue_item)
        return queue_item
    
    def queue_batch_processing(self, user_id: int, email_ids: List[str],
                              priority: int = PRIORITY_BATCH) -> List[AIProcessingQueue]:
        """Queue multiple emails for batch processing"""
        queue_items = []
        for email_id in email_ids:
            queue_item = AIProcessingQueue(
                user_id=user_id,
                task_type="email_grouping",
                email_id=email_id,
                status="pending",
                priority=priority
            )
            self.db.add(queue_item)
            queue_items.append(queue_item)
        
        self.db.commit()
        for item in queue_items:
            self.db.refresh(item)
        return queue_items
    
    def process_email_grouping(self, queue_item: AIProcessingQueue) -> bool:
        """Process email grouping for a single email"""
        try:
            queue_item.status = "processing"
            queue_item.updated_at = datetime.utcnow()
            self.db.commit()
            
            user = self.db.query(User).filter(User.id == queue_item.user_id).first()
            if not user:
                raise ValueError(f"User {queue_item.user_id} not found")
            
            # Get services
            gmail_service = get_gmail_service(user, self.db)
            ai_service = get_ai_service()
            entity_service = get_entity_extraction_service(ai_service)
            grouping_service = get_project_grouping_service(ai_service)
            
            # Fetch email
            email_data = gmail_service.fetch_message_parsed(queue_item.email_id)
            
            # Extract entities
            entities = entity_service.extract_from_email(email_data)
            
            # Get existing projects (simplified - will be enhanced in TASK-019)
            existing_projects = []  # TODO: Fetch from database in TASK-019
            
            # Group email (for now, just extract entities - full grouping in batch)
            result_data = {
                "email_id": queue_item.email_id,
                "entities": entities,
                "project_name": entities.get("project_name"),
                "confidence": entities.get("confidence", 0.0),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            queue_item.status = "completed"
            queue_item.result_data = result_data
            queue_item.processed_at = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing email grouping for queue item {queue_item.id}: {e}")
            queue_item.status = "failed"
            queue_item.error_message = str(e)
            queue_item.retry_count += 1
            
            if queue_item.retry_count >= queue_item.max_retries:
                queue_item.status = "failed_max_retries"
            
            self.db.commit()
            return False
    
    def process_pending_queue(self, limit: int = 50, priority_threshold: int = 0) -> Dict[str, int]:
        """Process pending items from queue, ordered by priority"""
        pending = self.db.query(AIProcessingQueue).filter(
            and_(
                AIProcessingQueue.status == "pending",
                AIProcessingQueue.priority >= priority_threshold
            )
        ).order_by(
            AIProcessingQueue.priority.desc(),
            AIProcessingQueue.created_at.asc()
        ).limit(limit).all()
        
        results = {"processed": 0, "failed": 0, "total": len(pending)}
        
        for item in pending:
            if item.task_type == "email_grouping":
                if self.process_email_grouping(item):
                    results["processed"] += 1
                else:
                    results["failed"] += 1
            else:
                logger.warning(f"Unknown task type: {item.task_type}")
                results["failed"] += 1
        
        return results
    
    def process_batch_grouping(self, user_id: int, email_ids: List[str],
                              existing_projects: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process batch email grouping"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Get services
            gmail_service = get_gmail_service(user, self.db)
            ai_service = get_ai_service()
            grouping_service = get_project_grouping_service(ai_service)
            
            # Fetch all emails
            emails = []
            for email_id in email_ids:
                try:
                    email_data = gmail_service.fetch_message_parsed(email_id)
                    emails.append(email_data)
                except Exception as e:
                    logger.warning(f"Failed to fetch email {email_id}: {e}")
                    continue
            
            # Group emails
            result = grouping_service.group_emails(
                emails=emails,
                existing_projects=existing_projects
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in batch grouping: {e}")
            raise


class BatchProcessingService:
    """Service for batch processing jobs (retroactive scans, etc.)"""
    
    def __init__(self, db: Session):
        """Initialize batch processing service"""
        self.db = db
        self.ai_processing = AIProcessingService(db)
    
    def create_retroactive_scan_job(self, user_id: int, date_start: datetime, 
                                   date_end: datetime, batch_size: int = 50) -> BatchProcessingJob:
        """Create a retroactive scanning job"""
        job = BatchProcessingJob(
            user_id=user_id,
            job_type="retroactive_scan",
            date_range_start=date_start,
            date_range_end=date_end,
            status="pending",
            batch_size=batch_size,
            total_items=0,
            processed_items=0,
            failed_items=0
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def execute_retroactive_scan(self, job: BatchProcessingJob) -> Dict[str, Any]:
        """Execute retroactive scan job"""
        try:
            job.status = "running"
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            user = self.db.query(User).filter(User.id == job.user_id).first()
            if not user:
                raise ValueError(f"User {job.user_id} not found")
            
            gmail_service = get_gmail_service(user, self.db)
            
            # Build query for date range
            query = ""
            if job.date_range_start and job.date_range_end:
                # Gmail query format: after:YYYY/MM/DD before:YYYY/MM/DD
                start_str = job.date_range_start.strftime("%Y/%m/%d")
                end_str = job.date_range_end.strftime("%Y/%m/%d")
                query = f"after:{start_str} before:{end_str}"
            
            # Fetch emails in batches
            all_email_ids = []
            page_token = None
            
            while True:
                response = gmail_service.list_messages(
                    query=query,
                    max_results=job.batch_size,
                    page_token=page_token
                )
                
                messages = response.get('messages', [])
                if not messages:
                    break
                
                email_ids = [msg['id'] for msg in messages]
                all_email_ids.extend(email_ids)
                
                job.total_items = len(all_email_ids)
                self.db.commit()
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            # Process emails in batches
            processed = 0
            failed = 0
            
            for i in range(0, len(all_email_ids), job.batch_size):
                batch_ids = all_email_ids[i:i + job.batch_size]
                
                # Queue batch for processing
                self.ai_processing.queue_batch_processing(
                    user_id=job.user_id,
                    email_ids=batch_ids,
                    priority=PRIORITY_BATCH
                )
                
                processed += len(batch_ids)
                job.processed_items = processed
                self.db.commit()
            
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result_summary = {
                "total_emails": len(all_email_ids),
                "processed": processed,
                "failed": failed
            }
            self.db.commit()
            
            return {
                "job_id": job.id,
                "total_emails": len(all_email_ids),
                "processed": processed,
                "failed": failed
            }
            
        except Exception as e:
            logger.error(f"Error executing retroactive scan job {job.id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    def pause_job(self, job_id: int) -> bool:
        """Pause a running batch job"""
        job = self.db.query(BatchProcessingJob).filter(BatchProcessingJob.id == job_id).first()
        if job and job.status == "running":
            job.status = "paused"
            self.db.commit()
            return True
        return False
    
    def resume_job(self, job_id: int) -> bool:
        """Resume a paused batch job"""
        job = self.db.query(BatchProcessingJob).filter(BatchProcessingJob.id == job_id).first()
        if job and job.status == "paused":
            job.status = "running"
            self.db.commit()
            return True
        return False


def get_ai_processing_service(db: Session) -> AIProcessingService:
    """Factory function to create AI processing service"""
    return AIProcessingService(db)


def get_batch_processing_service(db: Session) -> BatchProcessingService:
    """Factory function to create batch processing service"""
    return BatchProcessingService(db)

