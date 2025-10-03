"""
Tests for the release notes plugin.

This module tests all functions in the release notes plugin tasks.
"""

import pytest
from unittest.mock import Mock, patch
from marketing_project.plugins.release_notes.tasks import (
    analyze_release_type,
    extract_release_metadata,
    validate_release_structure,
    enhance_release_notes_with_ocr,
    route_release_processing
)
from marketing_project.core.models import ReleaseNotesContext, AppContext


class TestAnalyzeReleaseType:
    """Test the analyze_release_type function."""
    
    def test_analyze_major_release(self, sample_release_notes):
        """Test analyzing major release."""
        sample_release_notes.version = "2.0.0"
        sample_release_notes.features = ["New feature 1", "New feature 2", "New feature 3", "New feature 4", "New feature 5", "New feature 6"]
        sample_release_notes.breaking_changes = ["Breaking change 1"]
        
        result = analyze_release_type(sample_release_notes)
        assert result == "major"
    
    def test_analyze_major_release_with_breaking_changes(self, sample_release_notes):
        """Test analyzing major release with breaking changes."""
        sample_release_notes.version = "1.0.0"
        sample_release_notes.features = []
        sample_release_notes.breaking_changes = ["Breaking change 1"]
        
        result = analyze_release_type(sample_release_notes)
        assert result == "major"
    
    def test_analyze_minor_release(self, sample_release_notes):
        """Test analyzing minor release."""
        sample_release_notes.version = "1.5.0"
        sample_release_notes.features = ["New feature 1", "New feature 2"]
        sample_release_notes.breaking_changes = []
        
        result = analyze_release_type(sample_release_notes)
        assert result == "minor"
    
    def test_analyze_patch_release(self, sample_release_notes):
        """Test analyzing patch release."""
        sample_release_notes.version = "1.0.3"
        sample_release_notes.changes = ["Bug fix 1", "Bug fix 2"]
        sample_release_notes.features = []
        sample_release_notes.breaking_changes = []
        
        result = analyze_release_type(sample_release_notes)
        assert result == "patch"
    
    def test_analyze_hotfix_release(self, sample_release_notes):
        """Test analyzing hotfix release."""
        sample_release_notes.version = "1.0.1"
        sample_release_notes.changes = []
        sample_release_notes.features = []
        sample_release_notes.breaking_changes = []
        
        result = analyze_release_type(sample_release_notes)
        assert result == "hotfix"
    
    def test_analyze_release_invalid_version_format(self, sample_release_notes):
        """Test analyzing release with invalid version format."""
        sample_release_notes.version = "invalid-version"
        sample_release_notes.breaking_changes = ["Breaking change"]
        
        result = analyze_release_type(sample_release_notes)
        assert result == "major"  # Should fallback to breaking changes analysis
    
    def test_analyze_release_incomplete_version(self, sample_release_notes):
        """Test analyzing release with incomplete version."""
        sample_release_notes.version = "1.0"
        sample_release_notes.features = ["New feature"]
        sample_release_notes.breaking_changes = []  # Clear breaking changes
        
        result = analyze_release_type(sample_release_notes)
        assert result == "minor"  # Should fallback to features analysis


