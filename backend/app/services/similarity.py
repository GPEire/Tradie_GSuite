"""
Content Similarity Analysis Service
Compare emails to determine if they belong to the same project
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from app.services.ai import AIService, AIServiceError

logger = logging.getLogger(__name__)


class SimilarityService:
    """Service for analyzing email similarity and project matching"""
    
    def __init__(self, ai_service: AIService):
        """Initialize similarity service"""
        self.ai_service = ai_service
    
    def compare_emails(self, email1: Dict[str, Any], email2: Dict[str, Any],
                      existing_projects: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Compare two emails to determine if they belong to the same project
        
        Args:
            email1: First email data
            email2: Second email data
            existing_projects: Optional list of existing projects for context
        
        Returns:
            Similarity analysis with same_project boolean and confidence score
        """
        try:
            # Prepare email data for AI comparison
            email1_data = {
                'subject': email1.get('subject', ''),
                'from': email1.get('from', {}).get('email', '') if isinstance(email1.get('from'), dict) else str(email1.get('from', '')),
                'body_text': email1.get('body_text', '') or email1.get('snippet', ''),
                'id': email1.get('id', '')
            }
            
            email2_data = {
                'subject': email2.get('subject', ''),
                'from': email2.get('from', {}).get('email', '') if isinstance(email2.get('from'), dict) else str(email2.get('from', '')),
                'body_text': email2.get('body_text', '') or email2.get('snippet', ''),
                'id': email2.get('id', '')
            }
            
            # Use AI service to compare
            result = self.ai_service.compare_emails(
                email1=email1_data,
                email2=email2_data,
                existing_projects=existing_projects
            )
            
            # Add email IDs for reference
            result['email1_id'] = email1.get('id')
            result['email2_id'] = email2.get('id')
            
            return result
            
        except AIServiceError as e:
            logger.error(f"AI service error during similarity comparison: {e}")
            raise
        except Exception as e:
            logger.error(f"Error comparing emails: {e}")
            raise
    
    def find_matching_project(self, email: Dict[str, Any], 
                             existing_projects: List[Dict[str, Any]],
                             threshold: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Find matching project for an email from existing projects
        
        Args:
            email: Email data to match
            existing_projects: List of existing projects with sample emails
            threshold: Minimum confidence score to consider a match
        
        Returns:
            Matching project or None if no match found
        """
        best_match = None
        best_confidence = 0.0
        
        for project in existing_projects:
            # Get sample emails from project
            sample_emails = project.get('sample_emails', [])
            if not sample_emails:
                continue
            
            # Compare with first sample email (representative)
            try:
                comparison = self.compare_emails(email, sample_emails[0], existing_projects)
                
                if comparison.get('same_project', False):
                    confidence = comparison.get('confidence', 0.0)
                    if confidence > best_confidence and confidence >= threshold:
                        best_confidence = confidence
                        best_match = {
                            'project': project,
                            'confidence': confidence,
                            'matching_indicators': comparison.get('matching_indicators', {})
                        }
            except Exception as e:
                logger.warning(f"Error comparing email with project {project.get('id')}: {e}")
                continue
        
        return best_match
    
    def calculate_similarity_score(self, email1: Dict[str, Any], 
                                  email2: Dict[str, Any]) -> float:
        """
        Calculate similarity score between two emails (0.0-1.0)
        
        Returns:
            Similarity score
        """
        try:
            result = self.compare_emails(email1, email2)
            return result.get('confidence', 0.0)
        except Exception as e:
            logger.error(f"Error calculating similarity score: {e}")
            return 0.0
    
    def batch_compare(self, emails: List[Dict[str, Any]],
                     existing_projects: Optional[List[Dict[str, Any]]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare multiple emails to find similar ones
        
        Args:
            emails: List of emails to compare
            existing_projects: Optional existing projects for context
        
        Returns:
            Dictionary mapping email IDs to list of similar emails with scores
        """
        results = {}
        
        for i, email1 in enumerate(emails):
            email1_id = email1.get('id')
            if not email1_id:
                continue
            
            similar_emails = []
            
            for j, email2 in enumerate(emails):
                if i >= j:  # Skip self and already compared pairs
                    continue
                
                try:
                    comparison = self.compare_emails(email1, email2, existing_projects)
                    
                    if comparison.get('same_project', False):
                        similar_emails.append({
                            'email_id': email2.get('id'),
                            'confidence': comparison.get('confidence', 0.0),
                            'matching_indicators': comparison.get('matching_indicators', {})
                        })
                except Exception as e:
                    logger.warning(f"Error comparing emails {email1_id} and {email2.get('id')}: {e}")
                    continue
            
            if similar_emails:
                results[email1_id] = similar_emails
        
        return results


def get_similarity_service(ai_service: AIService) -> SimilarityService:
    """Factory function to create similarity service"""
    return SimilarityService(ai_service)

