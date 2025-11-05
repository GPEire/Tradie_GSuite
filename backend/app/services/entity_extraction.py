"""
Entity Extraction Pipeline
Extract project information from emails using AI
"""

from typing import Dict, List, Optional, Any
import logging
from app.services.ai import AIService, AIServiceError
from app.services.email_parser import parse_gmail_message

logger = logging.getLogger(__name__)


class EntityExtractionService:
    """Service for extracting entities from emails"""
    
    def __init__(self, ai_service: AIService):
        """Initialize entity extraction service"""
        self.ai_service = ai_service
    
    def extract_from_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all entities from a single email
        
        Args:
            email_data: Parsed email data (from parse_gmail_message)
        
        Returns:
            Extracted entities (project name, address, job numbers, client info, etc.)
        """
        try:
            # Prepare email content
            email_content = email_data.get('body_text', '') or email_data.get('snippet', '')
            email_subject = email_data.get('subject', '')
            from_address = email_data.get('from', {})
            sender_email = from_address.get('email', '') if isinstance(from_address, dict) else str(from_address)
            sender_name = from_address.get('name', '') if isinstance(from_address, dict) else None
            
            # Use comprehensive entity extraction
            result = self.ai_service.extract_entities(
                email_content=email_content,
                email_subject=email_subject,
                sender_email=sender_email,
                sender_name=sender_name
            )
            
            # Add email metadata to result
            result['email_id'] = email_data.get('id')
            result['thread_id'] = email_data.get('thread_id')
            result['date'] = email_data.get('date')
            result['sender_email'] = sender_email
            result['sender_name'] = sender_name
            
            return result
            
        except AIServiceError as e:
            logger.error(f"AI service error during entity extraction: {e}")
            raise
        except Exception as e:
            logger.error(f"Error extracting entities from email: {e}")
            raise
    
    def extract_project_name(self, email_data: Dict[str, Any], 
                            existing_projects: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract project name from email"""
        try:
            email_content = email_data.get('body_text', '') or email_data.get('snippet', '')
            email_subject = email_data.get('subject', '')
            from_address = email_data.get('from', {})
            sender_email = from_address.get('email', '') if isinstance(from_address, dict) else str(from_address)
            
            return self.ai_service.extract_project_name(
                email_content=email_content,
                email_subject=email_subject,
                sender_email=sender_email,
                existing_projects=existing_projects
            )
        except Exception as e:
            logger.error(f"Error extracting project name: {e}")
            raise
    
    def extract_address(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract property address from email"""
        try:
            email_content = email_data.get('body_text', '') or email_data.get('snippet', '')
            email_subject = email_data.get('subject', '')
            
            return self.ai_service.extract_address(
                email_content=email_content,
                email_subject=email_subject
            )
        except Exception as e:
            logger.error(f"Error extracting address: {e}")
            raise
    
    def extract_job_number(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job numbers and reference codes from email"""
        try:
            email_content = email_data.get('body_text', '') or email_data.get('snippet', '')
            email_subject = email_data.get('subject', '')
            
            return self.ai_service.extract_job_number(
                email_content=email_content,
                email_subject=email_subject
            )
        except Exception as e:
            logger.error(f"Error extracting job number: {e}")
            raise
    
    def extract_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract entities from multiple emails
        
        Args:
            emails: List of parsed email data
        
        Returns:
            List of extracted entities for each email
        """
        results = []
        
        for email in emails:
            try:
                extracted = self.extract_from_email(email)
                results.append(extracted)
            except Exception as e:
                logger.warning(f"Failed to extract entities from email {email.get('id')}: {e}")
                # Add error entry
                results.append({
                    'email_id': email.get('id'),
                    'error': str(e),
                    'confidence': 0.0
                })
        
        return results


def get_entity_extraction_service(ai_service: AIService) -> EntityExtractionService:
    """Factory function to create entity extraction service"""
    return EntityExtractionService(ai_service)

