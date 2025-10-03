"""
Tests for the blog posts plugin.

This module tests all functions in the blog posts plugin tasks.
"""

import pytest
from unittest.mock import Mock, patch
from marketing_project.plugins.blog_posts.tasks import (
    analyze_blog_post_type,
    extract_blog_post_metadata,
    validate_blog_post_structure,
    enhance_blog_post_with_ocr,
    route_blog_post_processing
)
from marketing_project.core.models import BlogPostContext, AppContext


class TestAnalyzeBlogPostType:
    """Test the analyze_blog_post_type function."""
    
    def test_analyze_tutorial_blog_post(self, sample_blog_post):
        """Test analyzing a tutorial blog post."""
        sample_blog_post.title = "How to Build AI Applications: A Complete Tutorial"
        result = analyze_blog_post_type(sample_blog_post)
        assert result == "tutorial"
    
    def test_analyze_review_blog_post(self, sample_blog_post):
        """Test analyzing a review blog post."""
        sample_blog_post.title = "Best AI Tools Review: Comparing Top 10 Solutions"
        result = analyze_blog_post_type(sample_blog_post)
        assert result == "review"
    
    def test_analyze_news_blog_post(self, sample_blog_post):
        """Test analyzing a news blog post."""
        sample_blog_post.title = "Breaking News: New AI Breakthrough Announced"
        result = analyze_blog_post_type(sample_blog_post)
        assert result == "news"
    
    def test_analyze_analysis_blog_post(self, sample_blog_post):
        """Test analyzing an analysis blog post."""
        sample_blog_post.title = "Deep Dive Analysis: AI Market Trends 2024"
        result = analyze_blog_post_type(sample_blog_post)
        assert result == "analysis"
    
    def test_analyze_blog_post_with_category(self, sample_blog_post):
        """Test analyzing a blog post with category."""
        sample_blog_post.title = "Some Random Title"
        sample_blog_post.category = "Technology"
        result = analyze_blog_post_type(sample_blog_post)
        assert result == "technology"
    
    def test_analyze_general_blog_post(self, sample_blog_post):
        """Test analyzing a general blog post."""
        sample_blog_post.title = "Random Blog Post About Nothing"
        sample_blog_post.category = None
        result = analyze_blog_post_type(sample_blog_post)
        assert result == "general"


class TestExtractBlogPostMetadata:
    """Test the extract_blog_post_metadata function."""
    
    @patch('marketing_project.plugins.blog_posts.tasks.parse_blog_post')
    def test_extract_blog_post_metadata(self, mock_parse, sample_blog_post):
        """Test extracting metadata from blog post."""
        mock_parse.return_value = {
            'title': 'Parsed Title',
            'metadata': {'author': 'Parsed Author'},
            'tags': ['parsed', 'tags'],
            'word_count': 200,
            'reading_time': '2 min',
            'headings': ['Heading 1', 'Heading 2'],
            'links': ['https://example.com'],
            'cleaned_content': 'Cleaned content'
        }
        
        result = extract_blog_post_metadata(sample_blog_post)
        
        assert isinstance(result, dict)
        assert result['content_type'] == 'blog_post'
        assert result['id'] == sample_blog_post.id
        assert result['title'] == sample_blog_post.title
        assert result['author'] == sample_blog_post.author
        assert result['category'] == sample_blog_post.category
        assert result['tags'] == sample_blog_post.tags
        assert result['word_count'] == sample_blog_post.word_count
        assert result['reading_time'] == sample_blog_post.reading_time
        assert result['tag_count'] == len(sample_blog_post.tags)
        assert result['has_author'] is True
        assert result['has_category'] is True
        assert 'headings' in result
        assert 'links' in result
        assert 'parsed_tags' in result
        assert 'cleaned_content' in result
    
    @patch('marketing_project.plugins.blog_posts.tasks.parse_blog_post')
    def test_extract_blog_post_metadata_with_parsed_data(self, mock_parse, sample_blog_post):
        """Test extracting metadata with parsed data overriding original."""
        mock_parse.return_value = {
            'title': 'Different Title',
            'metadata': {'author': 'Different Author', 'category': 'Different Category'},
            'tags': ['different', 'tags'],
            'word_count': 300,
            'reading_time': '3 min',
            'headings': ['Different Heading'],
            'links': ['https://different.com'],
            'cleaned_content': 'Different cleaned content'
        }
        
        # Set original values to None to test fallback
        sample_blog_post.author = None
        sample_blog_post.category = None
        sample_blog_post.tags = None
        sample_blog_post.word_count = None
        sample_blog_post.reading_time = None
        
        result = extract_blog_post_metadata(sample_blog_post)
        
        assert result['title'] == sample_blog_post.title  # Original title should be used
        assert result['author'] == 'Different Author'
        assert result['category'] == 'Different Category'
        assert result['tags'] == ['different', 'tags']
        assert result['word_count'] == 300
        assert result['reading_time'] == '3 min'


