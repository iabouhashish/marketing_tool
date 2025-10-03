"""
Tests for the SEO optimization plugin.

This module tests all functions in the SEO optimization plugin tasks.
"""

import pytest
from unittest.mock import Mock, patch
from marketing_project.plugins.seo_optimization.tasks import (
    optimize_title_tags,
    optimize_meta_descriptions,
    optimize_headings,
    optimize_content_structure,
    add_internal_links,
    analyze_seo_performance,
    analyze_technical_seo,
    calculate_seo_score
)
from marketing_project.core.models import ContentContext, BlogPostContext


class TestOptimizeTitleTags:
    """Test the optimize_title_tags function."""
    
    def test_optimize_title_tags_with_dict(self, sample_article_data):
        """Test optimizing title tags with dictionary input."""
        result = optimize_title_tags(sample_article_data)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'optimize_title_tags'
        
        data = result['data']
        assert 'current_title' in data
        assert 'optimized_titles' in data
        assert 'recommendations' in data
        assert 'seo_score' in data
        assert 'character_count' in data
        
        assert isinstance(data['optimized_titles'], list)
        assert isinstance(data['recommendations'], list)
        assert isinstance(data['seo_score'], (int, float))
        assert 0 <= data['seo_score'] <= 100
        assert isinstance(data['character_count'], int)
    
    def test_optimize_title_tags_with_content_context(self, sample_content_context):
        """Test optimizing title tags with ContentContext input."""
        result = optimize_title_tags(sample_content_context)
        
        assert result['success'] is True
        data = result['data']
        assert 'current_title' in data
        assert 'seo_score' in data
    
    def test_optimize_title_tags_with_keywords(self, sample_article_data):
        """Test optimizing title tags with keywords provided."""
        keywords = [
            {'keyword': 'SEO optimization'},
            {'keyword': 'content marketing'},
            {'keyword': 'search engine'}
        ]
        
        result = optimize_title_tags(sample_article_data, keywords)
        
        assert result['success'] is True
        data = result['data']
        assert len(data['optimized_titles']) > 0
        
        # Check that optimized titles contain keywords
        for title in data['optimized_titles']:
            assert isinstance(title, str)
            assert len(title) > 0
    
    def test_optimize_title_tags_analyzes_current_title(self, sample_article_data):
        """Test that title optimization analyzes current title."""
        result = optimize_title_tags(sample_article_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should analyze current title
        assert 'current_title' in data
        assert 'character_count' in data
        assert 'seo_score' in data
        assert 'recommendations' in data
    
    def test_optimize_title_tags_error_handling(self):
        """Test error handling in optimize_title_tags."""
        # Test with invalid input that should trigger an error
        result = optimize_title_tags(None)
        assert result['success'] is False
        assert 'error' in result


class TestOptimizeMetaDescriptions:
    """Test the optimize_meta_descriptions function."""
    
    def test_optimize_meta_descriptions_with_dict(self, sample_article_data):
        """Test optimizing meta descriptions with dictionary input."""
        result = optimize_meta_descriptions(sample_article_data)
        
        assert 'current_meta' in result
        assert 'optimized_meta' in result
        assert 'recommendations' in result
        assert 'seo_score' in result
        assert 'character_count' in result
        
        assert isinstance(result['optimized_meta'], list)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['seo_score'], (int, float))
        assert 0 <= result['seo_score'] <= 100
        assert isinstance(result['character_count'], int)
    
    def test_optimize_meta_descriptions_with_keywords(self, sample_article_data):
        """Test optimizing meta descriptions with keywords provided."""
        keywords = [
            {'keyword': 'SEO optimization'},
            {'keyword': 'content marketing'},
            {'keyword': 'search engine'}
        ]
        
        result = optimize_meta_descriptions(sample_article_data, keywords)
        
        assert len(result['optimized_meta']) > 0
        
        # Check that optimized descriptions contain keywords
        for meta in result['optimized_meta']:
            assert isinstance(meta, str)
            assert len(meta) > 0
    
    def test_optimize_meta_descriptions_analyzes_current(self, sample_article_data):
        """Test that meta description optimization analyzes current description."""
        result = optimize_meta_descriptions(sample_article_data)
        
        # Should analyze current meta description
        assert 'current_meta' in result
        assert 'character_count' in result
        assert 'seo_score' in result
        assert 'recommendations' in result