class TestExtractReleaseMetadata:
    """Test the extract_release_metadata function."""
    
    @patch('marketing_project.plugins.release_notes.tasks.parse_release_notes')
    def test_extract_release_metadata(self, mock_parse, sample_release_notes):
        """Test extracting metadata from release notes."""
        mock_parse.return_value = {
            'version': '2.1.0',
            'release_date': '2024-01-01',
            'changes': ['Parsed change 1', 'Parsed change 2'],
            'breaking_changes': ['Parsed breaking change'],
            'features': ['Parsed feature 1', 'Parsed feature 2'],
            'bug_fixes': ['Parsed bug fix 1', 'Parsed bug fix 2'],
            'cleaned_content': 'Cleaned release notes content'
        }
        
        result = extract_release_metadata(sample_release_notes)
        
        assert isinstance(result, dict)
        assert result['content_type'] == 'release_notes'
        assert result['id'] == sample_release_notes.id
        assert result['title'] == sample_release_notes.title
        assert result['version'] == sample_release_notes.version
        assert result['release_date'] == sample_release_notes.release_date
        assert result['changes_count'] == len(sample_release_notes.changes)
        assert result['breaking_changes_count'] == len(sample_release_notes.breaking_changes)
        assert result['features_count'] == len(sample_release_notes.features)
        assert result['bug_fixes_count'] == len(sample_release_notes.bug_fixes)
        assert result['total_changes'] > 0
        assert result['has_breaking_changes'] is True
        assert result['has_new_features'] is True
        assert 'parsed_changes' in result
        assert 'parsed_features' in result
        assert 'parsed_bug_fixes' in result
        assert 'parsed_breaking_changes' in result
        assert 'cleaned_content' in result
    
    @patch('marketing_project.plugins.release_notes.tasks.parse_release_notes')
    def test_extract_release_metadata_with_parsed_data(self, mock_parse, sample_release_notes):
        """Test extracting metadata with parsed data overriding original."""
        mock_parse.return_value = {
            'version': '2.2.0',
            'release_date': '2024-02-01',
            'changes': ['Different change 1', 'Different change 2'],
            'breaking_changes': ['Different breaking change'],
            'features': ['Different feature 1', 'Different feature 2'],
            'bug_fixes': ['Different bug fix 1'],
            'cleaned_content': 'Different cleaned content'
        }
        
        # Set original values to None to test fallback
        sample_release_notes.version = None
        sample_release_notes.release_date = None
        sample_release_notes.changes = None
        sample_release_notes.breaking_changes = None
        sample_release_notes.features = None
        sample_release_notes.bug_fixes = None
        
        result = extract_release_metadata(sample_release_notes)
        
        assert result['version'] == '2.2.0'
        assert result['release_date'] is None
        assert result['changes_count'] == 2
        assert result['breaking_changes_count'] == 1
        assert result['features_count'] == 2
        assert result['bug_fixes_count'] == 1
        assert result['has_breaking_changes'] is True
        assert result['has_new_features'] is True


class TestValidateReleaseStructure:
    """Test the validate_release_structure function."""
    
    def test_validate_valid_release_notes(self, sample_release_notes):
        """Test validating valid release notes."""
        result = validate_release_structure(sample_release_notes)
        assert result is True
    
    def test_validate_release_notes_missing_id(self, sample_release_notes):
        """Test validating release notes with missing ID."""
        sample_release_notes.id = None
        result = validate_release_structure(sample_release_notes)
        assert result is False
    
    def test_validate_release_notes_missing_title(self, sample_release_notes):
        """Test validating release notes with missing title."""
        sample_release_notes.title = None
        result = validate_release_structure(sample_release_notes)
        assert result is False
    
    def test_validate_release_notes_missing_content(self, sample_release_notes):
        """Test validating release notes with missing content."""
        sample_release_notes.content = None
        result = validate_release_structure(sample_release_notes)
        assert result is False
    
    def test_validate_release_notes_missing_snippet(self, sample_release_notes):
        """Test validating release notes with missing snippet."""
        sample_release_notes.snippet = None
        result = validate_release_structure(sample_release_notes)
        assert result is False
    
    def test_validate_release_notes_missing_version(self, sample_release_notes):
        """Test validating release notes with missing version."""
        sample_release_notes.version = None
        result = validate_release_structure(sample_release_notes)
        assert result is False
    
    def test_validate_release_notes_invalid_version_type(self, sample_release_notes):
        """Test validating release notes with invalid version type."""
        sample_release_notes.version = 123  # Should be string
        result = validate_release_structure(sample_release_notes)
        assert result is False


class TestEnhanceReleaseNotesWithOCR:
    """Test the enhance_release_notes_with_ocr function."""
    
    @patch('marketing_project.plugins.release_notes.tasks.extract_images_from_content')
    @patch('marketing_project.plugins.release_notes.tasks.enhance_content_with_ocr')
    def test_enhance_release_notes_with_ocr_no_images(self, mock_enhance, mock_extract, sample_release_notes):
        """Test enhancing release notes with OCR when no images provided."""
        mock_extract.return_value = []
        mock_enhance.return_value = {
            'enhanced_content': 'Enhanced release notes content',
            'ocr_text': 'OCR text from images',
            'has_screenshots': False,
            'image_count': 0,
            'screenshot_text': 'Screenshot text'
        }
        
        result = enhance_release_notes_with_ocr(sample_release_notes)
        
        assert isinstance(result, dict)
        assert 'original_release_notes' in result
        assert 'enhanced_content' in result
        assert 'ocr_text' in result
        assert 'has_screenshots' in result
        assert 'image_count' in result
        assert 'screenshot_text' in result
        
        assert result['original_release_notes'] == sample_release_notes
        assert result['has_screenshots'] is False
        assert result['image_count'] == 0
    
    @patch('marketing_project.plugins.release_notes.tasks.enhance_content_with_ocr')
    def test_enhance_release_notes_with_ocr_with_images(self, mock_enhance, sample_release_notes):
        """Test enhancing release notes with OCR when images are provided."""
        image_urls = ['https://example.com/screenshot1.png', 'https://example.com/screenshot2.png']
        mock_enhance.return_value = {
            'enhanced_content': 'Enhanced release notes with screenshots',
            'ocr_text': 'OCR text from screenshots',
            'has_screenshots': True,
            'image_count': 2,
            'screenshot_text': 'Screenshot text from images'
        }
        
        result = enhance_release_notes_with_ocr(sample_release_notes, image_urls)
        
        assert result['has_screenshots'] is True
        assert result['image_count'] == 2
        
        # Verify OCR service was called with correct parameters
        mock_enhance.assert_called_once_with(
            sample_release_notes.content,
            'release_notes',
            image_urls=image_urls
        )