class TestValidateBlogPostStructure:
    """Test the validate_blog_post_structure function."""
    
    def test_validate_valid_blog_post(self, sample_blog_post):
        """Test validating a valid blog post."""
        result = validate_blog_post_structure(sample_blog_post)
        assert result is True
    
    def test_validate_blog_post_missing_id(self, sample_blog_post):
        """Test validating blog post with missing ID."""
        sample_blog_post.id = None
        result = validate_blog_post_structure(sample_blog_post)
        assert result is False
    
    def test_validate_blog_post_missing_title(self, sample_blog_post):
        """Test validating blog post with missing title."""
        sample_blog_post.title = None
        result = validate_blog_post_structure(sample_blog_post)
        assert result is False
    
    def test_validate_blog_post_missing_content(self, sample_blog_post):
        """Test validating blog post with missing content."""
        sample_blog_post.content = None
        result = validate_blog_post_structure(sample_blog_post)
        assert result is False
    
    def test_validate_blog_post_missing_snippet(self, sample_blog_post):
        """Test validating blog post with missing snippet."""
        sample_blog_post.snippet = None
        result = validate_blog_post_structure(sample_blog_post)
        assert result is False


class TestEnhanceBlogPostWithOCR:
    """Test the enhance_blog_post_with_ocr function."""
    
    @patch('marketing_project.plugins.blog_posts.tasks.extract_images_from_content')
    @patch('marketing_project.plugins.blog_posts.tasks.enhance_content_with_ocr')
    def test_enhance_blog_post_with_ocr_no_images(self, mock_enhance, mock_extract, sample_blog_post):
        """Test enhancing blog post with OCR when no images provided."""
        mock_extract.return_value = []
        mock_enhance.return_value = {
            'enhanced_content': 'Enhanced content',
            'ocr_text': 'OCR text',
            'has_images': False,
            'image_count': 0,
            'image_alt_text': []
        }
        
        result = enhance_blog_post_with_ocr(sample_blog_post)
        
        assert isinstance(result, dict)
        assert 'original_blog_post' in result
        assert 'enhanced_content' in result
        assert 'ocr_text' in result
        assert 'has_images' in result
        assert 'image_count' in result
        assert 'image_alt_text' in result
        
        assert result['original_blog_post'] == sample_blog_post
        assert result['has_images'] is False
        assert result['image_count'] == 0
        assert result['image_alt_text'] == []
    
    @patch('marketing_project.plugins.blog_posts.tasks.enhance_content_with_ocr')
    def test_enhance_blog_post_with_ocr_with_images(self, mock_enhance, sample_blog_post):
        """Test enhancing blog post with OCR when images are provided."""
        image_urls = ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
        mock_enhance.return_value = {
            'enhanced_content': 'Enhanced content with images',
            'ocr_text': 'OCR text from images',
            'has_images': True,
            'image_count': 2,
            'image_alt_text': ['Alt text 1', 'Alt text 2']
        }
        
        result = enhance_blog_post_with_ocr(sample_blog_post, image_urls)
        
        assert result['has_images'] is True
        assert result['image_count'] == 2
        assert len(result['image_alt_text']) == 2
        
        # Verify OCR service was called with correct parameters
        mock_enhance.assert_called_once_with(
            sample_blog_post.content,
            'blog_post',
            image_urls=image_urls
        )

