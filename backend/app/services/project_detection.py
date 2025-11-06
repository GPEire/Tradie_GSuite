"""
Project Detection Service
Match emails to existing projects or create new projects
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import uuid
from app.models.project import Project, EmailProjectMapping
from app.models.user import User
from app.services.ai import AIService, get_ai_service
from app.services.entity_extraction import EntityExtractionService, get_entity_extraction_service
from app.services.similarity import SimilarityService, get_similarity_service
from app.services.confidence_scoring import get_confidence_scoring_service

logger = logging.getLogger(__name__)


class ProjectDetectionService:
    """Service for detecting and managing projects"""
    
    def __init__(self, user: User, db: Session):
        """Initialize project detection service"""
        self.user = user
        self.db = db
        self.ai_service = get_ai_service()
        self.entity_extractor = get_entity_extraction_service(self.ai_service)
        self.similarity_service = get_similarity_service(self.ai_service)
        self.confidence_scoring = get_confidence_scoring_service()
    
    def detect_project_for_email(self, email_data: Dict[str, Any],
                                auto_create: bool = True,
                                confidence_threshold: float = 0.7) -> Optional[Project]:
        """
        Detect or create project for an email
        
        Args:
            email_data: Parsed email data
            auto_create: Whether to create new project if no match found
            confidence_threshold: Minimum confidence to match existing project
        
        Returns:
            Project (existing or newly created)
        """
        try:
            # Extract entities from email
            entities = self.entity_extractor.extract_from_email(email_data)
            
            project_name = entities.get('project_name')
            address = entities.get('address', {}).get('full_address') if isinstance(entities.get('address'), dict) else entities.get('address')
            job_numbers = entities.get('job_numbers', [])
            client_info = entities.get('client_info', {})
            
            # Try to match existing project
            matched_project = self._match_to_existing_project(
                project_name=project_name,
                address=address,
                job_numbers=job_numbers,
                client_email=client_info.get('email') if isinstance(client_info, dict) else None,
                threshold=confidence_threshold
            )
            
            if matched_project:
                logger.info(f"Matched email {email_data.get('id')} to existing project {matched_project.project_id}")
                return matched_project
            
            # No match found - create new project if auto_create is True
            if auto_create and project_name:
                new_project = self._create_project_from_entities(
                    entities=entities,
                    email_id=email_data.get('id'),
                    confidence=entities.get('confidence', 0.0)
                )
                logger.info(f"Created new project {new_project.project_id} for email {email_data.get('id')}")
                return new_project
            
            # No match and auto_create is False
            return None
            
        except Exception as e:
            logger.error(f"Error detecting project for email {email_data.get('id')}: {e}")
            raise
    
    def _match_to_existing_project(self, project_name: Optional[str] = None,
                                  address: Optional[str] = None,
                                  job_numbers: Optional[List[str]] = None,
                                  client_email: Optional[str] = None,
                                  threshold: float = 0.7) -> Optional[Project]:
        """Match to existing project using multiple criteria"""
        
        # Get all active projects for user
        projects = self.db.query(Project).filter(
            Project.user_id == self.user.id,
            Project.status == "active"
        ).all()
        
        if not projects:
            return None
        
        best_match = None
        best_confidence = 0.0
        
        for project in projects:
            confidence = 0.0
            match_reasons = []
            
            # Match by project name
            if project_name and project.project_name:
                if project_name.lower() == project.project_name.lower():
                    confidence += 0.4
                    match_reasons.append("exact_name_match")
                elif project_name.lower() in project.project_name.lower() or project.project_name.lower() in project_name.lower():
                    confidence += 0.3
                    match_reasons.append("partial_name_match")
                
                # Check aliases
                if project.project_name_aliases:
                    for alias in project.project_name_aliases:
                        if project_name.lower() == alias.lower() or project_name.lower() in alias.lower():
                            confidence += 0.3
                            match_reasons.append("alias_match")
                            break
            
            # Match by address
            if address and project.address:
                if address.lower() == project.address.lower():
                    confidence += 0.4
                    match_reasons.append("exact_address_match")
                elif address.lower() in project.address.lower() or project.address.lower() in address.lower():
                    confidence += 0.3
                    match_reasons.append("partial_address_match")
            
            # Match by job number
            if job_numbers and project.job_numbers:
                for job_num in job_numbers:
                    if job_num in project.job_numbers:
                        confidence += 0.3
                        match_reasons.append("job_number_match")
                        break
            
            # Match by client email
            if client_email and project.client_email:
                if client_email.lower() == project.client_email.lower():
                    confidence += 0.2
                    match_reasons.append("client_email_match")
            
            # Normalize confidence (max 1.0)
            confidence = min(1.0, confidence)
            
            if confidence > best_confidence and confidence >= threshold:
                best_confidence = confidence
                best_match = project
        
        return best_match
    
    def _create_project_from_entities(self, entities: Dict[str, Any],
                                     email_id: str,
                                     confidence: float = 0.0) -> Project:
        """Create a new project from extracted entities"""
        
        # Generate unique project ID
        project_id = f"proj_{self.user.id}_{uuid.uuid4().hex[:12]}"
        
        # Extract address components
        address_data = entities.get('address', {})
        if isinstance(address_data, dict):
            full_address = address_data.get('full_address')
            street = address_data.get('street')
            suburb = address_data.get('suburb')
            state = address_data.get('state')
            postcode = address_data.get('postcode')
        else:
            full_address = address_data
            street = suburb = state = postcode = None
        
        # Extract client info
        client_info = entities.get('client_info', {})
        if isinstance(client_info, dict):
            client_name = client_info.get('name')
            client_email = client_info.get('email')
            client_phone = client_info.get('phone')
            client_company = client_info.get('company')
        else:
            client_name = client_email = client_phone = client_company = None
        
        project = Project(
            user_id=self.user.id,
            project_id=project_id,
            project_name=entities.get('project_name', 'Unnamed Project'),
            address=full_address,
            street=street,
            suburb=suburb,
            state=state,
            postcode=postcode,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            client_company=client_company,
            project_type=entities.get('project_type'),
            job_numbers=entities.get('job_numbers', []),
            status="active",
            email_count=0,
            created_from_email_id=email_id,
            confidence_score=str(confidence),
            needs_review=confidence < 0.7
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def add_email_to_project(self, email_id: str, project: Project,
                           thread_id: Optional[str] = None,
                           confidence: Optional[float] = None,
                           method: str = "auto") -> EmailProjectMapping:
        """Add email to project"""
        
        # Check if mapping already exists
        existing = self.db.query(EmailProjectMapping).filter(
            EmailProjectMapping.email_id == email_id,
            EmailProjectMapping.project_id == project.id,
            EmailProjectMapping.is_active == True
        ).first()
        
        if existing:
            return existing
        
        # Create new mapping
        mapping = EmailProjectMapping(
            user_id=self.user.id,
            project_id=project.id,
            email_id=email_id,
            thread_id=thread_id,
            confidence=str(confidence) if confidence else None,
            association_method=method,
            is_active=True
        )
        
        self.db.add(mapping)
        
        # Update project statistics
        project.email_count += 1
        project.last_email_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mapping)
        
        return mapping
    
    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by project_id"""
        return self.db.query(Project).filter(
            Project.project_id == project_id,
            Project.user_id == self.user.id
        ).first()
    
    def get_all_projects(self, status: Optional[str] = None) -> List[Project]:
        """Get all projects for user"""
        query = self.db.query(Project).filter(Project.user_id == self.user.id)
        
        if status:
            query = query.filter(Project.status == status)
        
        return query.order_by(Project.last_email_at.desc(), Project.created_at.desc()).all()
    
    def update_project_name_aliases(self, project: Project, aliases: List[str]) -> Project:
        """Update project name aliases"""
        project.project_name_aliases = aliases
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def add_project_alias(self, project: Project, alias: str) -> Project:
        """Add alias to project"""
        aliases = project.project_name_aliases or []
        if alias not in aliases:
            aliases.append(alias)
            project.project_name_aliases = aliases
            self.db.commit()
            self.db.refresh(project)
        return project


def get_project_detection_service(user: User, db: Session) -> ProjectDetectionService:
    """Factory function to create project detection service"""
    return ProjectDetectionService(user, db)