class TestRouteReleaseProcessing:
    """Test the route_release_processing function."""
    
    def test_route_major_release(self, sample_app_context_release, sample_available_agents):
        """Test routing major release to appropriate agent."""
        sample_app_context_release.content.version = "3.0.0"
        sample_app_context_release.content.breaking_changes = ["Breaking change"]
        
        result = route_release_processing(sample_app_context_release, sample_available_agents)
        
        assert "Successfully routed major release to releasenotes_agent" in result
    
    def test_route_minor_release(self, sample_app_context_release, sample_available_agents):
        """Test routing minor release to appropriate agent."""
        sample_app_context_release.content.version = "1.5.0"
        sample_app_context_release.content.features = ["New feature"]
        sample_app_context_release.content.breaking_changes = []
        
        result = route_release_processing(sample_app_context_release, sample_available_agents)
        
        assert "Successfully routed minor release to releasenotes_agent" in result
    
    def test_route_patch_release(self, sample_app_context_release, sample_available_agents):
        """Test routing patch release to appropriate agent."""
        sample_app_context_release.content.version = "1.0.3"
        sample_app_context_release.content.changes = ["Bug fix"]
        sample_app_context_release.content.features = []
        sample_app_context_release.content.breaking_changes = []
        
        result = route_release_processing(sample_app_context_release, sample_available_agents)
        
        assert "Successfully routed patch release to releasenotes_agent" in result
    
    def test_route_hotfix_release(self, sample_app_context_release, sample_available_agents):
        """Test routing hotfix release to appropriate agent."""
        sample_app_context_release.content.version = "1.0.1"
        sample_app_context_release.content.changes = []
        sample_app_context_release.content.features = []
        sample_app_context_release.content.breaking_changes = []
        
        result = route_release_processing(sample_app_context_release, sample_available_agents)
        
        assert "Successfully routed hotfix release to releasenotes_agent" in result
    
    def test_route_general_release(self, sample_app_context_release, sample_available_agents):
        """Test routing general release to general agent."""
        sample_app_context_release.content.version = "1.0.0"
        sample_app_context_release.content.changes = []
        sample_app_context_release.content.features = []
        sample_app_context_release.content.breaking_changes = []
        
        result = route_release_processing(sample_app_context_release, sample_available_agents)
        
        assert "Successfully routed general release to releasenotes_agent" in result
    
    def test_route_release_no_agent_available(self, sample_release_notes):
        """Test routing when no agent is available."""
        from marketing_project.core.models import AppContext
        available_agents = {}  # Empty agents dictionary
        
        # Create a fresh app context
        app_context = AppContext(
            content=sample_release_notes,
            labels={'version': '2.0.0', 'type': 'major'},
            content_type='release_notes'
        )
        
        result = route_release_processing(app_context, available_agents)
        
        assert "No specialized agent for major release, using general processing" in result
    
    def test_route_release_wrong_content_type(self, sample_app_context_blog, sample_available_agents):
        """Test routing with wrong content type."""
        result = route_release_processing(sample_app_context_blog, sample_available_agents)
        
        assert result == "Error: Content is not release notes"


