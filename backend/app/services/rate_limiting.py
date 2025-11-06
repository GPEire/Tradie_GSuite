"""
Rate Limiting and Quota Management Service
TASK-045: Implement rate limiting and quota management
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from app.models.user import User
from app.models.ai_processing import AIProcessingQueue

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter with sliding window"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str) -> tuple[bool, Optional[datetime]]:
        """
        Check if request is allowed
        
        Args:
            key: Unique identifier (e.g., user_id:operation_type)
            
        Returns:
            Tuple of (is_allowed, retry_after)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            # Calculate retry after
            oldest_request = min(self.requests[key])
            retry_after = oldest_request + timedelta(seconds=self.window_seconds)
            return False, retry_after
        
        # Record request
        self.requests[key].append(now)
        return True, None
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(self.requests[key]))


class QuotaManager:
    """Manage API quotas and limits"""
    
    # Gmail API quotas
    GMAIL_DAILY_QUOTA = 1000000000  # 1 billion units per day
    GMAIL_QUOTA_UNIT_COSTS = {
        'messages.list': 1,
        'messages.get': 5,
        'messages.batchGet': 5,
        'messages.send': 100,
        'messages.modify': 5,
        'labels.list': 1,
        'labels.create': 3,
        'labels.update': 3,
        'history.list': 1,
    }
    
    def __init__(self):
        """Initialize quota manager"""
        self.daily_usage: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.rate_limiters: Dict[str, RateLimiter] = {
            'gmail_read': RateLimiter(max_requests=250, window_seconds=1),  # 250 requests/second
            'gmail_write': RateLimiter(max_requests=100, window_seconds=1),  # 100 requests/second
            'ai_processing': RateLimiter(max_requests=10, window_seconds=60),  # 10 requests/minute
        }
    
    def check_rate_limit(self, user_id: int, operation_type: str) -> tuple[bool, Optional[datetime], Optional[str]]:
        """
        Check if operation is allowed
        
        Args:
            user_id: User ID
            operation_type: Type of operation (gmail_read, gmail_write, ai_processing)
            
        Returns:
            Tuple of (is_allowed, retry_after, error_message)
        """
        if operation_type not in self.rate_limiters:
            return True, None, None
        
        limiter = self.rate_limiters[operation_type]
        key = f"{user_id}:{operation_type}"
        
        is_allowed, retry_after = limiter.is_allowed(key)
        
        if not is_allowed:
            error_msg = f"Rate limit exceeded for {operation_type}. Retry after {retry_after}"
            return False, retry_after, error_msg
        
        return True, None, None
    
    def check_quota(self, user_id: int, operation: str) -> tuple[bool, Optional[str]]:
        """
        Check if operation is within quota
        
        Args:
            user_id: User ID
            operation: Gmail API operation name
            
        Returns:
            Tuple of (is_within_quota, error_message)
        """
        if operation not in self.GMAIL_QUOTA_UNIT_COSTS:
            return True, None
        
        cost = self.GMAIL_QUOTA_UNIT_COSTS[operation]
        today = datetime.utcnow().date().isoformat()
        
        # Check daily quota
        daily_usage = self.daily_usage[user_id].get(today, 0)
        if daily_usage + cost > self.GMAIL_DAILY_QUOTA:
            return False, f"Daily quota exceeded. Current usage: {daily_usage}/{self.GMAIL_DAILY_QUOTA}"
        
        # Record usage
        self.daily_usage[user_id][today] += cost
        
        return True, None
    
    def get_quota_status(self, user_id: int) -> Dict[str, Any]:
        """Get current quota status for user"""
        today = datetime.utcnow().date().isoformat()
        daily_usage = self.daily_usage[user_id].get(today, 0)
        
        status = {
            'daily_quota': self.GMAIL_DAILY_QUOTA,
            'daily_usage': daily_usage,
            'remaining': self.GMAIL_DAILY_QUOTA - daily_usage,
            'usage_percentage': (daily_usage / self.GMAIL_DAILY_QUOTA) * 100,
            'rate_limits': {}
        }
        
        # Get rate limit status
        for op_type, limiter in self.rate_limiters.items():
            key = f"{user_id}:{op_type}"
            status['rate_limits'][op_type] = {
                'remaining': limiter.get_remaining(key),
                'max_requests': limiter.max_requests,
                'window_seconds': limiter.window_seconds
            }
        
        return status
    
    def reset_daily_usage(self):
        """Reset daily usage (call at midnight)"""
        self.daily_usage.clear()
        logger.info("Daily quota usage reset")


# Global quota manager instance
_quota_manager = QuotaManager()


def get_quota_manager() -> QuotaManager:
    """Get global quota manager instance"""
    return _quota_manager


class GracefulDegradation:
    """Handle graceful degradation when limits are exceeded"""
    
    @staticmethod
    def should_degrade(user_id: int, operation_type: str) -> bool:
        """Check if we should degrade service quality"""
        quota_manager = get_quota_manager()
        quota_status = quota_manager.get_quota_status(user_id)
        
        # Degrade if usage > 80%
        if quota_status['usage_percentage'] > 80:
            return True
        
        # Degrade if rate limit remaining < 10%
        if operation_type in quota_status['rate_limits']:
            rate_limit = quota_status['rate_limits'][operation_type]
            if rate_limit['remaining'] < rate_limit['max_requests'] * 0.1:
                return True
        
        return False
    
    @staticmethod
    def get_degraded_batch_size(normal_batch_size: int) -> int:
        """Get reduced batch size for degraded mode"""
        return max(1, normal_batch_size // 2)
    
    @staticmethod
    def get_degraded_priority(normal_priority: int) -> int:
        """Get reduced priority for degraded mode"""
        return min(10, normal_priority + 2)  # Lower priority (higher number)