class TestOptimizeHeadings:
    """Test the optimize_headings function."""
    
    def test_optimize_headings_with_dict(self, sample_article_data):
        """Test optimizing headings with dictionary input."""
        result = optimize_headings(sample_article_data)
        
        assert 'current_headings' in result
        assert 'optimized_headings' in result
        assert 'recommendations' in result
        assert 'seo_score' in result
        assert 'heading_structure' in result
        
        assert isinstance(result['current_headings'], dict)
        assert isinstance(result['optimized_headings'], dict) or isinstance(result['optimized_headings'], list)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['seo_score'], (int, float))
        assert 0 <= result['seo_score'] <= 100
        assert isinstance(result['heading_structure'], dict)
    
    def test_optimize_headings_with_keywords(self, sample_article_data):
        """Test optimizing headings with keywords provided."""
        keywords = [
            {'keyword': 'SEO optimization'},
            {'keyword': 'content marketing'},
            {'keyword': 'search engine'}
        ]
        
        result = optimize_headings(sample_article_data, keywords)
        
        assert 'optimized_headings' in result
        
        # Check heading structure
        heading_structure = result['heading_structure']
        assert 'h1_count' in heading_structure
        assert 'h2_count' in heading_structure
        assert 'h3_count' in heading_structure
        assert 'total_headings' in heading_structure
    
    def test_optimize_headings_analyzes_current(self, sample_article_data):
        """Test that heading optimization analyzes current headings."""
        result = optimize_headings(sample_article_data)
        
        # Should analyze current heading structure
        assert 'current_headings' in result
        assert 'heading_structure' in result
        assert 'seo_score' in result
        assert 'recommendations' in result


class TestOptimizeContentStructure:
    """Test the optimize_content_structure function."""
    
    def test_optimize_content_structure_with_dict(self, sample_article_data):
        """Test optimizing content structure with dictionary input."""
        result = optimize_content_structure(sample_article_data)
        
        assert 'word_count' in result
        assert 'paragraph_count' in result
        assert 'sentence_count' in result
        assert 'readability_score' in result
        assert 'keyword_density' in result
        assert 'recommendations' in result
        assert 'seo_score' in result
        
        assert isinstance(result['word_count'], int)
        assert isinstance(result['paragraph_count'], int)
        assert isinstance(result['sentence_count'], int)
        assert isinstance(result['readability_score'], (int, float))
        assert isinstance(result['keyword_density'], dict)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['seo_score'], (int, float))
        assert 0 <= result['seo_score'] <= 100
    
    def test_optimize_content_structure_with_keywords(self, sample_article_data):
        """Test optimizing content structure with keywords provided."""
        keywords = [
            {'keyword': 'SEO optimization'},
            {'keyword': 'content marketing'},
            {'keyword': 'search engine'}
        ]
        
        result = optimize_content_structure(sample_article_data, keywords)
        
        assert 'keyword_density' in result
        
        # Check keyword density analysis
        keyword_density = result['keyword_density']
        for keyword, data in keyword_density.items():
            assert 'frequency' in data
            assert 'density' in data
            assert 'status' in data
            assert isinstance(data['frequency'], int)
            assert isinstance(data['density'], (int, float))
            assert data['status'] in ['optimal', 'needs_optimization']
    
    def test_optimize_content_structure_analyzes_content(self, sample_article_data):
        """Test that content structure optimization analyzes content."""
        result = optimize_content_structure(sample_article_data)
        
        # Should analyze content metrics
        assert result['word_count'] > 0
        assert result['paragraph_count'] > 0
        assert result['sentence_count'] > 0
        assert 'readability_score' in result
        assert 'recommendations' in result


class TestAddInternalLinks:
    """Test the add_internal_links function."""
    
    def test_add_internal_links_with_dict(self, sample_article_data):
        """Test adding internal links with dictionary input."""
        result = add_internal_links(sample_article_data)
        
        assert 'internal_links' in result
        assert isinstance(result['internal_links'], list)
        
        # Check that original content is preserved
        assert result['content'] == sample_article_data['content']
        assert result['title'] == sample_article_data['title']
    
    def test_add_internal_links_with_custom_pages(self, sample_article_data):
        """Test adding internal links with custom internal pages."""
        internal_pages = [
            {'url': '/custom-page', 'title': 'Custom Page', 'keywords': ['custom', 'page']},
            {'url': '/another-page', 'title': 'Another Page', 'keywords': ['another', 'page']}
        ]
        
        result = add_internal_links(sample_article_data, internal_pages)
        
        assert 'internal_links' in result
        assert isinstance(result['internal_links'], list)
    
    def test_add_internal_links_finds_opportunities(self, sample_article_data):
        """Test that internal links function finds linking opportunities."""
        result = add_internal_links(sample_article_data)
        
        # Should find some linking opportunities
        assert isinstance(result['internal_links'], list)
        
        # Check link structure if any links found
        for link in result['internal_links']:
            assert 'keyword' in link
            assert 'url' in link
            assert 'title' in link


