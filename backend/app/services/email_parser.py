"""
Email Parser Service
Parse Gmail API message format into structured email data
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from email.utils import parsedate_to_datetime
import base64
import re
from bs4 import BeautifulSoup
import html2text
import logging

logger = logging.getLogger(__name__)


class EmailParser:
    """Parser for Gmail API message format"""
    
    @staticmethod
    def extract_header(headers: List[Dict[str, str]], name: str) -> Optional[str]:
        """Extract header value by name (case-insensitive)"""
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value')
        return None
    
    @staticmethod
    def decode_body(data: str, encoding: str = 'base64') -> str:
        """Decode email body data"""
        try:
            if encoding == 'base64':
                decoded = base64.urlsafe_b64decode(data)
                return decoded.decode('utf-8', errors='ignore')
            elif encoding == 'base64url':
                decoded = base64.urlsafe_b64decode(data + '==')
                return decoded.decode('utf-8', errors='ignore')
            else:
                return data
        except Exception as e:
            logger.warning(f"Failed to decode body: {e}")
            return data
    
    @staticmethod
    def extract_body_from_payload(payload: Dict[str, Any], body_text: str = "", body_html: str = "") -> tuple[str, str]:
        """Recursively extract text and HTML body from payload"""
        # Handle multipart messages
        if payload.get('mimeType') == 'multipart/alternative' or payload.get('mimeType') == 'multipart/mixed':
            parts = payload.get('parts', [])
            for part in parts:
                body_text, body_html = EmailParser.extract_body_from_payload(part, body_text, body_html)
        
        # Handle single part messages
        elif payload.get('mimeType') == 'text/plain':
            body_data = payload.get('body', {}).get('data')
            if body_data:
                decoded = EmailParser.decode_body(body_data, payload.get('body', {}).get('encoding', 'base64'))
                body_text = decoded if not body_text else body_text
        
        elif payload.get('mimeType') == 'text/html':
            body_data = payload.get('body', {}).get('data')
            if body_data:
                decoded = EmailParser.decode_body(body_data, payload.get('body', {}).get('encoding', 'base64'))
                body_html = decoded if not body_html else body_html
        
        # Handle nested parts
        parts = payload.get('parts', [])
        if parts:
            for part in parts:
                body_text, body_html = EmailParser.extract_body_from_payload(part, body_text, body_html)
        
        return body_text, body_html
    
    @staticmethod
    def html_to_text(html: str) -> str:
        """Convert HTML to plain text"""
        if not html:
            return ""
        try:
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.body_width = 0
            return h.handle(html).strip()
        except Exception as e:
            logger.warning(f"Failed to convert HTML to text: {e}")
            # Fallback: use BeautifulSoup
            try:
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text().strip()
            except:
                return html
    
    @staticmethod
    def parse_email_address(address_string: str) -> Dict[str, str]:
        """Parse email address string into name and email"""
        if not address_string:
            return {"name": "", "email": ""}
        
        # Pattern: "Name <email@domain.com>" or "email@domain.com"
        pattern = r'^(.+?)\s*<(.+?)>$|^(.+?)$'
        match = re.match(pattern, address_string.strip())
        
        if match:
            if match.group(1) and match.group(2):
                return {"name": match.group(1).strip('"'), "email": match.group(2)}
            elif match.group(3):
                email = match.group(3).strip()
                return {"name": "", "email": email}
        
        return {"name": "", "email": address_string}
    
    @staticmethod
    def parse_addresses(address_string: Optional[str]) -> List[Dict[str, str]]:
        """Parse comma-separated email addresses"""
        if not address_string:
            return []
        
        addresses = []
        # Split by comma, but respect quoted names
        parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', address_string)
        for part in parts:
            parsed = EmailParser.parse_email_address(part.strip())
            if parsed["email"]:
                addresses.append(parsed)
        
        return addresses
    
    @staticmethod
    def parse_date(date_string: Optional[str]) -> Optional[datetime]:
        """Parse email date string to datetime"""
        if not date_string:
            return None
        
        try:
            return parsedate_to_datetime(date_string)
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_string}': {e}")
            return None
    
    @staticmethod
    def extract_attachments(payload: Dict[str, Any], attachments: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Extract attachment information from payload"""
        if attachments is None:
            attachments = []
        
        # Check if this part is an attachment
        filename = payload.get('filename')
        if filename:
            body = payload.get('body', {})
            attachment = {
                "filename": filename,
                "mime_type": payload.get('mimeType'),
                "size": body.get('size', 0),
                "attachment_id": body.get('attachmentId')
            }
            attachments.append(attachment)
        
        # Recursively check parts
        parts = payload.get('parts', [])
        for part in parts:
            EmailParser.extract_attachments(part, attachments)
        
        return attachments
    
    @staticmethod
    def parse_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail API message format into structured email data"""
        try:
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract headers
            subject = EmailParser.extract_header(headers, 'Subject') or ""
            from_header = EmailParser.extract_header(headers, 'From') or ""
            to_header = EmailParser.extract_header(headers, 'To') or ""
            cc_header = EmailParser.extract_header(headers, 'Cc')
            bcc_header = EmailParser.extract_header(headers, 'Bcc')
            date_header = EmailParser.extract_header(headers, 'Date')
            reply_to = EmailParser.extract_header(headers, 'Reply-To')
            in_reply_to = EmailParser.extract_header(headers, 'In-Reply-To')
            references = EmailParser.extract_header(headers, 'References')
            
            # Parse addresses
            from_address = EmailParser.parse_email_address(from_header)
            to_addresses = EmailParser.parse_addresses(to_header)
            cc_addresses = EmailParser.parse_addresses(cc_header)
            bcc_addresses = EmailParser.parse_addresses(bcc_header)
            
            # Parse date
            date = EmailParser.parse_date(date_header)
            
            # Extract body
            body_text, body_html = EmailParser.extract_body_from_payload(payload)
            
            # If no text body but HTML exists, convert HTML to text
            if not body_text and body_html:
                body_text = EmailParser.html_to_text(body_html)
            
            # Extract attachments
            attachments = EmailParser.extract_attachments(payload)
            
            # Build parsed email
            parsed_email = {
                "id": message.get('id'),
                "thread_id": message.get('threadId'),
                "label_ids": message.get('labelIds', []),
                "snippet": message.get('snippet', ''),
                "subject": subject,
                "from": from_address,
                "to": to_addresses,
                "cc": cc_addresses,
                "bcc": bcc_addresses,
                "reply_to": EmailParser.parse_email_address(reply_to) if reply_to else None,
                "date": date.isoformat() if date else None,
                "internal_date": message.get('internalDate'),
                "body_text": body_text,
                "body_html": body_html,
                "attachments": attachments,
                "size_estimate": message.get('sizeEstimate', 0),
                "history_id": message.get('historyId'),
                "in_reply_to": in_reply_to,
                "references": references
            }
            
            return parsed_email
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            raise ValueError(f"Failed to parse email message: {str(e)}")


def parse_gmail_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to parse Gmail message"""
    return EmailParser.parse_message(message)

