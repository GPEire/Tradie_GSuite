"""
Gmail API Service
Gmail API client with OAuth2 integration, error handling, and rate limiting
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import time
import logging
from collections import defaultdict
from app.models.user import User
from app.services.auth import decrypt_token, refresh_user_credentials
from app.services.email_parser import parse_gmail_message
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Gmail API Rate Limits (per user per second)
GMAIL_QUOTA_LIMITS = {
    "quota_per_second_per_user": 250,
    "quota_per_day": 1000000000,  # 1 billion requests per day (per project)
    "read_requests_per_second": 5,
    "write_requests_per_second": 5,
}

# Rate limiting tracking
_rate_limit_tracker = defaultdict(lambda: {"count": 0, "reset_time": time.time()})


class GmailAPIError(Exception):
    """Custom exception for Gmail API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, retry_after: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(self.message)


class GmailQuotaExceededError(GmailAPIError):
    """Raised when Gmail API quota is exceeded"""
    pass


class GmailRateLimitError(GmailAPIError):
    """Raised when rate limit is exceeded"""
    pass


def get_user_credentials(user: User, db: Optional[Session] = None) -> Optional[Credentials]:
    """Get Google OAuth2 credentials from user model"""
    from app.config import settings
    
    if not user.access_token:
        return None
    
    try:
        # Decrypt stored tokens
        access_token = decrypt_token(user.access_token)
        refresh_token = decrypt_token(user.refresh_token) if user.refresh_token else None
        
        # Create credentials object
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=settings.gmail_scopes.split(",")
        )
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Update stored tokens if database session provided
                if db:
                    from app.services.auth import encrypt_token
                    user.access_token = encrypt_token(credentials.token)
                    if credentials.refresh_token:
                        user.refresh_token = encrypt_token(credentials.refresh_token)
                    if credentials.expiry:
                        user.token_expires_at = datetime.fromtimestamp(credentials.expiry)
                    db.commit()
                logger.info(f"Refreshed token for user {user.email}")
            except RefreshError as e:
                logger.error(f"Failed to refresh token for user {user.email}: {e}")
                return None
        
        return credentials
        
    except Exception as e:
        logger.error(f"Error getting credentials for user {user.email}: {e}")
        return None


def check_rate_limit(user_id: int, operation_type: str = "read") -> bool:
    """Check if rate limit is exceeded for user"""
    current_time = time.time()
    key = f"{user_id}_{operation_type}"
    
    # Reset counter if 1 second has passed
    if current_time >= _rate_limit_tracker[key]["reset_time"]:
        _rate_limit_tracker[key] = {"count": 0, "reset_time": current_time + 1}
    
    # Check limit based on operation type
    limit = GMAIL_QUOTA_LIMITS.get(f"{operation_type}_requests_per_second", 5)
    
    if _rate_limit_tracker[key]["count"] >= limit:
        return False
    
    _rate_limit_tracker[key]["count"] += 1
    return True


def handle_gmail_api_error(error: HttpError) -> GmailAPIError:
    """Convert Gmail API HttpError to custom exception"""
    status_code = error.resp.status if hasattr(error, 'resp') else None
    
    # Rate limit errors
    if status_code == 429:
        retry_after = None
        if hasattr(error, 'resp') and 'Retry-After' in error.resp.headers:
            retry_after = int(error.resp.headers['Retry-After'])
        return GmailRateLimitError(
            f"Rate limit exceeded: {error.error_details if hasattr(error, 'error_details') else str(error)}",
            status_code=status_code,
            retry_after=retry_after
        )
    
    # Quota exceeded
    if status_code == 403 and "quota" in str(error).lower():
        return GmailQuotaExceededError(
            f"Gmail API quota exceeded: {error.error_details if hasattr(error, 'error_details') else str(error)}",
            status_code=status_code
        )
    
    # Other errors
    return GmailAPIError(
        f"Gmail API error: {error.error_details if hasattr(error, 'error_details') else str(error)}",
        status_code=status_code
    )