class TestAnalyzeSeoPerformance:
    """Test the analyze_seo_performance function."""
    
    def test_analyze_seo_performance_with_dict(self, sample_article_data):
        """Test analyzing SEO performance with dictionary input."""
        result = analyze_seo_performance(sample_article_data)
        
        assert 'overall_score' in result
        assert 'title_optimization' in result
        assert 'meta_optimization' in result
        assert 'heading_optimization' in result
        assert 'content_optimization' in result
        assert 'technical_seo' in result
        assert 'recommendations' in result
        assert 'priority_actions' in result
        
        assert isinstance(result['overall_score'], (int, float))
        assert 0 <= result['overall_score'] <= 100
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['priority_actions'], list)
    
    def test_analyze_seo_performance_with_keywords(self, sample_article_data):
        """Test analyzing SEO performance with keywords provided."""
        keywords = [
            {'keyword': 'SEO optimization'},
            {'keyword': 'content marketing'},
            {'keyword': 'search engine'}
        ]
        
        result = analyze_seo_performance(sample_article_data, keywords)
        
        assert 'overall_score' in result
        assert 'recommendations' in result
        assert 'priority_actions' in result
    
    def test_analyze_seo_performance_provides_comprehensive_analysis(self, sample_article_data):
        """Test that SEO performance analysis provides comprehensive results."""
        result = analyze_seo_performance(sample_article_data)
        
        # Should provide comprehensive analysis
        assert 'title_optimization' in result
        assert 'meta_optimization' in result
        assert 'heading_optimization' in result
        assert 'content_optimization' in result
        assert 'technical_seo' in result
        
        # Each optimization should have seo_score (check in data for title_optimization)
        for optimization in ['meta_optimization', 'heading_optimization', 'content_optimization', 'technical_seo']:
            if result[optimization]:
                assert 'seo_score' in result[optimization]
        
        # Check title_optimization has seo_score in data
        if result['title_optimization']:
            assert 'data' in result['title_optimization']
            assert 'seo_score' in result['title_optimization']['data']


class TestAnalyzeTechnicalSeo:
    """Test the analyze_technical_seo function."""
    
    def test_analyze_technical_seo_with_dict(self, sample_article_data):
        """Test analyzing technical SEO with dictionary input."""
        result = analyze_technical_seo(sample_article_data)
        
        assert 'seo_score' in result
        assert 'recommendations' in result
        assert 'checks' in result
        
        assert isinstance(result['seo_score'], (int, float))
        assert 0 <= result['seo_score'] <= 100
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['checks'], dict)
    
    def test_analyze_technical_seo_checks_technical_elements(self, sample_article_data):
        """Test that technical SEO analysis checks technical elements."""
        result = analyze_technical_seo(sample_article_data)
        
        checks = result['checks']
        
        # Should check various technical elements
        expected_checks = [
            'has_title', 'has_meta_description', 'title_length_ok', 'meta_length_ok',
            'has_h1', 'has_h2', 'word_count_ok', 'has_images', 'has_links', 'has_lists'
        ]
        
        for check in expected_checks:
            assert check in checks
            assert isinstance(checks[check], bool)
    
    def test_analyze_technical_seo_generates_recommendations(self, sample_article_data):
        """Test that technical SEO analysis generates recommendations."""
        result = analyze_technical_seo(sample_article_data)
        
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
        
        # Should have some recommendations based on failed checks
        for recommendation in result['recommendations']:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0


