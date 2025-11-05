"""
Attachment Processing Service
Extract attachment metadata, parse filenames, aggregate by project, Google Drive integration
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import re
import logging
from app.models.attachment import EmailAttachment, AttachmentProjectMapping
from app.models.user import User
from app.services.gmail import GmailService, get_gmail_service
from app.services.ai import AIService, get_ai_service
from app.services.email_parser import parse_gmail_message

logger = logging.getLogger(__name__)


class AttachmentProcessingService:
    """Service for processing email attachments"""
    
    def __init__(self, user: User, db: Session):
        """Initialize attachment processing service"""
        self.user = user
        self.db = db
        self.gmail_service = get_gmail_service(user, db)
        self.ai_service = get_ai_service()
    
    def extract_attachment_metadata(self, email_id: str) -> List[Dict[str, Any]]:
        """
        Extract attachment metadata from email
        
        Args:
            email_id: Gmail message ID
        
        Returns:
            List of attachment metadata
        """
        try:
            # Fetch email
            message = self.gmail_service.get_message(email_id, format="full")
            parsed_email = parse_gmail_message(message)
            
            attachments = parsed_email.get('attachments', [])
            metadata_list = []
            
            for attachment in attachments:
                filename = attachment.get('filename', '')
                
                # Analyze filename for project indicators
                project_indicators = self._parse_filename_for_project(filename)
                
                # Determine file type category
                file_type = self._categorize_file_type(attachment.get('mime_type', ''), filename)
                
                metadata = {
                    "attachment_id": attachment.get('attachment_id'),
                    "filename": filename,
                    "mime_type": attachment.get('mime_type'),
                    "size": attachment.get('size', 0),
                    "file_extension": self._get_file_extension(filename),
                    "file_type_category": file_type,
                    "project_indicators": project_indicators
                }
                
                metadata_list.append(metadata)
                
                # Store in database
                self._store_attachment_metadata(
                    email_id=email_id,
                    thread_id=parsed_email.get('thread_id'),
                    attachment_data=attachment,
                    metadata=metadata
                )
            
            return metadata_list
            
        except Exception as e:
            logger.error(f"Error extracting attachment metadata for email {email_id}: {e}")
            raise
    
    def _parse_filename_for_project(self, filename: str) -> Dict[str, Any]:
        """
        Parse attachment filename for project indicators
        
        Common patterns:
        - Project names in filename
        - Job numbers (JOB-123, #456)
        - Addresses (123_Main_St.pdf)
        - Dates (2024-01-15_Project.pdf)
        """
        indicators = {
            "project_name": None,
            "job_number": None,
            "address": None,
            "date": None,
            "keywords": []
        }
        
        if not filename:
            return indicators
        
        # Extract job numbers
        job_patterns = [
            r'[Jj]ob[_\s-]*(?:#|No\.?|Number)?\s*(\d+)',
            r'[Qq]uote[_\s-]*(?:#|No\.?|Number)?\s*(\d+)',
            r'[Rr]ef[_\s-]*(?:#|No\.?|Number)?\s*([A-Z0-9-]+)',
            r'#(\d+)',
            r'JOB-(\d+)',
            r'Q-(\d+)'
        ]
        
        for pattern in job_patterns:
            match = re.search(pattern, filename)
            if match:
                indicators["job_number"] = match.group(1)
                break
        
        # Extract potential project names (words that might be project names)
        # Look for capitalized words or words separated by underscores/dashes
        project_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Capitalized words
            r'([A-Z][a-z]+(?:_[A-Z][a-z]+)+)',  # Underscore separated
            r'([A-Z][a-z]+(?:-[A-Z][a-z]+)+)'  # Dash separated
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, filename)
            if matches:
                # Filter out common non-project words
                common_words = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png', 'dwg', 'plan', 'drawing'}
                potential_projects = [m for m in matches if m.lower() not in common_words]
                if potential_projects:
                    indicators["project_name"] = potential_projects[0]
                    break
        
        # Extract dates
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY
            r'(\d{4}_\d{2}_\d{2})',  # YYYY_MM_DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                indicators["date"] = match.group(1)
                break
        
        # Extract keywords
        keywords = re.findall(r'\b[A-Z][a-z]+\b', filename)
        indicators["keywords"] = keywords[:10]  # Limit to 10 keywords
        
        return indicators
    
    def _categorize_file_type(self, mime_type: str, filename: str) -> str:
        """Categorize file type"""
        if not mime_type and not filename:
            return "unknown"
        
        mime_lower = mime_type.lower() if mime_type else ""
        filename_lower = filename.lower() if filename else ""
        
        # Document types
        if any(x in mime_lower or any(ext in filename_lower for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']) 
               for x in ['pdf', 'document', 'text', 'msword']):
            return "document"
        
        # Spreadsheet types
        if any(x in mime_lower or any(ext in filename_lower for ext in ['.xls', '.xlsx', '.csv']) 
               for x in ['spreadsheet', 'excel', 'csv']):
            return "spreadsheet"
        
        # Image types
        if any(x in mime_lower or any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']) 
               for x in ['image']):
            return "image"
        
        # CAD/Drawing types
        if any(ext in filename_lower for ext in ['.dwg', '.dxf', '.dwf', '.cad']):
            return "drawing"
        
        # Archive types
        if any(x in mime_lower or any(ext in filename_lower for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']) 
               for x in ['zip', 'archive', 'compressed']):
            return "archive"
        
        return "other"
    
    def _get_file_extension(self, filename: str) -> Optional[str]:
        """Get file extension from filename"""
        if not filename:
            return None
        
        parts = filename.rsplit('.', 1)
        return parts[1].lower() if len(parts) > 1 else None
    
    def _store_attachment_metadata(self, email_id: str, thread_id: Optional[str],
                                  attachment_data: Dict[str, Any], metadata: Dict[str, Any]):
        """Store attachment metadata in database"""
        try:
            attachment = EmailAttachment(
                user_id=self.user.id,
                email_id=email_id,
                thread_id=thread_id,
                attachment_id=attachment_data.get('attachment_id', ''),
                filename=attachment_data.get('filename', ''),
                mime_type=attachment_data.get('mime_type'),
                size=attachment_data.get('size', 0),
                file_extension=metadata.get('file_extension'),
                file_type_category=metadata.get('file_type_category'),
                project_indicators=metadata.get('project_indicators')
            )
            
            self.db.add(attachment)
            self.db.commit()
            self.db.refresh(attachment)
            
            return attachment
            
        except Exception as e:
            logger.warning(f"Error storing attachment metadata: {e}")
            self.db.rollback()
            return None
    
    def aggregate_attachments_by_project(self, project_id: str) -> List[EmailAttachment]:
        """Get all attachments for a project"""
        attachments = self.db.query(EmailAttachment).filter(
            EmailAttachment.project_id == project_id,
            EmailAttachment.user_id == self.user.id
        ).all()
        
        return attachments
    
    def associate_attachment_with_project(self, attachment_id: int, project_id: str,
                                        confidence: Optional[float] = None,
                                        method: str = "manual") -> AttachmentProjectMapping:
        """Associate attachment with project"""
        # Update attachment
        attachment = self.db.query(EmailAttachment).filter(
            EmailAttachment.id == attachment_id,
            EmailAttachment.user_id == self.user.id
        ).first()
        
        if attachment:
            attachment.project_id = project_id
            self.db.commit()
        
        # Create mapping
        mapping = AttachmentProjectMapping(
            attachment_id=attachment_id,
            project_id=project_id,
            confidence=str(confidence) if confidence else None,
            association_method=method
        )
        
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        
        return mapping
    
    def upload_to_drive(self, email_id: str, attachment_id: str,
                       drive_folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload attachment to Google Drive
        
        Args:
            email_id: Gmail message ID
            attachment_id: Gmail attachment ID
            drive_folder_id: Optional Google Drive folder ID
        
        Returns:
            Drive file information
        """
        try:
            # Get attachment data from Gmail
            attachment = self.gmail_service.service.users().messages().attachments().get(
                userId='me',
                messageId=email_id,
                id=attachment_id
            ).execute()
            
            # Decode attachment data
            import base64
            file_data = base64.urlsafe_b64decode(attachment['data'])
            
            # Get attachment metadata
            message = self.gmail_service.get_message(email_id, format="full")
            parsed_email = parse_gmail_message(message)
            
            attachment_info = next(
                (a for a in parsed_email.get('attachments', []) 
                 if a.get('attachment_id') == attachment_id),
                None
            )
            
            if not attachment_info:
                raise ValueError(f"Attachment {attachment_id} not found in email")
            
            filename = attachment_info.get('filename', 'attachment')
            
            # TODO: Implement Google Drive API upload
            # For now, return placeholder
            # In production, this would:
            # 1. Create Drive API client
            # 2. Upload file to Drive
            # 3. Set folder if provided
            # 4. Return file ID and URL
            
            drive_file_id = f"drive_{attachment_id}"  # Placeholder
            drive_url = f"https://drive.google.com/file/d/{drive_file_id}"  # Placeholder
            
            # Update attachment record
            db_attachment = self.db.query(EmailAttachment).filter(
                EmailAttachment.attachment_id == attachment_id,
                EmailAttachment.email_id == email_id
            ).first()
            
            if db_attachment:
                db_attachment.drive_file_id = drive_file_id
                db_attachment.drive_url = drive_url
                db_attachment.is_uploaded_to_drive = True
                self.db.commit()
            
            return {
                "drive_file_id": drive_file_id,
                "drive_url": drive_url,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error uploading attachment to Drive: {e}")
            raise


def get_attachment_processing_service(user: User, db: Session) -> AttachmentProcessingService:
    """Factory function to create attachment processing service"""
    return AttachmentProcessingService(user, db)