class GmailService:
    """Gmail API service with rate limiting and error handling"""
    
    def __init__(self, user: User, db: Optional[Session] = None):
        """Initialize Gmail service for user"""
        self.user = user
        self.db = db
        self.credentials = get_user_credentials(user, db)
        if not self.credentials:
            raise GmailAPIError("User credentials not available or expired")
        
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def _execute_with_retry(self, request, max_retries: int = 3, operation_type: str = "read"):
        """Execute Gmail API request with retry logic and rate limiting"""
        # Check rate limit
        if not check_rate_limit(self.user.id, operation_type):
            raise GmailRateLimitError(
                "Rate limit exceeded. Please wait before making another request.",
                retry_after=1
            )
        
        for attempt in range(max_retries):
            try:
                return request.execute()
            except HttpError as error:
                error_obj = handle_gmail_api_error(error)
                
                # Retry on rate limit or server errors
                if isinstance(error_obj, GmailRateLimitError) and attempt < max_retries - 1:
                    retry_after = error_obj.retry_after or (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying after {retry_after} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_after)
                    continue
                
                # Don't retry on quota exceeded or auth errors
                if isinstance(error_obj, GmailQuotaExceededError) or error_obj.status_code in [401, 403]:
                    raise error_obj
                
                # Retry on server errors (5xx)
                if error_obj.status_code and 500 <= error_obj.status_code < 600 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error, retrying after {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                # Raise error if max retries reached or non-retryable error
                raise error_obj
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Unexpected error, retrying (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(2 ** attempt)
                    continue
                raise GmailAPIError(f"Unexpected error: {str(e)}")
        
        raise GmailAPIError("Max retries exceeded")
    
    def get_profile(self) -> Dict[str, Any]:
        """Get Gmail profile information"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def list_messages(self, query: str = "", max_results: int = 10, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List Gmail messages with optional query filter"""
        try:
            request = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                pageToken=page_token
            )
            return self._execute_with_retry(request, operation_type="read")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def get_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        """Get a specific message by ID"""
        try:
            request = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            )
            return self._execute_with_retry(request, operation_type="read")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def list_labels(self) -> List[Dict[str, Any]]:
        """List all Gmail labels"""
        try:
            request = self.service.users().labels().list(userId='me')
            response = self._execute_with_retry(request, operation_type="read")
            return response.get('labels', [])
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def create_label(self, label_name: str, label_list_visibility: str = "labelShow", 
                     message_list_visibility: str = "show") -> Dict[str, Any]:
        """Create a new Gmail label"""
        try:
            label_object = {
                'name': label_name,
                'labelListVisibility': label_list_visibility,
                'messageListVisibility': message_list_visibility
            }
            request = self.service.users().labels().create(
                userId='me',
                body=label_object
            )
            return self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def get_label(self, label_id: str) -> Dict[str, Any]:
        """Get a specific label by ID"""
        try:
            request = self.service.users().labels().get(
                userId='me',
                id=label_id
            )
            return self._execute_with_retry(request, operation_type="read")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def update_label(self, label_id: str, label_name: Optional[str] = None,
                     label_list_visibility: Optional[str] = None,
                     message_list_visibility: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing Gmail label"""
        try:
            label_object = {}
            if label_name is not None:
                label_object['name'] = label_name
            if label_list_visibility is not None:
                label_object['labelListVisibility'] = label_list_visibility
            if message_list_visibility is not None:
                label_object['messageListVisibility'] = message_list_visibility
            
            request = self.service.users().labels().patch(
                userId='me',
                id=label_id,
                body=label_object
            )
            return self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def delete_label(self, label_id: str) -> None:
        """Delete a Gmail label"""
        try:
            request = self.service.users().labels().delete(
                userId='me',
                id=label_id
            )
            self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def modify_message(self, message_id: str, add_label_ids: Optional[List[str]] = None,
                       remove_label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Modify message labels (add or remove)"""
        try:
            modify_request = {}
            if add_label_ids:
                modify_request['addLabelIds'] = add_label_ids
            if remove_label_ids:
                modify_request['removeLabelIds'] = remove_label_ids
            
            if not modify_request:
                raise GmailAPIError("At least one of add_label_ids or remove_label_ids must be provided")
            
            request = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=modify_request
            )
            return self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def batch_modify_messages(self, message_ids: List[str], 
                             add_label_ids: Optional[List[str]] = None,
                             remove_label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Modify labels for multiple messages at once"""
        try:
            modify_request = {
                'ids': message_ids
            }
            if add_label_ids:
                modify_request['addLabelIds'] = add_label_ids
            if remove_label_ids:
                modify_request['removeLabelIds'] = remove_label_ids
            
            if not add_label_ids and not remove_label_ids:
                raise GmailAPIError("At least one of add_label_ids or remove_label_ids must be provided")
            
            request = self.service.users().messages().batchModify(
                userId='me',
                body=modify_request
            )
            return self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def apply_label_to_thread(self, thread_id: str, label_id: str) -> Dict[str, Any]:
        """Apply a label to all messages in a thread"""
        try:
            request = self.service.users().threads().modify(
                userId='me',
                id=thread_id,
                body={'addLabelIds': [label_id]}
            )
            return self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def remove_label_from_thread(self, thread_id: str, label_id: str) -> Dict[str, Any]:
        """Remove a label from all messages in a thread"""
        try:
            request = self.service.users().threads().modify(
                userId='me',
                id=thread_id,
                body={'removeLabelIds': [label_id]}
            )
            return self._execute_with_retry(request, operation_type="write")
        except HttpError as error:
            raise handle_gmail_api_error(error)
    
    def find_or_create_label(self, label_name: str) -> Dict[str, Any]:
        """Find existing label by name or create if it doesn't exist"""
        try:
            # List all labels
            labels = self.list_labels()
            
            # Search for existing label
            for label in labels:
                if label.get('name') == label_name:
                    return label
            
            # Label doesn't exist, create it
            return self.create_label(label_name)
        except Exception as e:
            logger.error(f"Error finding or creating label '{label_name}': {e}")
            raise GmailAPIError(f"Failed to find or create label: {str(e)}")
    
    def get_quota_info(self) -> Dict[str, Any]:
        """Get current quota usage information (if available)"""
        # Gmail API doesn't directly expose quota info, but we can track our own usage
        return {
            "quota_limits": GMAIL_QUOTA_LIMITS,
            "rate_limit_status": dict(_rate_limit_tracker)
        }
    
    def fetch_message_parsed(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        """Get a message and parse it into structured format"""
        message = self.get_message(message_id, format=format)
        return parse_gmail_message(message)
    
    def fetch_messages_parsed(self, query: str = "", max_results: int = 10, 
                             page_token: Optional[str] = None, include_body: bool = True) -> Dict[str, Any]:
        """List messages and parse them into structured format"""
        # First, get message list
        response = self.list_messages(query=query, max_results=max_results, page_token=page_token)
        
        messages = response.get('messages', [])
        parsed_emails = []
        
        # Fetch and parse each message
        for msg in messages:
            try:
                if include_body:
                    parsed = self.fetch_message_parsed(msg['id'])
                else:
                    # Get just metadata
                    message = self.get_message(msg['id'], format="metadata")
                    parsed = parse_gmail_message(message)
                parsed_emails.append(parsed)
            except Exception as e:
                logger.warning(f"Failed to parse message {msg.get('id')}: {e}")
                continue
        
        return {
            "emails": parsed_emails,
            "next_page_token": response.get('nextPageToken'),
            "result_size_estimate": response.get('resultSizeEstimate', 0)
        }


def get_gmail_service(user: User, db: Optional[Session] = None) -> GmailService:
    """Factory function to create Gmail service for user"""
    return GmailService(user, db)