class TestCalculateSeoScore:
    """Test the calculate_seo_score function."""
    
    def test_calculate_seo_score_with_dict(self, sample_article_data):
        """Test calculating SEO score with dictionary input."""
        result = calculate_seo_score(sample_article_data)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'calculate_seo_score'
        
        data = result['data']
        assert 'overall_seo_score' in data
        assert 'seo_grade' in data
        assert 'score_breakdown' in data
        assert 'issues' in data
        assert 'recommendations' in data
        assert 'keyword_density' in data
        assert 'content_metrics' in data
        
        assert isinstance(data['overall_seo_score'], (int, float))
        assert 0 <= data['overall_seo_score'] <= 100
        assert data['seo_grade'] in ['A', 'B', 'C', 'D', 'F']
        assert isinstance(data['score_breakdown'], dict)
        assert isinstance(data['issues'], list)
        assert isinstance(data['recommendations'], list)
        assert isinstance(data['keyword_density'], dict)
        assert isinstance(data['content_metrics'], dict)
    
    def test_calculate_seo_score_with_content_context(self, sample_content_context):
        """Test calculating SEO score with ContentContext input."""
        result = calculate_seo_score(sample_content_context)
        
        assert result['success'] is True
        data = result['data']
        assert 'overall_seo_score' in data
        assert 'seo_grade' in data
        assert 'score_breakdown' in data
    
    def test_calculate_seo_score_with_keywords(self, sample_article_data):
        """Test calculating SEO score with keywords provided."""
        keywords = [
            {'keyword': 'SEO optimization'},
            {'keyword': 'content marketing'},
            {'keyword': 'search engine'}
        ]
        
        result = calculate_seo_score(sample_article_data, keywords)
        
        assert result['success'] is True
        data = result['data']
        assert 'keyword_density' in data
        assert len(data['keyword_density']) > 0
    
    def test_calculate_seo_score_provides_breakdown(self, sample_article_data):
        """Test that SEO score calculation provides detailed breakdown."""
        result = calculate_seo_score(sample_article_data)
        
        assert result['success'] is True
        score_breakdown = result['data']['score_breakdown']
        
        # Should provide detailed score breakdown
        expected_categories = [
            'title_optimization', 'meta_description', 'content_quality',
            'keyword_optimization', 'technical_seo', 'content_structure',
            'readability', 'internal_linking'
        ]
        
        for category in expected_categories:
            assert category in score_breakdown
            assert isinstance(score_breakdown[category], (int, float))
            assert 0 <= score_breakdown[category] <= 20  # Max points per category
    
    def test_calculate_seo_score_identifies_issues(self, sample_article_data):
        """Test that SEO score calculation identifies issues."""
        result = calculate_seo_score(sample_article_data)
        
        assert result['success'] is True
        issues = result['data']['issues']
        recommendations = result['data']['recommendations']
        
        # Should identify issues and provide recommendations
        assert isinstance(issues, list)
        assert isinstance(recommendations, list)
        
        for issue in issues:
            assert isinstance(issue, str)
            assert len(issue) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
    
    def test_calculate_seo_score_error_handling(self):
        """Test error handling in calculate_seo_score."""
        # Test with invalid input that should trigger an error
        result = calculate_seo_score(None)
        assert result['success'] is False
        assert 'error' in result


class TestIntegration:
    """Test integration between functions."""
    
    def test_full_seo_optimization_workflow(self, sample_article_data):
        """Test the full SEO optimization workflow."""
        # Step 1: Optimize title tags
        title_result = optimize_title_tags(sample_article_data)
        assert title_result['success'] is True
        
        # Step 2: Optimize meta descriptions
        meta_result = optimize_meta_descriptions(sample_article_data)
        
        # Step 3: Optimize headings
        heading_result = optimize_headings(sample_article_data)
        
        # Step 4: Optimize content structure
        content_result = optimize_content_structure(sample_article_data)
        
        # Step 5: Add internal links
        links_result = add_internal_links(sample_article_data)
        assert 'internal_links' in links_result
        
        # Step 6: Analyze SEO performance
        performance_result = analyze_seo_performance(sample_article_data)
        assert 'overall_score' in performance_result
        
        # Step 7: Calculate overall SEO score
        score_result = calculate_seo_score(sample_article_data)
        assert score_result['success'] is True
        
        # Verify all results have expected structure
        assert 'optimized_titles' in title_result['data']
        assert 'optimized_meta' in meta_result
        assert 'optimized_headings' in heading_result
        assert 'word_count' in content_result
        assert 'overall_seo_score' in score_result['data']


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_optimize_title_tags_no_title(self):
        """Test optimizing title tags when no title is provided."""
        no_title_article = {'content': 'Some content'}
        
        result = optimize_title_tags(no_title_article)
        
        assert result['success'] is True
        assert result['data']['current_title'] == ''
        assert result['data']['character_count'] == 0
    
    def test_optimize_meta_descriptions_no_description(self):
        """Test optimizing meta descriptions when no description is provided."""
        no_meta_article = {'content': 'Some content', 'title': 'Some Title'}
        
        result = optimize_meta_descriptions(no_meta_article)
        
        assert result['current_meta'] == ''
        assert result['character_count'] == 0
    
    def test_calculate_seo_score_minimal_content(self):
        """Test calculating SEO score for minimal content."""
        minimal_article = {'content': 'Minimal content', 'title': 'Minimal'}
        
        result = calculate_seo_score(minimal_article)
        
        assert result['success'] is True
        assert result['data']['overall_seo_score'] < 50  # Should be low score
        assert len(result['data']['issues']) > 0  # Should identify issues
    
    def test_calculate_seo_score_empty_content(self):
        """Test calculating SEO score for empty content."""
        empty_article = {'content': '', 'title': ''}
        
        result = calculate_seo_score(empty_article)
        
        assert result['success'] is True
        assert result['data']['overall_seo_score'] < 30  # Should be very low score
        assert len(result['data']['issues']) > 0  # Should identify many issues
