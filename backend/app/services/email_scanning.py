"""
Email Scanning Service
Real-time, manual, retroactive, and scheduled email scanning
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
from app.models.user import User
from app.models.scan_config import ScanConfiguration, ScheduledScan
from app.models.watch import NotificationQueue
from app.services.gmail import GmailService, get_gmail_service
from app.services.watch import WatchService, get_watch_service, PollingService, get_polling_service
from app.services.ai_processing import get_ai_processing_service, PRIORITY_REALTIME, PRIORITY_NORMAL
from app.services.email_parser import parse_gmail_message

logger = logging.getLogger(__name__)


class EmailScanningService:
    """Service for email scanning functionality"""
    
    def __init__(self, user: User, db: Session):
        """Initialize email scanning service"""
        self.user = user
        self.db = db
        self.gmail_service = get_gmail_service(user, db)
        self.watch_service = get_watch_service(user, db)
        self.ai_processing = get_ai_processing_service(db)
    
    def scan_realtime(self) -> Dict[str, Any]:
        """
        Start real-time email scanning using Gmail watch/polling
        
        Returns:
            Watch configuration result
        """
        try:
            # Get or create scan configuration
            config = self._get_or_create_config()
            
            if not config.is_enabled:
                raise ValueError("Email scanning is disabled for this user")
            
            # Start watch (will use push if available, polling otherwise)
            watch_result = self.watch_service.start_watch(
                topic_name=None,  # Use polling mode for now
                label_ids=config.included_labels,
                label_filter_action=config.label_filter_action
            )
            
            # Update last scan time
            config.last_scan_at = datetime.utcnow()
            config.scan_frequency = "realtime"
            self.db.commit()
            
            return {
                "status": "started",
                "watch_type": watch_result.get("watch_type", "polling"),
                "history_id": watch_result.get("historyId"),
                "expiration": watch_result.get("expiration")
            }
            
        except Exception as e:
            logger.error(f"Error starting real-time scan: {e}")
            raise
    
    def scan_on_demand(self, limit: int = 100, 
                      label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Trigger on-demand manual email scan
        
        Args:
            limit: Maximum number of emails to scan
            label_ids: Optional label IDs to filter
        
        Returns:
            Scan results
        """
        try:
            config = self._get_or_create_config()
            
            # Build query
            query = self._build_scan_query(config, label_ids)
            
            # Fetch emails
            response = self.gmail_service.list_messages(
                query=query,
                max_results=limit
            )
            
            messages = response.get('messages', [])
            email_ids = [msg['id'] for msg in messages]
            
            # Queue emails for processing
            queue_items = self.ai_processing.queue_batch_processing(
                user_id=self.user.id,
                email_ids=email_ids,
                priority=PRIORITY_NORMAL
            )
            
            # Update last scan time
            config.last_scan_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "status": "queued",
                "emails_found": len(email_ids),
                "queued_items": len(queue_items),
                "email_ids": email_ids
            }
            
        except Exception as e:
            logger.error(f"Error in on-demand scan: {e}")
            raise
    
    def scan_retroactive(self, date_start: datetime, date_end: datetime,
                        limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform retroactive scan with date range
        
        Args:
            date_start: Start date for scanning
            date_end: End date for scanning
            limit: Optional limit on number of emails
        
        Returns:
            Scan results
        """
        try:
            # Build date range query
            start_str = date_start.strftime("%Y/%m/%d")
            end_str = date_end.strftime("%Y/%m/%d")
            query = f"after:{start_str} before:{end_str}"
            
            # Get scan configuration for filters
            config = self._get_or_create_config()
            query = self._apply_filters_to_query(query, config)
            
            # Fetch emails (in batches if needed)
            all_email_ids = []
            page_token = None
            max_results = limit or 1000  # Default limit
            
            while True:
                if len(all_email_ids) >= max_results:
                    break
                
                batch_size = min(100, max_results - len(all_email_ids))
                
                response = self.gmail_service.list_messages(
                    query=query,
                    max_results=batch_size,
                    page_token=page_token
                )
                
                messages = response.get('messages', [])
                if not messages:
                    break
                
                email_ids = [msg['id'] for msg in messages]
                all_email_ids.extend(email_ids)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            # Queue for batch processing
            queue_items = self.ai_processing.queue_batch_processing(
                user_id=self.user.id,
                email_ids=all_email_ids,
                priority=PRIORITY_NORMAL
            )
            
            # Update configuration
            config.scan_retroactive = True
            config.retroactive_date_start = date_start
            config.retroactive_date_end = date_end
            config.last_scan_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "status": "queued",
                "emails_found": len(all_email_ids),
                "queued_items": len(queue_items),
                "date_range": {
                    "start": date_start.isoformat(),
                    "end": date_end.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in retroactive scan: {e}")
            raise
    
    def create_scheduled_scan(self, schedule_type: str, schedule_time: Optional[str] = None,
                             schedule_day: Optional[str] = None) -> ScheduledScan:
        """
        Create a scheduled scan (daily/weekly)
        
        Args:
            schedule_type: "daily" or "weekly"
            schedule_time: Time of day (HH:MM format, e.g., "09:00")
            schedule_day: Day of week for weekly (e.g., "monday")
        """
        try:
            # Calculate next run time
            next_run = self._calculate_next_run(schedule_type, schedule_time, schedule_day)
            
            scheduled_scan = ScheduledScan(
                user_id=self.user.id,
                schedule_type=schedule_type,
                schedule_time=schedule_time,
                schedule_day=schedule_day,
                is_active=True,
                next_run_at=next_run
            )
            
            self.db.add(scheduled_scan)
            self.db.commit()
            self.db.refresh(scheduled_scan)
            
            logger.info(f"Created scheduled scan {scheduled_scan.id} for user {self.user.id}")
            
            return scheduled_scan
            
        except Exception as e:
            logger.error(f"Error creating scheduled scan: {e}")
            raise
    
    def execute_scheduled_scan(self, scheduled_scan: ScheduledScan) -> Dict[str, Any]:
        """Execute a scheduled scan"""
        try:
            # Update schedule
            scheduled_scan.last_run_at = datetime.utcnow()
            scheduled_scan.run_count += 1
            scheduled_scan.next_run_at = self._calculate_next_run(
                scheduled_scan.schedule_type,
                scheduled_scan.schedule_time,
                scheduled_scan.schedule_day
            )
            
            # Perform scan
            result = self.scan_on_demand(limit=1000)
            
            scheduled_scan.last_run_result = result
            self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing scheduled scan {scheduled_scan.id}: {e}")
            scheduled_scan.last_run_result = {"error": str(e)}
            self.db.commit()
            raise
    
    def _get_or_create_config(self) -> ScanConfiguration:
        """Get or create scan configuration for user"""
        config = self.db.query(ScanConfiguration).filter(
            ScanConfiguration.user_id == self.user.id
        ).first()
        
        if not config:
            config = ScanConfiguration(
                user_id=self.user.id,
                is_enabled=True,
                scan_frequency="realtime"
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def _build_scan_query(self, config: ScanConfiguration,
                         label_ids: Optional[List[str]] = None) -> str:
        """Build Gmail query from scan configuration"""
        query_parts = []
        
        # Use provided label_ids or config labels
        scan_labels = label_ids or config.included_labels
        
        if scan_labels:
            if config.label_filter_action == "include":
                # Include specific labels
                label_query = " OR ".join([f"label:{label}" for label in scan_labels])
                query_parts.append(f"({label_query})")
            elif config.label_filter_action == "exclude":
                # Exclude specific labels
                for label in scan_labels:
                    query_parts.append(f"-label:{label}")
        
        # Apply sender filters
        if config.excluded_senders:
            for sender in config.excluded_senders:
                query_parts.append(f"-from:{sender}")
        
        if config.excluded_domains:
            for domain in config.excluded_domains:
                query_parts.append(f"-from:*@{domain}")
        
        return " ".join(query_parts) if query_parts else ""
    
    def _apply_filters_to_query(self, base_query: str, config: ScanConfiguration) -> str:
        """Apply configuration filters to a base query"""
        query_parts = [base_query] if base_query else []
        
        # Apply label filters
        if config.included_labels:
            if config.label_filter_action == "include":
                label_query = " OR ".join([f"label:{label}" for label in config.included_labels])
                query_parts.append(f"({label_query})")
        
        # Apply sender filters
        if config.excluded_senders:
            for sender in config.excluded_senders:
                query_parts.append(f"-from:{sender}")
        
        if config.excluded_domains:
            for domain in config.excluded_domains:
                query_parts.append(f"-from:*@{domain}")
        
        return " ".join(query_parts)
    
    def _calculate_next_run(self, schedule_type: str, schedule_time: Optional[str],
                           schedule_day: Optional[str]) -> datetime:
        """Calculate next run time for scheduled scan"""
        now = datetime.utcnow()
        
        if schedule_type == "daily":
            # Next run at specified time today or tomorrow
            if schedule_time:
                hour, minute = map(int, schedule_time.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
            else:
                next_run = now + timedelta(days=1)
        
        elif schedule_type == "weekly":
            # Next run on specified day at specified time
            days_ahead = self._days_until_weekday(schedule_day or "monday")
            next_run = now + timedelta(days=days_ahead)
            if schedule_time:
                hour, minute = map(int, schedule_time.split(":"))
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        else:
            next_run = now + timedelta(days=1)
        
        return next_run
    
    def _days_until_weekday(self, weekday: str) -> int:
        """Calculate days until next occurrence of weekday"""
        weekday_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        target_day = weekday_map.get(weekday.lower(), 0)
        current_day = datetime.utcnow().weekday()
        
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        
        return days_ahead


def get_email_scanning_service(user: User, db: Session) -> EmailScanningService:
    """Factory function to create email scanning service"""
    return EmailScanningService(user, db)