class TestIntegration:
    """Test integration between functions."""
    
    @patch('marketing_project.plugins.release_notes.tasks.parse_release_notes')
    @patch('marketing_project.plugins.release_notes.tasks.extract_images_from_content')
    @patch('marketing_project.plugins.release_notes.tasks.enhance_content_with_ocr')
    def test_full_release_notes_processing_workflow(self, mock_enhance, mock_extract, mock_parse, 
                                                   sample_release_notes, sample_available_agents):
        """Test the full release notes processing workflow."""
        # Setup mocks
        mock_parse.return_value = {
            'version': '2.1.0',
            'release_date': '2024-01-01',
            'changes': ['Change 1', 'Change 2'],
            'breaking_changes': ['Breaking change'],
            'features': ['Feature 1', 'Feature 2'],
            'bug_fixes': ['Bug fix 1', 'Bug fix 2'],
            'cleaned_content': 'Cleaned release notes content'
        }
        mock_extract.return_value = ['https://example.com/screenshot.png']
        mock_enhance.return_value = {
            'enhanced_content': 'Enhanced release notes',
            'ocr_text': 'OCR text',
            'has_screenshots': True,
            'image_count': 1,
            'screenshot_text': 'Screenshot text'
        }
        
        # Step 1: Analyze release type
        release_type = analyze_release_type(sample_release_notes)
        assert release_type in ['major', 'minor', 'patch', 'hotfix']
        
        # Step 2: Extract metadata
        metadata = extract_release_metadata(sample_release_notes)
        assert metadata['content_type'] == 'release_notes'
        assert 'version' in metadata
        assert 'changes_count' in metadata
        
        # Step 3: Validate structure
        is_valid = validate_release_structure(sample_release_notes)
        assert is_valid is True
        
        # Step 4: Enhance with OCR
        enhanced_data = enhance_release_notes_with_ocr(sample_release_notes)
        assert 'enhanced_content' in enhanced_data
        assert 'ocr_text' in enhanced_data
        
        # Step 5: Route to appropriate agent
        app_context = AppContext(
            content=sample_release_notes,
            labels={'category': 'product'},
            content_type='release_notes'
        )
        routing_result = route_release_processing(app_context, sample_available_agents)
        assert "Successfully routed" in routing_result or "No specialized agent" in routing_result


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_analyze_release_type_empty_version(self):
        """Test analyzing release with empty version."""
        release_notes = ReleaseNotesContext(
            id="test-1",
            title="Test Release",
            content="Some content",
            snippet="Some snippet",
            version=""
        )
        
        result = analyze_release_type(release_notes)
        assert result == "patch"  # Should fallback to patch
    
    def test_analyze_release_type_none_version(self):
        """Test analyzing release with empty version."""
        release_notes = ReleaseNotesContext(
            id="test-1",
            title="Test Release",
            content="Some content",
            snippet="Some snippet",
            version=""
        )
        
        result = analyze_release_type(release_notes)
        assert result == "patch"  # Should fallback to patch
    
    def test_extract_metadata_with_minimal_release_notes(self):
        """Test extracting metadata from minimal release notes."""
        release_notes = ReleaseNotesContext(
            id="test-1",
            title="Minimal Release",
            content="Minimal content",
            snippet="Minimal snippet",
            version="1.0.0"
        )
        
        with patch('marketing_project.plugins.release_notes.tasks.parse_release_notes') as mock_parse:
            mock_parse.return_value = {
                'version': '1.0.0',
                'release_date': None,
                'changes': [],
                'breaking_changes': [],
                'features': [],
                'bug_fixes': [],
                'cleaned_content': 'Minimal content'
            }
            
            result = extract_release_metadata(release_notes)
            
            assert result['content_type'] == 'release_notes'
            assert result['id'] == 'test-1'
            assert result['title'] == 'Minimal Release'
            assert result['changes_count'] == 0
            assert result['breaking_changes_count'] == 0
            assert result['features_count'] == 0
            assert result['bug_fixes_count'] == 0
            assert result['has_breaking_changes'] is False
            assert result['has_new_features'] is False
    
    def test_validate_release_structure_minimal_valid(self):
        """Test validating minimal but valid release notes structure."""
        release_notes = ReleaseNotesContext(
            id="test-1",
            title="Test",
            content="Content",
            snippet="Snippet",
            version="1.0.0"
        )
        
        result = validate_release_structure(release_notes)
        assert result is True
    
    def test_analyze_release_type_complex_version(self):
        """Test analyzing release with complex version format."""
        release_notes = ReleaseNotesContext(
            id="test-1",
            title="Test Release",
            content="Some content",
            snippet="Some snippet",
            version="1.2.3-beta.1"
        )
        
        # Should handle complex version formats gracefully
        result = analyze_release_type(release_notes)
        assert result in ['major', 'minor', 'patch', 'hotfix']
