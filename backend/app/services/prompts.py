"""
Prompt Engineering for Project Detection
Well-crafted prompts for extracting project information from emails
"""

from typing import Dict, List, Optional
from enum import Enum


class PromptType(str, Enum):
    """Types of prompts available"""
    PROJECT_NAME_EXTRACTION = "project_name_extraction"
    ADDRESS_DETECTION = "address_detection"
    JOB_NUMBER_DETECTION = "job_number_detection"
    CONTENT_SIMILARITY = "content_similarity"
    ENTITY_EXTRACTION = "entity_extraction"


class ProjectDetectionPrompts:
    """Collection of prompts for project detection and email grouping"""
    
    @staticmethod
    def get_project_name_extraction_prompt(email_content: str, email_subject: str, 
                                         sender_email: str, existing_projects: Optional[List[str]] = None) -> str:
        """
        Extract project name from email content
        
        Focuses on identifying:
        - Project names (e.g., "Smith Residence Renovation", "Main Street Build")
        - Job names (e.g., "Kitchen Renovation", "Bathroom Upgrade")
        - Property names/descriptions
        - Client-specific project identifiers
        """
        existing_projects_text = ""
        if existing_projects:
            existing_projects_text = f"\n\nExisting projects for this sender: {', '.join(existing_projects)}"
        
        return f"""You are an AI assistant helping builders and carpenters organize emails by project/job.

Analyze the following email and extract the project name or job identifier. For builders and carpenters in Australia, projects are typically identified by:
- Property address or location
- Client name + project type (e.g., "Smith Kitchen Renovation")
- Job descriptions (e.g., "Deck Construction", "Bathroom Renovation")
- Property names or building names
- Job numbers or reference codes

Email Subject: {email_subject}
Sender: {sender_email}
Email Content:
{email_content[:2000]}{existing_projects_text}

Extract the project name or job identifier from this email. If multiple projects are mentioned, identify the PRIMARY project this email is about.

Return ONLY a JSON object with this structure:
{{
    "project_name": "extracted project name or null if not found",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of why this project name was identified",
    "alternative_names": ["any alternative project names or variations mentioned"],
    "project_type": "renovation|new_build|maintenance|quote|other or null",
    "keywords": ["key words that indicate project identity"]
}}

If no clear project can be identified, set project_name to null and confidence to a low value (<0.5)."""

    @staticmethod
    def get_address_detection_prompt(email_content: str, email_subject: str) -> str:
        """
        Extract property addresses and location information
        
        Focuses on Australian addresses and property locations
        """
        return f"""You are an AI assistant extracting property addresses and location information from emails for Australian builders and carpenters.

Analyze the email and extract any property addresses, locations, or site information. Australian addresses typically include:
- Street number and name
- Suburb/town
- State (VIC, NSW, QLD, SA, WA, TAS, NT, ACT)
- Postcode
- Property descriptions (e.g., "corner block", "rear unit", "lot 5")

Email Subject: {email_subject}
Email Content:
{email_content[:2000]}

Extract all addresses and location information. Return ONLY a JSON object:
{{
    "addresses": [
        {{
            "full_address": "complete address string if found",
            "street": "street name and number",
            "suburb": "suburb or town",
            "state": "state abbreviation (VIC, NSW, etc.)",
            "postcode": "postcode",
            "property_description": "any additional property details",
            "confidence": 0.0-1.0
        }}
    ],
    "location_keywords": ["any location-related keywords mentioned"],
    "site_description": "any description of the property or site"
}}

If no address is found, return addresses as an empty array."""

    @staticmethod
    def get_job_number_detection_prompt(email_content: str, email_subject: str) -> str:
        """
        Extract job numbers, reference codes, and project identifiers
        
        Common patterns:
        - Job #123, Job-123, JOB-2024-001
        - Quote #456
        - Ref: ABC123
        - Project ID: XYZ789
        """
        return f"""You are an AI assistant extracting job numbers, reference codes, and project identifiers from emails.

Builders and carpenters often use job numbers, quote numbers, or reference codes to track projects. Extract any such identifiers from the email.

Common patterns:
- Job #123, Job-123, JOB-2024-001
- Quote #456, Quote-456
- Ref: ABC123, Reference: XYZ789
- Project ID: PROJ-2024-001
- Invoice #INV-123
- PO Number: PO-456

Email Subject: {email_subject}
Email Content:
{email_content[:2000]}

Return ONLY a JSON object:
{{
    "job_numbers": [
        {{
            "value": "the job number or code",
            "type": "job_number|quote_number|reference|invoice|po|other",
            "confidence": 0.0-1.0,
            "context": "where it was found (subject, body, signature)"
        }}
    ],
    "project_codes": ["any project codes or identifiers"],
    "invoice_numbers": ["any invoice or PO numbers mentioned"]
}}

If no job numbers are found, return empty arrays."""

    @staticmethod
    def get_entity_extraction_prompt(email_content: str, email_subject: str, 
                                   sender_email: str, sender_name: Optional[str] = None) -> str:
        """
        Comprehensive entity extraction from email
        
        Extracts:
        - Project name
        - Address
        - Job numbers
        - Client/customer information
        - Project type
        - Key dates
        """
        sender_info = f"{sender_name} ({sender_email})" if sender_name else sender_email
        
        return f"""You are an AI assistant extracting structured information from emails for Australian builders and carpenters.

Analyze the email and extract all relevant project information.

Email Subject: {email_subject}
Sender: {sender_info}
Email Content:
{email_content[:3000]}

Extract comprehensive project information. Return ONLY a JSON object:
{{
    "project_name": "primary project name or null",
    "address": {{
        "full_address": "complete address or null",
        "street": "street address",
        "suburb": "suburb/town",
        "state": "state abbreviation",
        "postcode": "postcode"
    }},
    "job_numbers": ["all job numbers, quote numbers, or reference codes"],
    "client_info": {{
        "name": "client/customer name",
        "email": "client email if different from sender",
        "phone": "phone number if mentioned",
        "company": "company name if mentioned"
    }},
    "project_type": "renovation|new_build|maintenance|quote|variation|payment|completion|other",
    "key_dates": {{
        "start_date": "project start date if mentioned",
        "deadline": "deadline or due date",
        "meeting_date": "meeting or site visit date"
    }},
    "project_keywords": ["keywords that identify this project"],
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of extracted information"
}}

Use null for any fields that cannot be determined from the email."""

    @staticmethod
    def get_content_similarity_prompt(email1_content: Dict, email2_content: Dict, 
                                    existing_projects: Optional[List[Dict]] = None) -> str:
        """
        Compare two emails to determine if they belong to the same project
        
        Uses semantic similarity and entity matching
        """
        email1_text = f"""
Email 1:
Subject: {email1_content.get('subject', '')}
From: {email1_content.get('from', '')}
Content: {email1_content.get('body_text', '')[:1000]}
"""
        
        email2_text = f"""
Email 2:
Subject: {email2_content.get('subject', '')}
From: {email2_content.get('from', '')}
Content: {email2_content.get('body_text', '')[:1000]}
"""
        
        projects_text = ""
        if existing_projects:
            projects_list = "\n".join([f"- {p.get('name', 'Unknown')}: {p.get('address', 'N/A')}" 
                                       for p in existing_projects[:5]])
            projects_text = f"\n\nExisting Projects:\n{projects_list}"
        
        return f"""You are an AI assistant determining if two emails belong to the same project/job for Australian builders and carpenters.

Compare the two emails and determine if they are related to the same project based on:
- Project name or job identifier
- Property address or location
- Job numbers or reference codes
- Client/customer information
- Project type and description
- Semantic similarity of content

{email1_text}

{email2_text}{projects_text}

Analyze the similarity and return ONLY a JSON object:
{{
    "same_project": true/false,
    "confidence": 0.0-1.0,
    "matching_indicators": {{
        "project_name_match": "description of project name similarity",
        "address_match": "description of address similarity",
        "job_number_match": "description of job number match",
        "client_match": "description of client information match",
        "content_similarity": "description of content similarity"
    }},
    "suggested_project_name": "suggested unified project name if same_project is true",
    "reasoning": "detailed explanation of why emails are or aren't the same project"
}}

Consider:
- Same sender discussing same property = likely same project
- Different senders but same address = likely same project
- Same project name mentioned = likely same project
- Different job numbers = might be different projects or variations
- Similar content but different addresses = likely different projects"""

    @staticmethod
    def get_batch_project_grouping_prompt(emails: List[Dict], 
                                         existing_projects: Optional[List[Dict]] = None) -> str:
        """
        Group multiple emails into projects
        
        Analyzes a batch of emails and groups them by project
        """
        emails_text = "\n\n".join([
            f"Email {i+1}:\n"
            f"Subject: {email.get('subject', '')}\n"
            f"From: {email.get('from', '')}\n"
            f"Date: {email.get('date', '')}\n"
            f"Content: {email.get('body_text', '')[:500]}"
            for i, email in enumerate(emails[:10])  # Limit to 10 emails for token efficiency
        ])
        
        projects_text = ""
        if existing_projects:
            projects_list = "\n".join([f"- {p.get('name', 'Unknown')} ({p.get('address', 'N/A')})" 
                                       for p in existing_projects[:10]])
            projects_text = f"\n\nExisting Projects:\n{projects_list}"
        
        return f"""You are an AI assistant grouping emails by project/job for Australian builders and carpenters.

Analyze the following emails and group them by project. Each project should contain related emails based on:
- Same project name or job identifier
- Same property address
- Same client/customer
- Related job numbers or references
- Similar project descriptions

Emails to analyze:
{emails_text}{projects_text}

Return ONLY a JSON object:
{{
    "project_groups": [
        {{
            "project_name": "project name",
            "project_id": "suggested unique identifier",
            "email_ids": ["list of email IDs in this group"],
            "confidence": 0.0-1.0,
            "key_indicators": ["indicators that group these emails"],
            "address": "property address if identified",
            "client": "client name if identified",
            "project_type": "renovation|new_build|maintenance|other"
        }}
    ],
    "unmatched_emails": ["email IDs that couldn't be grouped"],
    "reasoning": "explanation of grouping decisions"
}}

Group emails intelligently - if emails are clearly related (same address, same client, etc.), group them together even if project names vary slightly."""