class TestIntegration:
    """Test integration between functions."""
    
    @patch('marketing_project.plugins.blog_posts.tasks.parse_blog_post')
    @patch('marketing_project.plugins.blog_posts.tasks.extract_images_from_content')
    @patch('marketing_project.plugins.blog_posts.tasks.enhance_content_with_ocr')
    def test_full_blog_post_processing_workflow(self, mock_enhance, mock_extract, mock_parse, 
                                               sample_blog_post, sample_available_agents):
        """Test the full blog post processing workflow."""
        # Setup mocks
        mock_parse.return_value = {
            'title': 'Parsed Title',
            'metadata': {'author': 'Parsed Author'},
            'tags': ['parsed', 'tags'],
            'word_count': 200,
            'reading_time': '2 min',
            'headings': ['Heading 1'],
            'links': ['https://example.com'],
            'cleaned_content': 'Cleaned content'
        }
        mock_extract.return_value = ['https://example.com/image.jpg']
        mock_enhance.return_value = {
            'enhanced_content': 'Enhanced content',
            'ocr_text': 'OCR text',
            'has_images': True,
            'image_count': 1,
            'image_alt_text': ['Alt text']
        }
        
        # Step 1: Analyze blog post type
        blog_type = analyze_blog_post_type(sample_blog_post)
        assert blog_type in ['tutorial', 'review', 'news', 'analysis', 'general']
        
        # Step 2: Extract metadata
        metadata = extract_blog_post_metadata(sample_blog_post)
        assert metadata['content_type'] == 'blog_post'
        assert 'word_count' in metadata
        
        # Step 3: Validate structure
        is_valid = validate_blog_post_structure(sample_blog_post)
        assert is_valid is True
        
        # Step 4: Enhance with OCR
        enhanced_data = enhance_blog_post_with_ocr(sample_blog_post)
        assert 'enhanced_content' in enhanced_data
        assert 'ocr_text' in enhanced_data
        
        # Step 5: Route to appropriate agent
        app_context = AppContext(
            content=sample_blog_post,
            labels={'category': 'technology'},
            content_type='blog_post'
        )
        routing_result = route_blog_post_processing(app_context, sample_available_agents)
        assert "Successfully routed" in routing_result or "No specialized agent" in routing_result


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_analyze_blog_post_type_empty_title(self):
        """Test analyzing blog post with empty title."""
        blog_post = BlogPostContext(
            id="test-1",
            title="",
            content="Some content",
            snippet="Some snippet"
        )
        
        result = analyze_blog_post_type(blog_post)
        assert result == "general"
    
    def test_analyze_blog_post_type_none_title(self):
        """Test analyzing blog post with empty title."""
        blog_post = BlogPostContext(
            id="test-1",
            title="",
            content="Some content",
            snippet="Some snippet"
        )
        
        result = analyze_blog_post_type(blog_post)
        assert result == "general"
    
    def test_extract_metadata_with_minimal_blog_post(self):
        """Test extracting metadata from minimal blog post."""
        blog_post = BlogPostContext(
            id="test-1",
            title="Minimal Title",
            content="Minimal content",
            snippet="Minimal snippet"
        )
        
        with patch('marketing_project.plugins.blog_posts.tasks.parse_blog_post') as mock_parse:
            mock_parse.return_value = {
                'title': 'Parsed Title',
                'metadata': {},
                'tags': [],
                'word_count': 0,
                'reading_time': '',
                'headings': [],
                'links': [],
                'cleaned_content': 'Minimal content'
            }
            
            result = extract_blog_post_metadata(blog_post)
            
            assert result['content_type'] == 'blog_post'
            assert result['id'] == 'test-1'
            assert result['title'] == 'Minimal Title'
            assert result['has_author'] is False
            assert result['has_category'] is False
            assert result['tag_count'] == 0
