"""
Tests for AI Prompt Engineering
Tests for prompt generation and structure
"""

import pytest
from app.services.prompts import PromptType, get_prompt, ProjectDetectionPrompts


class TestPromptGeneration:
    """Test prompt generation functions"""
    
    def test_project_name_extraction_prompt(self):
        """Test project name extraction prompt generation"""
        prompt = get_prompt(
            PromptType.PROJECT_NAME_EXTRACTION,
            email_content="We need to discuss the kitchen renovation at 123 Main St.",
            email_subject="Kitchen Renovation - Main Street",
            sender_email="client@example.com"
        )
        
        assert "project name" in prompt.lower()
        assert "extract" in prompt.lower()
        assert "JSON" in prompt
        assert "kitchen renovation" in prompt or "Main Street" in prompt
    
    def test_address_detection_prompt(self):
        """Test address detection prompt generation"""
        prompt = get_prompt(
            PromptType.ADDRESS_DETECTION,
            email_content="The property is at 456 Oak Avenue, Melbourne VIC 3000",
            email_subject="Property Location"
        )
        
        assert "address" in prompt.lower()
        assert "australian" in prompt.lower()
        assert "JSON" in prompt
    
    def test_job_number_detection_prompt(self):
        """Test job number detection prompt generation"""
        prompt = get_prompt(
            PromptType.JOB_NUMBER_DETECTION,
            email_content="Job #12345 is ready for inspection",
            email_subject="Job #12345 Update"
        )
        
        assert "job number" in prompt.lower()
        assert "reference" in prompt.lower()
        assert "JSON" in prompt
    
    def test_content_similarity_prompt(self):
        """Test content similarity prompt generation"""
        prompt = get_prompt(
            PromptType.CONTENT_SIMILARITY,
            email1_content={"subject": "Project Update", "body_text": "Kitchen renovation progress"},
            email2_content={"subject": "Kitchen Project", "body_text": "Renovation update"}
        )
        
        assert "same project" in prompt.lower()
        assert "compare" in prompt.lower()
        assert "JSON" in prompt
    
    def test_entity_extraction_prompt(self):
        """Test entity extraction prompt generation"""
        prompt = get_prompt(
            PromptType.ENTITY_EXTRACTION,
            email_content="Project: Smith Residence Renovation at 789 Park St, Sydney NSW 2000. Job #67890",
            email_subject="Smith Residence Update",
            sender_email="smith@example.com",
            sender_name="John Smith"
        )
        
        assert "extract" in prompt.lower()
        assert "comprehensive" in prompt.lower() or "structured" in prompt.lower()
        assert "JSON" in prompt


class TestProjectDetectionPrompts:
    """Test ProjectDetectionPrompts class"""
    
    def test_get_project_name_extraction_prompt(self):
        """Test project name extraction prompt"""
        prompts = ProjectDetectionPrompts()
        result = prompts.get_project_name_extraction_prompt(
            email_content="Kitchen renovation project",
            email_subject="Kitchen Project",
            sender_email="test@example.com"
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "project name" in result.lower()
    
    def test_get_address_detection_prompt(self):
        """Test address detection prompt"""
        prompts = ProjectDetectionPrompts()
        result = prompts.get_address_detection_prompt(
            email_content="123 Main St, Melbourne",
            email_subject="Address"
        )
        
        assert isinstance(result, str)
        assert "address" in result.lower()
    
    def test_get_batch_grouping_prompt(self):
        """Test batch grouping prompt"""
        prompts = ProjectDetectionPrompts()
        emails = [
            {"subject": "Project A", "from": "client@example.com", "body_text": "Email 1"},
            {"subject": "Project B", "from": "client@example.com", "body_text": "Email 2"}
        ]
        result = prompts.get_batch_project_grouping_prompt(emails=emails)
        
        assert isinstance(result, str)
        assert "group" in result.lower()
        assert "project" in result.lower()