def get_prompt(prompt_type: PromptType, **kwargs) -> str:
    """Factory function to get prompts by type"""
    prompts = ProjectDetectionPrompts()
    
    if prompt_type == PromptType.PROJECT_NAME_EXTRACTION:
        return prompts.get_project_name_extraction_prompt(
            kwargs.get('email_content', ''),
            kwargs.get('email_subject', ''),
            kwargs.get('sender_email', ''),
            kwargs.get('existing_projects')
        )
    
    elif prompt_type == PromptType.ADDRESS_DETECTION:
        return prompts.get_address_detection_prompt(
            kwargs.get('email_content', ''),
            kwargs.get('email_subject', '')
        )
    
    elif prompt_type == PromptType.JOB_NUMBER_DETECTION:
        return prompts.get_job_number_detection_prompt(
            kwargs.get('email_content', ''),
            kwargs.get('email_subject', '')
        )
    
    elif prompt_type == PromptType.CONTENT_SIMILARITY:
        return prompts.get_content_similarity_prompt(
            kwargs.get('email1_content', {}),
            kwargs.get('email2_content', {}),
            kwargs.get('existing_projects')
        )
    
    elif prompt_type == PromptType.ENTITY_EXTRACTION:
        return prompts.get_entity_extraction_prompt(
            kwargs.get('email_content', ''),
            kwargs.get('email_subject', ''),
            kwargs.get('sender_email', ''),
            kwargs.get('sender_name')
        )
    
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")

