"""
AI Service for OpenAI Integration
Handles OpenAI API calls for project detection and email grouping
"""

from typing import Optional, Dict, List, Any
import json
import logging
from openai import OpenAI
from app.config import settings
from app.services.prompts import PromptType, get_prompt

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.openai_api_key:
            raise AIServiceError("OpenAI API key not configured. Set OPENAI_API_KEY in environment variables.")
        
        if settings.ai_provider != "openai":
            raise AIServiceError(f"AI provider '{settings.ai_provider}' not yet implemented. Only 'openai' is supported.")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info(f"Initialized AI Service with model: {self.model}")
    
    def _call_openai(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Make API call to OpenAI
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature (0.0-2.0). Lower = more deterministic
            max_tokens: Maximum tokens in response
        
        Returns:
            Parsed JSON response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that extracts and analyzes project information from emails for Australian builders and carpenters. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {content[:200]}")
                # Try to extract JSON from response if wrapped in markdown
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    raise AIServiceError(f"Failed to parse AI response as JSON: {str(e)}")
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise AIServiceError(f"OpenAI API call failed: {str(e)}")
    
    def extract_project_name(self, email_content: str, email_subject: str, 
                            sender_email: str, existing_projects: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract project name from email"""
        prompt = get_prompt(
            PromptType.PROJECT_NAME_EXTRACTION,
            email_content=email_content,
            email_subject=email_subject,
            sender_email=sender_email,
            existing_projects=existing_projects
        )
        
        return self._call_openai(prompt, temperature=0.3)
    
    def extract_address(self, email_content: str, email_subject: str) -> Dict[str, Any]:
        """Extract property address from email"""
        prompt = get_prompt(
            PromptType.ADDRESS_DETECTION,
            email_content=email_content,
            email_subject=email_subject
        )
        
        return self._call_openai(prompt, temperature=0.3)
    
    def extract_job_number(self, email_content: str, email_subject: str) -> Dict[str, Any]:
        """Extract job numbers and reference codes from email"""
        prompt = get_prompt(
            PromptType.JOB_NUMBER_DETECTION,
            email_content=email_content,
            email_subject=email_subject
        )
        
        return self._call_openai(prompt, temperature=0.3)
    
    def extract_entities(self, email_content: str, email_subject: str, 
                        sender_email: str, sender_name: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive entity extraction from email"""
        prompt = get_prompt(
            PromptType.ENTITY_EXTRACTION,
            email_content=email_content,
            email_subject=email_subject,
            sender_email=sender_email,
            sender_name=sender_name
        )
        
        return self._call_openai(prompt, temperature=0.3, max_tokens=2500)
    
    def compare_emails(self, email1: Dict[str, Any], email2: Dict[str, Any], 
                     existing_projects: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Compare two emails to determine if they belong to the same project"""
        prompt = get_prompt(
            PromptType.CONTENT_SIMILARITY,
            email1_content=email1,
            email2_content=email2,
            existing_projects=existing_projects
        )
        
        return self._call_openai(prompt, temperature=0.2)  # Lower temperature for more consistent comparisons
    
    def group_emails(self, emails: List[Dict[str, Any]], 
                    existing_projects: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Group multiple emails into projects"""
        from app.services.prompts import ProjectDetectionPrompts
        
        prompt = ProjectDetectionPrompts.get_batch_project_grouping_prompt(
            emails=emails,
            existing_projects=existing_projects
        )
        
        return self._call_openai(prompt, temperature=0.3, max_tokens=3000)


def get_ai_service() -> AIService:
    """Factory function to get AI service instance"""
    return AIService()

