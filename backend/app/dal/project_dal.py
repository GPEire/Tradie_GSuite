"""
Project Data Access Layer
TASK-038: Database operations for projects
"""

from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.dal.base import BaseDAL
from app.models.project import Project, EmailProjectMapping
from app.models.user import User

logger = logging.getLogger(__name__)


class ProjectDAL(BaseDAL[Project]):
    """Data Access Layer for Project operations"""
    
    def get_by_project_id(self, user_id: int, project_id: str) -> Optional[Project]:
        """Get project by user and project_id"""
        return self.db.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.project_id == project_id
            )
        ).first()
    
    def get_user_projects(self, user_id: int, status: Optional[str] = None) -> List[Project]:
        """Get all projects for user, optionally filtered by status"""
        query = self.db.query(self.model).filter(self.model.user_id == user_id)
        
        if status:
            query = query.filter(self.model.status == status)
        
        return query.order_by(self.model.last_email_at.desc().nullslast()).all()
    
    def get_projects_needing_review(self, user_id: int) -> List[Project]:
        """Get projects that need review"""
        return self.db.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.needs_review == True
            )
        ).all()
    
    def update_email_count(self, project_id: int) -> None:
        """Update email count for project"""
        count = self.db.query(EmailProjectMapping).filter(
            and_(
                EmailProjectMapping.project_id == project_id,
                EmailProjectMapping.is_active == True
            )
        ).count()
        
        project = self.get(project_id)
        if project:
            project.email_count = count
            self.db.commit()
    
    def get_project_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get project statistics for user"""
        total = self.db.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id
        ).scalar()
        
        active = self.db.query(func.count(self.model.id)).filter(
            and_(
                self.model.user_id == user_id,
                self.model.status == 'active'
            )
        ).scalar()
        
        needs_review = self.db.query(func.count(self.model.id)).filter(
            and_(
                self.model.user_id == user_id,
                self.model.needs_review == True
            )
        ).scalar()
        
        total_emails = self.db.query(func.sum(self.model.email_count)).filter(
            self.model.user_id == user_id
        ).scalar() or 0
        
        return {
            'total_projects': total,
            'active_projects': active,
            'needs_review': needs_review,
            'total_emails': total_emails
        }


class EmailProjectMappingDAL(BaseDAL[EmailProjectMapping]):
    """Data Access Layer for Email-Project Mappings"""
    
    def get_by_email_id(self, user_id: int, email_id: str) -> List[EmailProjectMapping]:
        """Get all mappings for an email"""
        return self.db.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.email_id == email_id,
                self.model.is_active == True
            )
        ).all()
    
    def get_project_emails(self, user_id: int, project_id: int) -> List[EmailProjectMapping]:
        """Get all emails for a project"""
        return self.db.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.project_id == project_id,
                self.model.is_active == True
            )
        ).order_by(self.model.created_at.desc()).all()
    
    def remove_email_from_project(self, user_id: int, project_id: int, email_id: str) -> bool:
        """Remove email from project (deactivate mapping)"""
        mapping = self.db.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.project_id == project_id,
                self.model.email_id == email_id
            )
        ).first()
        
        if mapping:
            mapping.is_active = False
            self.db.commit()
            return True
        return False
    
    def get_email_count_by_project(self, user_id: int) -> Dict[int, int]:
        """Get email count per project"""
        results = self.db.query(
            self.model.project_id,
            func.count(self.model.id).label('count')
        ).filter(
            and_(
                self.model.user_id == user_id,
                self.model.is_active == True
            )
        ).group_by(self.model.project_id).all()
        
        return {project_id: count for project_id, count in results}

