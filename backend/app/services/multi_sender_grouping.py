"""
Multi-Sender Project Grouping Service
Group emails from different senders that belong to the same project
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import logging
from app.models.user import User
from app.models.project import Project, EmailProjectMapping
from app.services.ai import AIService, get_ai_service
from app.services.entity_extraction import EntityExtractionService, get_entity_extraction_service
from app.services.similarity import SimilarityService, get_similarity_service
from app.services.project_detection import ProjectDetectionService, get_project_detection_service
from collections import defaultdict

logger = logging.getLogger(__name__)


class MultiSenderGroupingService:
    """Service for grouping emails from multiple senders"""
    
    def __init__(self, user: User, db: Session):
        """Initialize multi-sender grouping service"""
        self.user = user
        self.db = db
        self.ai_service = get_ai_service()
        self.entity_extractor = get_entity_extraction_service(self.ai_service)
        self.similarity_service = get_similarity_service(self.ai_service)
        self.project_detection = get_project_detection_service(user, db)
    
    def group_multi_sender_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Group emails from multiple senders into projects
        
        Uses shared project identifiers:
        - Same property address
        - Same job number
        - Same project name
        - Similar content (semantic similarity)
        """
        try:
            # Extract entities for all emails
            email_entities = []
            for email in emails:
                try:
                    entities = self.entity_extractor.extract_from_email(email)
                    entities['email_id'] = email.get('id')
                    entities['email'] = email
                    email_entities.append(entities)
                except Exception as e:
                    logger.warning(f"Error extracting entities: {e}")
                    continue
            
            # Group by address (strongest indicator)
            address_groups = self._group_by_address(email_entities)
            
            # Group by job number (secondary indicator)
            job_number_groups = self._group_by_job_number(email_entities)
            
            # Group by project name (tertiary indicator)
            project_name_groups = self._group_by_project_name(email_entities)
            
            # Merge groups intelligently
            merged_groups = self._merge_groups(
                address_groups, job_number_groups, project_name_groups, email_entities
            )
            
            # Create or match projects
            project_assignments = []
            for group in merged_groups:
                project = self._get_or_create_project_for_group(group)
                
                # Associate emails with project
                for email_id in group['email_ids']:
                    email = next((e for e in emails if e.get('id') == email_id), None)
                    if email:
                        mapping = self.project_detection.add_email_to_project(
                            email_id=email_id,
                            project=project,
                            thread_id=email.get('thread_id'),
                            confidence=group.get('confidence'),
                            method="multi_sender"
                        )
                        project_assignments.append({
                            "email_id": email_id,
                            "project_id": project.project_id,
                            "project_name": project.project_name
                        })
            
            return {
                "projects_created": len(set(g['project_id'] for g in merged_groups if g.get('project_id'))),
                "emails_assigned": len(project_assignments),
                "assignments": project_assignments
            }
            
        except Exception as e:
            logger.error(f"Error in multi-sender grouping: {e}")
            raise
    
    def _group_by_address(self, email_entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group emails by property address"""
        address_groups = defaultdict(list)
        
        for entity in email_entities:
            address = entity.get('address', {}).get('full_address') if isinstance(entity.get('address'), dict) else entity.get('address')
            if address:
                # Normalize address for matching
                normalized = address.lower().strip()
                address_groups[normalized].append(entity)
        
        return dict(address_groups)
    
    def _group_by_job_number(self, email_entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group emails by job number"""
        job_number_groups = defaultdict(list)
        
        for entity in email_entities:
            job_numbers = entity.get('job_numbers', [])
            for job_num in job_numbers:
                if job_num:
                    normalized = job_num.lower().strip()
                    job_number_groups[normalized].append(entity)
        
        return dict(job_number_groups)
    
    def _group_by_project_name(self, email_entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group emails by project name"""
        project_name_groups = defaultdict(list)
        
        for entity in email_entities:
            project_name = entity.get('project_name')
            if project_name:
                normalized = project_name.lower().strip()
                project_name_groups[normalized].append(entity)
        
        return dict(project_name_groups)
    
    def _merge_groups(self, address_groups: Dict, job_number_groups: Dict,
                     project_name_groups: Dict, all_entities: List[Dict]) -> List[Dict[str, Any]]:
        """Merge groups using priority: address > job number > project name"""
        final_groups = []
        processed_emails = set()
        
        # Process by address (highest priority)
        for address, entities in address_groups.items():
            if len(entities) > 1:
                email_ids = [e['email_id'] for e in entities if e['email_id'] not in processed_emails]
                if email_ids:
                    processed_emails.update(email_ids)
                    
                    # Get senders (including CC/BCC)
                    senders = self._extract_all_senders([e['email'] for e in entities])
                    
                    final_groups.append({
                        'project_name': entities[0].get('project_name', f"Project at {address}"),
                        'address': address,
                        'email_ids': email_ids,
                        'senders': senders,
                        'confidence': 0.9,
                        'key_indicators': ['address_match']
                    })
        
        # Process by job number (medium priority)
        for job_number, entities in job_number_groups.items():
            if len(entities) > 1:
                email_ids = [e['email_id'] for e in entities if e['email_id'] not in processed_emails]
                if email_ids:
                    processed_emails.update(email_ids)
                    
                    senders = self._extract_all_senders([e['email'] for e in entities])
                    
                    final_groups.append({
                        'project_name': entities[0].get('project_name', f"Project {job_number}"),
                        'job_number': job_number,
                        'email_ids': email_ids,
                        'senders': senders,
                        'confidence': 0.8,
                        'key_indicators': ['job_number_match']
                    })
        
        # Process by project name (lower priority)
        for project_name, entities in project_name_groups.items():
            if len(entities) > 1:
                email_ids = [e['email_id'] for e in entities if e['email_id'] not in processed_emails]
                if email_ids:
                    processed_emails.update(email_ids)
                    
                    senders = self._extract_all_senders([e['email'] for e in entities])
                    
                    final_groups.append({
                        'project_name': project_name,
                        'email_ids': email_ids,
                        'senders': senders,
                        'confidence': 0.7,
                        'key_indicators': ['project_name_match']
                    })
        
        return final_groups
    
    def _extract_all_senders(self, emails: List[Dict[str, Any]]) -> List[str]:
        """Extract all senders, including CC/BCC participants"""
        senders = set()
        
        for email in emails:
            # From address
            from_addr = email.get('from', {})
            if isinstance(from_addr, dict):
                if from_addr.get('email'):
                    senders.add(from_addr['email'].lower())
            elif isinstance(from_addr, str):
                senders.add(from_addr.lower())
            
            # To addresses
            to_addresses = email.get('to', []) or email.get('to_addresses', [])
            for addr in to_addresses:
                if isinstance(addr, dict) and addr.get('email'):
                    senders.add(addr['email'].lower())
                elif isinstance(addr, str):
                    senders.add(addr.lower())
            
            # CC addresses
            cc_addresses = email.get('cc', []) or email.get('cc_addresses', [])
            for addr in cc_addresses:
                if isinstance(addr, dict) and addr.get('email'):
                    senders.add(addr['email'].lower())
                elif isinstance(addr, str):
                    senders.add(addr.lower())
            
            # BCC addresses (if available)
            bcc_addresses = email.get('bcc', []) or email.get('bcc_addresses', [])
            for addr in bcc_addresses:
                if isinstance(addr, dict) and addr.get('email'):
                    senders.add(addr['email'].lower())
                elif isinstance(addr, str):
                    senders.add(addr.lower())
        
        return list(senders)
    
    def _get_or_create_project_for_group(self, group: Dict[str, Any]) -> Project:
        """Get existing project or create new one for group"""
        # Try to find existing project
        project_name = group.get('project_name')
        address = group.get('address')
        job_number = group.get('job_number')
        
        # Search by project name
        if project_name:
            project = self.db.query(Project).filter(
                Project.user_id == self.user.id,
                Project.status == "active",
                Project.project_name.ilike(f"%{project_name}%")
            ).first()
            
            if project:
                return project
        
        # Search by address
        if address:
            project = self.db.query(Project).filter(
                Project.user_id == self.user.id,
                Project.status == "active",
                Project.address.ilike(f"%{address}%")
            ).first()
            
            if project:
                return project
        
        # Search by job number
        if job_number:
            projects = self.db.query(Project).filter(
                Project.user_id == self.user.id,
                Project.status == "active"
            ).all()
            
            for project in projects:
                if project.job_numbers and job_number in project.job_numbers:
                    return project
        
        # Create new project
        # Build entity dict for project creation
        entities = {
            'project_name': project_name or 'Unnamed Project',
            'address': {'full_address': address} if address else {},
            'job_numbers': [job_number] if job_number else [],
            'client_info': {}
        }
        
        project = self.project_detection._create_project_from_entities(
            entities=entities,
            email_id=group['email_ids'][0] if group.get('email_ids') else None,
            confidence=group.get('confidence', 0.7)
        )
        
        return project


def get_multi_sender_grouping_service(user: User, db: Session) -> MultiSenderGroupingService:
    """Factory function to create multi-sender grouping service"""
    return MultiSenderGroupingService(user, db)

