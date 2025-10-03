"""
Tests for kwx-based keyword extraction functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from marketing_project.core.models import BlogPostContext
from marketing_project.plugins.seo_keywords.tasks import (
    extract_keywords_with_kwx,
    extract_keywords_advanced
)


class TestKWXKeywordExtraction:
    """Test cases for kwx-based keyword extraction."""
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return BlogPostContext(
            id="test-content",
            title="Machine Learning for Marketing",
            content="Machine learning is revolutionizing marketing strategies. AI-powered tools help businesses analyze customer behavior and optimize campaigns. Data-driven marketing approaches are becoming essential for competitive advantage.",
            snippet="Learn how machine learning transforms marketing"
        )
    
    @pytest.fixture
    def empty_content(self):
        """Empty content for testing edge cases."""
        return BlogPostContext(
            id="empty-content",
            title="Empty Test",
            content="",
            snippet=""
        )
    
    @pytest.fixture
    def title_only_content(self):
        """Content with only title for testing."""
        return BlogPostContext(
            id="title-only",
            title="Marketing Automation Guide",
            content="",
            snippet=""
        )
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', False)
    def test_extract_keywords_with_kwx_not_available(self, sample_content):
        """Test kwx extraction when library is not available."""
        result = extract_keywords_with_kwx(sample_content)
        
        assert result['success'] is False
        assert "kwx library not available" in result['error']
        assert result['task_name'] == 'extract_keywords_with_kwx'
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_kws')
    def test_extract_keywords_with_kwx_frequency_method(self, mock_extract_kws, sample_content):
        """Test kwx extraction with frequency method."""
        # Mock the kwx extract_kws function
        mock_extract_kws.return_value = [
            ["machine learning", "marketing", "data-driven", "customer behavior", "optimize campaigns"]
        ]
        
        result = extract_keywords_with_kwx(sample_content, max_keywords=5, method="frequency")
        
        assert result['success'] is True
        assert result['data']['total_keywords_found'] == 5
        assert result['data']['method'] == "frequency"
        assert result['data']['extraction_library'] == "kwx"
        
        keywords = result['data']['keywords']
        assert len(keywords) == 5
        assert keywords[0]['keyword'] == "machine learning"
        assert keywords[0]['score'] == 1.0  # Dummy score from our implementation
        assert keywords[0]['method'] == "frequency"
        assert keywords[0]['in_title'] is True  # "machine learning" is in title
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_kws')
    def test_extract_keywords_with_kwx_tfidf_method(self, mock_extract_kws, sample_content):
        """Test kwx extraction with tfidf method."""
        # Mock the kwx extract_kws function
        mock_extract_kws.return_value = [
            ["ai-powered tools", "marketing strategies", "competitive advantage"]
        ]
        
        result = extract_keywords_with_kwx(sample_content, max_keywords=3, method="tfidf")
        
        assert result['success'] is True
        assert result['data']['method'] == "tfidf"
        assert result['data']['total_keywords_found'] == 3
        
        keywords = result['data']['keywords']
        assert keywords[0]['keyword'] == "ai-powered tools"
        assert keywords[0]['score'] == 1.0  # Dummy score from our implementation
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_kws')
    def test_extract_keywords_with_kwx_yake_method(self, mock_extract_kws, sample_content):
        """Test kwx extraction with yake method."""
        # Mock the kwx extract_kws function
        mock_extract_kws.return_value = [
            ["marketing automation", "customer analytics"]
        ]
        
        result = extract_keywords_with_kwx(sample_content, method="yake")
        
        assert result['success'] is True
        assert result['data']['method'] == "yake"
        assert result['data']['total_keywords_found'] == 2
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_kws')
    def test_extract_keywords_with_kwx_invalid_method(self, mock_extract_kws, sample_content):
        """Test kwx extraction with invalid method falls back to frequency."""
        # Mock the kwx extract_kws function
        mock_extract_kws.return_value = [["test keyword"]]
        
        result = extract_keywords_with_kwx(sample_content, method="invalid_method")
        
        assert result['success'] is True
        # Should fall back to frequency method
        mock_extract_kws.assert_called_once()
        call_args = mock_extract_kws.call_args
        assert call_args[1]['method'] == 'frequency'  # Should use frequency as fallback
    
    def test_extract_keywords_with_kwx_empty_content(self, empty_content):
        """Test kwx extraction with empty content."""
        result = extract_keywords_with_kwx(empty_content)
        
        assert result['success'] is True  # Our implementation handles empty content gracefully
        assert result['data']['total_keywords_found'] == 0
        assert result['data']['keywords'] == []
    
    def test_extract_keywords_with_kwx_title_only(self, title_only_content):
        """Test kwx extraction with title only content."""
        result = extract_keywords_with_kwx(title_only_content)
        
        assert result['success'] is True
        assert result['data']['total_keywords_found'] == 0
        assert result['data']['keywords'] == []
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_kws')
    def test_extract_keywords_with_kwx_exception_handling(self, mock_extract_kws, sample_content):
        """Test kwx extraction exception handling."""
        # Mock the kwx extract_kws function to raise an exception
        mock_extract_kws.side_effect = Exception("KWX processing error")
        
        result = extract_keywords_with_kwx(sample_content)
        
        assert result['success'] is False
        assert "KWX keyword extraction failed" in result['error']
        assert "KWX processing error" in result['error']
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', False)
    def test_extract_keywords_advanced_not_available(self, sample_content):
        """Test advanced extraction when kwx is not available."""
        result = extract_keywords_advanced(sample_content)
        
        assert result['success'] is False
        assert "kwx library not available" in result['error']
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_keywords_with_kwx')
    def test_extract_keywords_advanced_single_method(self, mock_extract, sample_content):
        """Test advanced extraction with single method."""
        # Mock successful extraction for frequency method
        mock_extract.return_value = {
            'success': True,
            'data': {
                'keywords': [
                    {'keyword': 'machine learning', 'score': 0.8, 'ngram_length': 2, 'in_title': True},
                    {'keyword': 'marketing', 'score': 0.7, 'ngram_length': 1, 'in_title': True}
                ]
            }
        }
        
        result = extract_keywords_advanced(sample_content, methods=['frequency'], max_keywords=2)
        
        assert result['success'] is True
        assert result['data']['total_keywords_found'] == 2
        assert result['data']['methods_used'] == ['frequency']
        assert result['data']['combined_results'] is True
        
        keywords = result['data']['keywords']
        assert len(keywords) == 2
        assert keywords[0]['keyword'] == 'machine learning'
        assert keywords[0]['total_score'] == 0.8
        assert keywords[0]['confidence'] == 1.0  # Single method coverage
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_keywords_with_kwx')
    def test_extract_keywords_advanced_multiple_methods(self, mock_extract, sample_content):
        """Test advanced extraction with multiple methods."""
        # Mock different results for different methods
        def mock_extract_side_effect(content, max_keywords, method):
            if method == 'frequency':
                return {
                    'success': True,
                    'data': {
                        'keywords': [
                            {'keyword': 'machine learning', 'score': 0.8, 'ngram_length': 2, 'in_title': True},
                            {'keyword': 'marketing', 'score': 0.7, 'ngram_length': 1, 'in_title': True}
                        ]
                    }
                }
            elif method == 'tfidf':
                return {
                    'success': True,
                    'data': {
                        'keywords': [
                            {'keyword': 'machine learning', 'score': 0.9, 'ngram_length': 2, 'in_title': True},
                            {'keyword': 'ai-powered', 'score': 0.6, 'ngram_length': 1, 'in_title': False}
                        ]
                    }
                }
            else:  # yake
                return {
                    'success': True,
                    'data': {
                        'keywords': [
                            {'keyword': 'marketing strategies', 'score': 0.85, 'ngram_length': 2, 'in_title': False}
                        ]
                    }
                }
        
        mock_extract.side_effect = mock_extract_side_effect
        
        result = extract_keywords_advanced(
            sample_content, 
            methods=['frequency', 'tfidf', 'yake'], 
            max_keywords=3
        )
        
        assert result['success'] is True
        assert result['data']['total_keywords_found'] == 3
        assert result['data']['methods_used'] == ['frequency', 'tfidf', 'yake']
        
        keywords = result['data']['keywords']
        # Should be sorted by total_score
        assert keywords[0]['keyword'] == 'machine learning'  # Highest combined score
        assert abs(keywords[0]['total_score'] - 0.85) < 0.01  # Average of 0.8 and 0.9 (with floating point precision)
        assert keywords[0]['confidence'] == 2/3  # Found in 2 out of 3 methods
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_keywords_with_kwx')
    def test_extract_keywords_advanced_all_methods_fail(self, mock_extract, sample_content):
        """Test advanced extraction when all methods fail."""
        # Mock all methods to fail
        mock_extract.return_value = {
            'success': False,
            'error': 'Method failed'
        }
        
        result = extract_keywords_advanced(sample_content, methods=['frequency', 'tfidf'])
        
        assert result['success'] is True  # Now returns success with empty results
        assert result['data']['total_keywords_found'] == 0
        assert result['data']['keywords'] == []
    
    @patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True)
    @patch('marketing_project.plugins.seo_keywords.tasks.extract_keywords_with_kwx')
    def test_extract_keywords_advanced_without_combining(self, mock_extract, sample_content):
        """Test advanced extraction without combining results."""
        # Mock successful extraction
        mock_extract.return_value = {
            'success': True,
            'data': {
                'keywords': [
                    {'keyword': 'test keyword', 'score': 0.5, 'ngram_length': 2, 'in_title': False}
                ]
            }
        }
        
        result = extract_keywords_advanced(
            sample_content, 
            methods=['frequency'], 
            combine_results=False
        )
        
        assert result['success'] is True
        assert result['data']['combined_results'] is False
        # Keywords should not have combined scoring when combine_results=False
        keywords = result['data']['keywords']
        # When not combining, keywords should have individual method results
        assert 'methods' in keywords[0]  # Should have methods field
        assert 'scores' in keywords[0]  # Should have scores dict
    
    def test_extract_keywords_advanced_default_methods(self, sample_content):
        """Test advanced extraction with default methods."""
        with patch('marketing_project.plugins.seo_keywords.tasks.KWX_AVAILABLE', True), \
             patch('marketing_project.plugins.seo_keywords.tasks.extract_keywords_with_kwx') as mock_extract:
            
            mock_extract.return_value = {
                'success': True,
                'data': {'keywords': []}
            }
            
            result = extract_keywords_advanced(sample_content)
            
            # Should use default methods
            assert result['success'] is True
            assert result['data']['methods_used'] == ['frequency', 'tfidf', 'yake']
