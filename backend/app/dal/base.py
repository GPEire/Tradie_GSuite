"""
Data Access Layer (DAL)
TASK-038: Abstract database operations
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import Base
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAL(Generic[ModelType]):
    """Base Data Access Layer for database operations"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize DAL
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get record by field values"""
        return self.db.query(self.model).filter_by(**kwargs).first()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0, **filters) -> List[ModelType]:
        """Get all records with optional filters"""
        query = self.db.query(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def create(self, **kwargs) -> ModelType:
        """Create new record"""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update record by ID"""
        instance = self.get(id)
        if not instance:
            return None
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete record by ID"""
        instance = self.get(id)
        if not instance:
            return False
        
        self.db.delete(instance)
        self.db.commit()
        return True
    
    def count(self, **filters) -> int:
        """Count records matching filters"""
        query = self.db.query(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def exists(self, **filters) -> bool:
        """Check if record exists"""
        return self.count(**filters) > 0

