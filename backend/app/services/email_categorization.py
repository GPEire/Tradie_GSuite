"""
Email Categorization Service
Categorize emails by type (inquiry, ongoing, variation, quote, payment, completion)
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import logging
import re
from app.models.user import User
from app.services.ai import AIService, get_ai_service
from app.services.entity_extraction import EntityExtractionService, get_entity_extraction_service

logger = logging.getLogger(__name__)


class EmailCategorizationService:
    """Service for categorizing emails"""
    
    # Email type categories
    CATEGORY_NEW_INQUIRY = "new_inquiry"
    CATEGORY_ONGOING = "ongoing"
    CATEGORY_VARIATION = "variation"
    CATEGORY_QUOTE = "quote"
    CATEGORY_PAYMENT = "payment"
    CATEGORY_COMPLETION = "completion"
    CATEGORY_FOLLOW_UP = "follow_up"
    CATEGORY_OTHER = "other"
    
    def __init__(self, user: User, db: Session):
        """Initialize email categorization service"""
        self.user = user
        self.db = db
        self.ai_service = get_ai_service()
        self.entity_extractor = get_entity_extraction_service(self.ai_service)
    
    def categorize_email(self, email_data: Dict[str, Any],
                        existing_project: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Categorize email by type
        
        Args:
            email_data: Parsed email data
            existing_project: Optional existing project context
        
        Returns:
            Categorization result with category, confidence, and flags
        """
        try:
            # Extract entities
            entities = self.entity_extractor.extract_from_email(email_data)
            
            # Rule-based categorization
            category, confidence, indicators = self._categorize_by_rules(email_data, entities)
            
            # AI-based categorization if needed
            if confidence < 0.7:
                ai_category = self._categorize_by_ai(email_data, entities)
                if ai_category['confidence'] > confidence:
                    category = ai_category['category']
                    confidence = ai_category['confidence']
                    indicators.extend(ai_category.get('indicators', []))
            
            # Determine if new inquiry
            is_new_inquiry = self._is_new_inquiry(email_data, entities, existing_project)
            
            return {
                "category": category,
                "confidence": confidence,
                "indicators": list(set(indicators)),
                "is_new_inquiry": is_new_inquiry,
                "is_ongoing": category == self.CATEGORY_ONGOING,
                "requires_action": category in [
                    self.CATEGORY_NEW_INQUIRY,
                    self.CATEGORY_VARIATION,
                    self.CATEGORY_QUOTE,
                    self.CATEGORY_PAYMENT
                ]
            }
            
        except Exception as e:
            logger.error(f"Error categorizing email: {e}")
            return {
                "category": self.CATEGORY_OTHER,
                "confidence": 0.0,
                "indicators": [],
                "is_new_inquiry": False,
                "is_ongoing": False,
                "requires_action": False
            }
    
    def _categorize_by_rules(self, email_data: Dict[str, Any],
                            entities: Dict[str, Any]) -> tuple[str, float, List[str]]:
        """Categorize using rule-based heuristics"""
        subject = email_data.get('subject', '').lower()
        body_text = (email_data.get('body_text', '') or email_data.get('snippet', '')).lower()
        
        indicators = []
        confidence = 0.0
        category = self.CATEGORY_OTHER
        
        # New Inquiry patterns
        inquiry_patterns = [
            r'\b(quote|quotation|estimate|pricing|cost|price)\b',
            r'\b(inquiry|enquiry|interested|considering)\b',
            r'\b(new project|new job|new build|renovation)\b',
            r'\b(available|can you|could you|would you)\b'
        ]
        
        if any(re.search(pattern, subject + ' ' + body_text[:500]) for pattern in inquiry_patterns):
            category = self.CATEGORY_NEW_INQUIRY
            confidence = 0.8
            indicators.append("inquiry_keywords")
        
        # Quote patterns
        quote_patterns = [
            r'\b(quote|quotation|estimate|pricing|cost breakdown)\b',
            r'\b(please quote|provide quote|send quote)\b'
        ]
        
        if any(re.search(pattern, subject + ' ' + body_text[:500]) for pattern in quote_patterns):
            category = self.CATEGORY_QUOTE
            confidence = 0.9
            indicators.append("quote_keywords")
        
        # Payment patterns
        payment_patterns = [
            r'\b(invoice|payment|paid|invoice #|invoice number)\b',
            r'\b(receipt|payment received|payment confirmation)\b',
            r'\b(deposit|progress payment|final payment)\b'
        ]
        
        if any(re.search(pattern, subject + ' ' + body_text[:500]) for pattern in payment_patterns):
            category = self.CATEGORY_PAYMENT
            confidence = 0.9
            indicators.append("payment_keywords")
        
        # Variation patterns
        variation_patterns = [
            r'\b(variation|change|modification|adjustment)\b',
            r'\b(additional work|extra|scope change)\b',
            r'\b(revised|updated|changed)\b'
        ]
        
        if any(re.search(pattern, subject + ' ' + body_text[:500]) for pattern in variation_patterns):
            category = self.CATEGORY_VARIATION
            confidence = 0.85
            indicators.append("variation_keywords")
        
        # Completion patterns
        completion_patterns = [
            r'\b(completed|finished|done|final inspection)\b',
            r'\b(handover|hand over|sign off)\b',
            r'\b(project complete|job complete)\b'
        ]
        
        if any(re.search(pattern, subject + ' ' + body_text[:500]) for pattern in completion_patterns):
            category = self.CATEGORY_COMPLETION
            confidence = 0.9
            indicators.append("completion_keywords")
        
        # Ongoing communication (default if no other match)
        if category == self.CATEGORY_OTHER:
            # Check if it's a reply
            if email_data.get('in_reply_to') or email_data.get('references'):
                category = self.CATEGORY_ONGOING
                confidence = 0.7
                indicators.append("reply_thread")
            else:
                category = self.CATEGORY_ONGOING
                confidence = 0.6
                indicators.append("general_communication")
        
        return category, confidence, indicators
    
    def _categorize_by_ai(self, email_data: Dict[str, Any],
                         entities: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to categorize email"""
        try:
            # Use AI to determine category
            prompt = f"""Categorize this email for a builder/carpenter business:

Subject: {email_data.get('subject', '')}
Content: {(email_data.get('body_text', '') or email_data.get('snippet', ''))[:1000]}

Categories:
- new_inquiry: New customer inquiry or quote request
- ongoing: Ongoing project communication
- variation: Change request or variation to existing project
- quote: Quote or estimate discussion
- payment: Invoice or payment related
- completion: Project completion or handover
- follow_up: Follow-up communication
- other: Other types

Return ONLY a JSON object:
{{
    "category": "category_name",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""
            
            result = self.ai_service._call_openai(prompt, temperature=0.3)
            
            return {
                "category": result.get('category', self.CATEGORY_OTHER),
                "confidence": result.get('confidence', 0.5),
                "indicators": [result.get('reasoning', '')]
            }
            
        except Exception as e:
            logger.warning(f"Error in AI categorization: {e}")
            return {
                "category": self.CATEGORY_OTHER,
                "confidence": 0.5,
                "indicators": []
            }
    
    def _is_new_inquiry(self, email_data: Dict[str, Any],
                        entities: Dict[str, Any],
                        existing_project: Optional[Dict[str, Any]]) -> bool:
        """Determine if email is a new inquiry"""
        
        # If no existing project, likely new inquiry
        if not existing_project:
            return True
        
        # Check if it's a quote request
        subject = email_data.get('subject', '').lower()
        body = (email_data.get('body_text', '') or email_data.get('snippet', '')).lower()
        
        inquiry_keywords = ['quote', 'quotation', 'estimate', 'inquiry', 'enquiry', 'interested']
        if any(keyword in subject or keyword in body[:200] for keyword in inquiry_keywords):
            return True
        
        # Check if sender is new to this project
        from_addr = email_data.get('from', {})
        sender_email = from_addr.get('email', '') if isinstance(from_addr, dict) else str(from_addr)
        
        # If project has no previous emails from this sender, might be new inquiry
        # (This would need project email history - simplified for now)
        
        return False
    
    def categorize_batch(self, emails: List[Dict[str, Any]],
                        existing_projects: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Categorize multiple emails"""
        results = []
        
        for email in emails:
            email_id = email.get('id')
            project_id = existing_projects.get(email_id) if existing_projects else None
            
            existing_project = None
            if project_id:
                # TODO: Fetch project from database
                pass
            
            categorization = self.categorize_email(email, existing_project)
            categorization['email_id'] = email_id
            
            results.append(categorization)
        
        return results


def get_email_categorization_service(user: User, db: Session) -> EmailCategorizationService:
    """Factory function to create email categorization service"""
    return EmailCategorizationService(user, db)

