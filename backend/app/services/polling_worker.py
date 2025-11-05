"""
Polling Worker Service
Background worker for polling Gmail when push notifications aren't available
"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.watch import GmailWatch
from app.services.watch import PollingService, get_polling_service
from app.services.watch import POLLING_INTERVALS

logger = logging.getLogger(__name__)


class PollingWorker:
    """Background worker for polling Gmail"""
    
    def __init__(self, interval: str = "normal"):
        """Initialize polling worker"""
        self.interval_seconds = POLLING_INTERVALS.get(interval, POLLING_INTERVALS["normal"])
        self.running = False
    
    async def poll_user(self, user_id: int):
        """Poll Gmail for a specific user"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return
            
            # Check if user has active polling watch
            watch = db.query(GmailWatch).filter(
                GmailWatch.user_id == user_id,
                GmailWatch.is_active == True,
                GmailWatch.watch_type == "polling"
            ).first()
            
            if not watch:
                logger.info(f"No active polling watch for user {user_id}")
                return
            
            # Poll for changes
            polling_service = get_polling_service(user, db)
            messages = polling_service.poll_for_changes()
            
            if messages:
                logger.info(f"Found {len(messages)} new messages for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error polling user {user_id}: {e}")
        finally:
            db.close()
    
    async def run_polling_loop(self):
        """Run continuous polling loop"""
        self.running = True
        logger.info(f"Starting polling worker with interval {self.interval_seconds} seconds")
        
        while self.running:
            try:
                db = SessionLocal()
                # Get all users with active polling watches
                watches = db.query(GmailWatch).filter(
                    GmailWatch.is_active == True,
                    GmailWatch.watch_type == "polling"
                ).all()
                
                user_ids = list(set([watch.user_id for watch in watches]))
                
                # Poll each user
                for user_id in user_ids:
                    await self.poll_user(user_id)
                
                db.close()
                
                # Wait before next poll
                await asyncio.sleep(self.interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop(self):
        """Stop the polling worker"""
        self.running = False
        logger.info("Stopping polling worker")


# Global polling worker instance
_polling_worker: Optional[PollingWorker] = None


def start_polling_worker(interval: str = "normal"):
    """Start the polling worker"""
    global _polling_worker
    if _polling_worker is None or not _polling_worker.running:
        _polling_worker = PollingWorker(interval=interval)
        # In production, this would run in a separate process/thread
        # For now, it's a placeholder for the async implementation
        logger.info("Polling worker started (async implementation)")


def stop_polling_worker():
    """Stop the polling worker"""
    global _polling_worker
    if _polling_worker:
        _polling_worker.stop()
        _polling_worker = None

