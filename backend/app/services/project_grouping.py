"""
Project Grouping Logic
Group emails by project using entity extraction and similarity analysis
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import logging
from collections import defaultdict
from app.services.ai import AIService, AIServiceError
from app.services.entity_extraction import EntityExtractionService, get_entity_extraction_service
from app.services.similarity import SimilarityService, get_similarity_service

logger = logging.getLogger(__name__)


class ProjectGroupingService:
    """Service for grouping emails into projects"""
    
    def __init__(self, ai_service: AIService):
        """Initialize project grouping service"""
        self.ai_service = ai_service
        self.entity_extractor = get_entity_extraction_service(ai_service)
        self.similarity_service = get_similarity_service(ai_service)
    
    def group_emails(self, emails: List[Dict[str, Any]], 
                    existing_projects: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Group emails into projects
        
        Args:
            emails: List of parsed email data
            existing_projects: Optional list of existing projects
        
        Returns:
            Grouped projects with email assignments
        """
        try:
            # Use AI batch grouping for initial grouping
            email_data_for_ai = [
                {
                    'id': email.get('id'),
                    'subject': email.get('subject', ''),
                    'from': email.get('from', {}).get('email', '') if isinstance(email.get('from'), dict) else str(email.get('from', '')),
                    'body_text': email.get('body_text', '') or email.get('snippet', ''),
                    'date': email.get('date', '')
                }
                for email in emails
            ]
            
            ai_result = self.ai_service.group_emails(
                emails=email_data_for_ai,
                existing_projects=existing_projects
            )
            
            # Process AI results and refine groups
            project_groups = self._refine_groups(emails, ai_result, existing_projects)
            
            return {
                'project_groups': project_groups,
                'unmatched_emails': ai_result.get('unmatched_emails', []),
                'total_emails': len(emails),
                'total_projects': len(project_groups)
            }
            
        except AIServiceError as e:
            logger.error(f"AI service error during grouping: {e}")
            raise
        except Exception as e:
            logger.error(f"Error grouping emails: {e}")
            raise
    
    def _refine_groups(self, emails: List[Dict[str, Any]], 
                      ai_result: Dict[str, Any],
                      existing_projects: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Refine AI-generated groups with additional logic"""
        
        email_map = {email.get('id'): email for email in emails}
        project_groups = []
        
        for group in ai_result.get('project_groups', []):
            email_ids = group.get('email_ids', [])
            if not email_ids:
                continue
            
            # Get actual email objects
            group_emails = [email_map.get(eid) for eid in email_ids if email_map.get(eid)]
            
            if not group_emails:
                continue
            
            # Extract entities for the group
            group_entities = self._extract_group_entities(group_emails)
            
            # Handle thread-based grouping
            thread_groups = self._group_by_thread(group_emails)
            
            # Merge thread groups if they're the same project
            merged_group = self._merge_thread_groups(thread_groups, group_entities)
            
            project_groups.append({
                'project_id': group.get('project_id', f"project_{len(project_groups)}"),
                'project_name': group.get('project_name', merged_group.get('project_name', 'Unnamed Project')),
                'email_ids': email_ids,
                'emails': group_emails,
                'confidence': group.get('confidence', 0.0),
                'key_indicators': group.get('key_indicators', []),
                'address': group.get('address') or group_entities.get('address'),
                'client': group.get('client') or group_entities.get('client'),
                'project_type': group.get('project_type') or group_entities.get('project_type'),
                'job_numbers': group_entities.get('job_numbers', []),
                'thread_ids': list(set([e.get('thread_id') for e in group_emails if e.get('thread_id')]))
            })
        
        return project_groups
    
    def _extract_group_entities(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common entities from a group of emails"""
        all_addresses = []
        all_job_numbers = []
        all_clients = []
        project_types = []
        
        for email in emails:
            try:
                entities = self.entity_extractor.extract_from_email(email)
                
                # Collect addresses
                if entities.get('address') and entities['address'].get('full_address'):
                    all_addresses.append(entities['address']['full_address'])
                
                # Collect job numbers
                all_job_numbers.extend(entities.get('job_numbers', []))
                
                # Collect client info
                if entities.get('client_info') and entities['client_info'].get('name'):
                    all_clients.append(entities['client_info']['name'])
                
                # Collect project types
                if entities.get('project_type'):
                    project_types.append(entities['project_type'])
                    
            except Exception as e:
                logger.warning(f"Error extracting entities from email {email.get('id')}: {e}")
                continue
        
        # Find most common values
        from collections import Counter
        
        return {
            'address': all_addresses[0] if all_addresses else None,
            'job_numbers': list(set(all_job_numbers)),
            'client': Counter(all_clients).most_common(1)[0][0] if all_clients else None,
            'project_type': Counter(project_types).most_common(1)[0][0] if project_types else None
        }
    
    def _group_by_thread(self, emails: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group emails by thread"""
        thread_map = defaultdict(list)
        
        for email in emails:
            thread_id = email.get('thread_id')
            if thread_id:
                thread_map[thread_id].append(email)
            else:
                # Emails without thread ID are their own group
                thread_map[f"solo_{email.get('id')}"].append(email)
        
        return list(thread_map.values())
    
    def _merge_thread_groups(self, thread_groups: List[List[Dict[str, Any]]], 
                           group_entities: Dict[str, Any]) -> Dict[str, Any]:
        """Merge thread groups if they belong to the same project"""
        if len(thread_groups) <= 1:
            return {
                'project_name': group_entities.get('project_name'),
                'threads': thread_groups
            }
        
        # Check if threads are related (same project)
        merged_threads = [thread_groups[0]]
        
        for thread in thread_groups[1:]:
            # Check similarity with existing merged threads
            is_related = False
            
            for merged_thread in merged_threads:
                # Compare representative emails
                if thread and merged_thread:
                    try:
                        comparison = self.similarity_service.compare_emails(
                            thread[0], merged_thread[0]
                        )
                        
                        if comparison.get('same_project', False) and comparison.get('confidence', 0.0) >= 0.7:
                            merged_thread.extend(thread)
                            is_related = True
                            break
                    except Exception as e:
                        logger.warning(f"Error comparing threads: {e}")
            
            if not is_related:
                merged_threads.append(thread)
        
        return {
            'project_name': group_entities.get('project_name'),
            'threads': merged_threads
        }
    
    def handle_multi_sender_grouping(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group emails from multiple senders that belong to the same project
        
        Uses address, job number, and project name matching
        """
        # Extract entities for all emails
        email_entities = []
        for email in emails:
            try:
                entities = self.entity_extractor.extract_from_email(email)
                entities['email_id'] = email.get('id')
                entities['email'] = email
                email_entities.append(entities)
            except Exception as e:
                logger.warning(f"Error extracting entities for multi-sender grouping: {e}")
                continue
        
        # Group by address (strongest indicator)
        address_groups = defaultdict(list)
        for entity in email_entities:
            address = entity.get('address', {}).get('full_address') if isinstance(entity.get('address'), dict) else None
            if address:
                address_groups[address].append(entity)
        
        # Group by job number (secondary indicator)
        job_number_groups = defaultdict(list)
        for entity in email_entities:
            job_numbers = entity.get('job_numbers', [])
            for job_num in job_numbers:
                if job_num:
                    job_number_groups[job_num].append(entity)
        
        # Group by project name (tertiary indicator)
        project_name_groups = defaultdict(list)
        for entity in email_entities:
            project_name = entity.get('project_name')
            if project_name:
                project_name_groups[project_name].append(entity)
        
        # Merge groups intelligently
        merged_groups = self._merge_multi_sender_groups(
            address_groups, job_number_groups, project_name_groups, email_entities
        )
        
        return merged_groups
    
    def _merge_multi_sender_groups(self, address_groups: Dict, job_number_groups: Dict,
                                   project_name_groups: Dict, all_entities: List[Dict]) -> List[Dict[str, Any]]:
        """Merge multi-sender groups using priority: address > job number > project name"""
        final_groups = []
        processed_emails = set()
        
        # Process by address (highest priority)
        for address, entities in address_groups.items():
            if len(entities) > 1:
                email_ids = [e['email_id'] for e in entities]
                processed_emails.update(email_ids)
                
                final_groups.append({
                    'project_name': entities[0].get('project_name', f"Project at {address}"),
                    'address': address,
                    'email_ids': email_ids,
                    'senders': list(set([e['email'].get('from', {}).get('email', '') if isinstance(e['email'].get('from'), dict) else '' for e in entities])),
                    'confidence': 0.9  # High confidence for address match
                })
        
        # Process by job number (medium priority)
        for job_number, entities in job_number_groups.items():
            if len(entities) > 1:
                # Skip if already processed
                email_ids = [e['email_id'] for e in entities if e['email_id'] not in processed_emails]
                if email_ids:
                    processed_emails.update(email_ids)
                    
                    final_groups.append({
                        'project_name': entities[0].get('project_name', f"Project {job_number}"),
                        'job_number': job_number,
                        'email_ids': email_ids,
                        'senders': list(set([e['email'].get('from', {}).get('email', '') if isinstance(e['email'].get('from'), dict) else '' for e in entities])),
                        'confidence': 0.8  # Medium-high confidence for job number match
                    })
        
        # Process by project name (lower priority)
        for project_name, entities in project_name_groups.items():
            if len(entities) > 1:
                email_ids = [e['email_id'] for e in entities if e['email_id'] not in processed_emails]
                if email_ids:
                    processed_emails.update(email_ids)
                    
                    final_groups.append({
                        'project_name': project_name,
                        'email_ids': email_ids,
                        'senders': list(set([e['email'].get('from', {}).get('email', '') if isinstance(e['email'].get('from'), dict) else '' for e in entities])),
                        'confidence': 0.7  # Medium confidence for project name match
                    })
        
        # Handle unmatched emails
        unmatched = [e for e in all_entities if e['email_id'] not in processed_emails]
        for entity in unmatched:
            final_groups.append({
                'project_name': entity.get('project_name', 'Unnamed Project'),
                'email_ids': [entity['email_id']],
                'senders': [entity['email'].get('from', {}).get('email', '') if isinstance(entity['email'].get('from'), dict) else ''],
                'confidence': entity.get('confidence', 0.5)
            })
        
        return final_groups
    
    def handle_edge_cases(self, emails: List[Dict[str, Any]], 
                         project_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle edge cases:
        - Multiple projects mentioned in one email
        - Ambiguous emails (low confidence)
        - Emails with no clear project identifier
        """
        refined_groups = []
        
        for group in project_groups:
            # Check for multiple projects in group
            if self._has_multiple_projects(group):
                # Split into separate groups
                split_groups = self._split_multiple_projects(group)
                refined_groups.extend(split_groups)
            else:
                refined_groups.append(group)
        
        # Handle ambiguous emails (low confidence)
        ambiguous = [g for g in refined_groups if g.get('confidence', 0.0) < 0.5]
        for group in ambiguous:
            group['flags'] = group.get('flags', [])
            group['flags'].append('low_confidence')
            group['needs_review'] = True
        
        return refined_groups
    
    def _has_multiple_projects(self, group: Dict[str, Any]) -> bool:
        """Check if a group contains emails about multiple projects"""
        project_names = set()
        
        for email in group.get('emails', []):
            try:
                entities = self.entity_extractor.extract_from_email(email)
                project_name = entities.get('project_name')
                if project_name:
                    project_names.add(project_name)
            except Exception:
                continue
        
        return len(project_names) > 1
    
    def _split_multiple_projects(self, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a group that contains multiple projects"""
        project_email_map = defaultdict(list)
        
        for email in group.get('emails', []):
            try:
                entities = self.entity_extractor.extract_from_email(email)
                project_name = entities.get('project_name', 'Unknown')
                project_email_map[project_name].append(email)
            except Exception:
                project_email_map['Unknown'].append(email)
        
        split_groups = []
        for project_name, emails in project_email_map.items():
            split_groups.append({
                **group,
                'project_name': project_name,
                'emails': emails,
                'email_ids': [e.get('id') for e in emails],
                'flags': ['split_from_multiple_projects']
            })
        
        return split_groups


def get_project_grouping_service(ai_service: AIService) -> ProjectGroupingService:
    """Factory function to create project grouping service"""
    return ProjectGroupingService(ai_service)

