"""
Email Scanning Configuration Service
Manage scanning filters and configuration
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import logging
from app.models.user import User
from app.models.scan_config import ScanConfiguration

logger = logging.getLogger(__name__)


class ScanConfigurationService:
    """Service for managing email scanning configuration"""
    
    def __init__(self, user: User, db: Session):
        """Initialize scan configuration service"""
        self.user = user
        self.db = db
    
    def get_configuration(self) -> ScanConfiguration:
        """Get or create scan configuration"""
        config = self.db.query(ScanConfiguration).filter(
            ScanConfiguration.user_id == self.user.id
        ).first()
        
        if not config:
            config = ScanConfiguration(
                user_id=self.user.id,
                is_enabled=True,
                scan_frequency="realtime"
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def update_configuration(self, **kwargs) -> ScanConfiguration:
        """Update scan configuration"""
        config = self.get_configuration()
        
        # Update allowed fields
        allowed_fields = [
            'is_enabled', 'scan_frequency', 'included_labels', 'excluded_labels',
            'label_filter_action', 'excluded_senders', 'excluded_domains',
            'scan_retroactive', 'retroactive_date_start', 'retroactive_date_end',
            'scan_options'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(config, field, value)
        
        self.db.commit()
        self.db.refresh(config)
        
        logger.info(f"Updated scan configuration for user {self.user.id}")
        
        return config
    
    def set_label_filters(self, included_labels: Optional[List[str]] = None,
                         excluded_labels: Optional[List[str]] = None,
                         filter_action: str = "include") -> ScanConfiguration:
        """Set label/folder filters"""
        config = self.get_configuration()
        config.included_labels = included_labels
        config.excluded_labels = excluded_labels
        config.label_filter_action = filter_action
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def add_excluded_sender(self, email: str) -> ScanConfiguration:
        """Add sender to exclusion list"""
        config = self.get_configuration()
        excluded = config.excluded_senders or []
        if email not in excluded:
            excluded.append(email)
            config.excluded_senders = excluded
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def remove_excluded_sender(self, email: str) -> ScanConfiguration:
        """Remove sender from exclusion list"""
        config = self.get_configuration()
        excluded = config.excluded_senders or []
        if email in excluded:
            excluded.remove(email)
            config.excluded_senders = excluded
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def add_excluded_domain(self, domain: str) -> ScanConfiguration:
        """Add domain to exclusion list"""
        config = self.get_configuration()
        excluded = config.excluded_domains or []
        if domain not in excluded:
            excluded.append(domain)
            config.excluded_domains = excluded
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def remove_excluded_domain(self, domain: str) -> ScanConfiguration:
        """Remove domain from exclusion list"""
        config = self.get_configuration()
        excluded = config.excluded_domains or []
        if domain in excluded:
            excluded.remove(domain)
            config.excluded_domains = excluded
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def set_scan_frequency(self, frequency: str) -> ScanConfiguration:
        """Set scanning frequency"""
        valid_frequencies = ["realtime", "hourly", "daily", "weekly", "manual"]
        if frequency not in valid_frequencies:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
        
        config = self.get_configuration()
        config.scan_frequency = frequency
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def enable_scanning(self) -> ScanConfiguration:
        """Enable email scanning"""
        config = self.get_configuration()
        config.is_enabled = True
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def disable_scanning(self) -> ScanConfiguration:
        """Disable email scanning"""
        config = self.get_configuration()
        config.is_enabled = False
        self.db.commit()
        self.db.refresh(config)
        return config


def get_scan_configuration_service(user: User, db: Session) -> ScanConfigurationService:
    """Factory function to create scan configuration service"""
    return ScanConfigurationService(user, db)

