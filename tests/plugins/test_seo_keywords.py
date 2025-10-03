"""
Tests for the SEO keywords plugin.

This module tests all functions in the SEO keywords plugin tasks.
"""

import pytest
from unittest.mock import Mock, patch
from marketing_project.plugins.seo_keywords.tasks import (
    extract_primary_keywords,
    extract_secondary_keywords,
    analyze_keyword_density,
    generate_keyword_suggestions,
    optimize_keyword_placement,
    calculate_keyword_scores
)
from marketing_project.core.models import ContentContext


class TestExtractPrimaryKeywords:
    """Test the extract_primary_keywords function."""
    
    def test_extract_primary_keywords_with_content_context(self, sample_blog_post):
        """Test extracting primary keywords from ContentContext."""
        result = extract_primary_keywords(sample_blog_post, max_keywords=3)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'extract_primary_keywords'
        
        data = result['data']
        assert 'primary_keywords' in data
        assert 'total_keywords_found' in data
        assert 'filtered_words_count' in data
        
        keywords = data['primary_keywords']
        assert len(keywords) <= 3
        assert all('keyword' in kw for kw in keywords)
        assert all('frequency' in kw for kw in keywords)
        assert all('score' in kw for kw in keywords)
        assert all('in_title' in kw for kw in keywords)
        assert all('density' in kw for kw in keywords)
    
    def test_extract_primary_keywords_with_dict(self, sample_article_data):
        """Test extracting primary keywords from dictionary."""
        result = extract_primary_keywords(sample_article_data, max_keywords=5)
        
        assert result['success'] is True
        data = result['data']
        assert len(data['primary_keywords']) <= 5
    
    def test_extract_primary_keywords_title_boost(self, sample_blog_post):
        """Test that keywords in title get score boost."""
        sample_blog_post.title = "Artificial Intelligence and Machine Learning Guide"
        sample_blog_post.content = "This is about artificial intelligence and machine learning. AI is important."
        
        result = extract_primary_keywords(sample_blog_post, max_keywords=3)
        
        assert result['success'] is True
        keywords = result['data']['primary_keywords']
        
        # Keywords in title should have higher scores
        title_keywords = [kw for kw in keywords if kw['in_title']]
        assert len(title_keywords) > 0
        
        for kw in title_keywords:
            assert kw['score'] > 0
    
    def test_extract_primary_keywords_filters_stop_words(self, sample_blog_post):
        """Test that stop words are filtered out."""
        sample_blog_post.title = "The Best Guide"
        sample_blog_post.content = "This is the best guide for the users. The content is good."
        
        result = extract_primary_keywords(sample_blog_post, max_keywords=10)
        
        assert result['success'] is True
        keywords = result['data']['primary_keywords']
        keyword_words = [kw['keyword'] for kw in keywords]
        
        # Common stop words should be filtered out
        stop_words = ['the', 'is', 'for', 'and', 'this', 'a', 'an']
        for stop_word in stop_words:
            assert stop_word not in keyword_words
    
    def test_extract_primary_keywords_invalid_content(self):
        """Test extracting keywords from invalid content."""
        from marketing_project.core.models import BlogPostContext
        invalid_content = BlogPostContext(
            id="test",
            title="",  # Empty title
            content="",  # Empty content
            snippet=""  # Empty snippet
        )
        
        result = extract_primary_keywords(invalid_content)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Content validation failed' in result['error']
    
    def test_extract_primary_keywords_error_handling(self):
        """Test error handling in extract_primary_keywords."""
        with patch('marketing_project.plugins.seo_keywords.tasks.ensure_content_context') as mock_ensure:
            mock_ensure.side_effect = Exception("Test error")
            
            result = extract_primary_keywords({})
            assert result['success'] is False
            assert 'Keyword extraction failed' in result['error']


class TestExtractSecondaryKeywords:
    """Test the extract_secondary_keywords function."""
    
    def test_extract_secondary_keywords_with_phrases(self, sample_blog_post):
        """Test extracting secondary keywords with phrases."""
        primary_keywords = ['artificial', 'intelligence', 'machine', 'learning']
        
        result = extract_secondary_keywords(sample_blog_post, primary_keywords, max_keywords=5)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'extract_secondary_keywords'
        
        data = result['data']
        assert 'secondary_keywords' in data
        assert 'total_secondary_found' in data
        assert 'primary_keywords_used' in data
        
        secondary_keywords = data['secondary_keywords']
        assert len(secondary_keywords) <= 5
        assert all('keyword' in kw for kw in secondary_keywords)
        assert all('related_to' in kw for kw in secondary_keywords)
        assert all('type' in kw for kw in secondary_keywords)
        assert all('frequency' in kw for kw in secondary_keywords)
    
    def test_extract_secondary_keywords_with_synonyms(self, sample_blog_post):
        """Test extracting secondary keywords with synonyms."""
        sample_blog_post.content = "This is the best guide with excellent tips and recommendations."
        primary_keywords = ['best', 'guide', 'tips']
        
        result = extract_secondary_keywords(sample_blog_post, primary_keywords, max_keywords=10)
        
        assert result['success'] is True
        secondary_keywords = result['data']['secondary_keywords']
        
        # Should find synonyms
        synonym_keywords = [kw for kw in secondary_keywords if kw['type'] == 'synonym']
        assert len(synonym_keywords) > 0
    
    def test_extract_secondary_keywords_invalid_content(self):
        """Test extracting secondary keywords from invalid content."""
        from marketing_project.core.models import BlogPostContext
        invalid_content = BlogPostContext(
            id="test",
            title="",
            content="",
            snippet=""
        )
        
        result = extract_secondary_keywords(invalid_content, ['test'])
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Content validation failed' in result['error']


class TestAnalyzeKeywordDensity:
    """Test the analyze_keyword_density function."""
    
    def test_analyze_keyword_density_optimal(self, sample_blog_post):
        """Test analyzing keyword density for optimal content."""
        keywords = ['artificial', 'intelligence', 'machine', 'learning']
        
        result = analyze_keyword_density(sample_blog_post, keywords)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'analyze_keyword_density'
        
        data = result['data']
        assert 'total_words' in data
        assert 'keyword_densities' in data
        assert 'keyword_positions' in data
        assert 'recommendations' in data
        
        # Check keyword density analysis
        for keyword in keywords:
            assert keyword in data['keyword_densities']
            density_info = data['keyword_densities'][keyword]
            assert 'frequency' in density_info
            assert 'density' in density_info
            assert 'status' in density_info
            assert density_info['status'] in ['optimal', 'needs_optimization']
    
    def test_analyze_keyword_density_low_density(self, sample_blog_post):
        """Test analyzing keyword density for low density content."""
        # Create content with very low keyword density
        sample_blog_post.content = "This is a very long article about many different topics and concepts that are not related to our target keywords at all."
        keywords = ['artificial', 'intelligence']
        
        result = analyze_keyword_density(sample_blog_post, keywords)
        
        assert result['success'] is True
        data = result['data']
        
        # Should recommend increasing density
        recommendations = data['recommendations']
        assert any('Increase' in rec for rec in recommendations)
    
    def test_analyze_keyword_density_high_density(self, sample_blog_post):
        """Test analyzing keyword density for high density content."""
        # Create content with very high keyword density
        sample_blog_post.content = "artificial intelligence artificial intelligence artificial intelligence " * 10
        keywords = ['artificial', 'intelligence']
        
        result = analyze_keyword_density(sample_blog_post, keywords)
        
        assert result['success'] is True
        data = result['data']
        
        # Should recommend reducing density
        recommendations = data['recommendations']
        assert any('Reduce' in rec for rec in recommendations)
    
    def test_analyze_keyword_density_invalid_content(self):
        """Test analyzing keyword density for invalid content."""
        from marketing_project.core.models import BlogPostContext
        invalid_content = BlogPostContext(
            id="test",
            title="",
            content="",
            snippet=""
        )
        
        result = analyze_keyword_density(invalid_content, ['test'])
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Content validation failed' in result['error']


class TestGenerateKeywordSuggestions:
    """Test the generate_keyword_suggestions function."""
    
    def test_generate_keyword_suggestions_industry_specific(self, sample_blog_post):
        """Test generating industry-specific keyword suggestions."""
        result = generate_keyword_suggestions(
            sample_blog_post, 
            industry='technology', 
            target_audience='professionals'
        )
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'generate_keyword_suggestions'
        
        data = result['data']
        assert 'suggestions' in data
        assert 'total_suggestions' in data
        assert 'industry' in data
        assert 'target_audience' in data
        
        suggestions = data['suggestions']
        assert len(suggestions) <= 10
        assert all('keyword' in s for s in suggestions)
        assert all('type' in s for s in suggestions)
        assert all('relevance_score' in s for s in suggestions)
        assert all('suggestion_reason' in s for s in suggestions)
    
    def test_generate_keyword_suggestions_long_tail(self, sample_blog_post):
        """Test generating long-tail keyword suggestions."""
        sample_blog_post.content = "artificial intelligence machine learning data science automation technology innovation"
        
        result = generate_keyword_suggestions(sample_blog_post)
        
        assert result['success'] is True
        suggestions = result['data']['suggestions']
        
        # Should find long-tail keywords
        long_tail_keywords = [s for s in suggestions if s['type'] == 'long_tail']
        assert len(long_tail_keywords) > 0
    
    def test_generate_keyword_suggestions_audience_specific(self, sample_blog_post):
        """Test generating audience-specific keyword suggestions."""
        result = generate_keyword_suggestions(
            sample_blog_post,
            target_audience='beginners'
        )
        
        assert result['success'] is True
        suggestions = result['data']['suggestions']
        
        # Should find audience-specific keywords
        audience_keywords = [s for s in suggestions if s['type'] == 'audience']
        assert len(audience_keywords) > 0
    
    def test_generate_keyword_suggestions_invalid_content(self):
        """Test generating keyword suggestions for invalid content."""
        from marketing_project.core.models import BlogPostContext
        invalid_content = BlogPostContext(
            id="test",
            title="",
            content="",
            snippet=""
        )
        
        result = generate_keyword_suggestions(invalid_content)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Content validation failed' in result['error']


class TestOptimizeKeywordPlacement:
    """Test the optimize_keyword_placement function."""
    
    def test_optimize_keyword_placement(self, sample_blog_post):
        """Test optimizing keyword placement."""
        keywords = ['artificial', 'intelligence', 'machine', 'learning']
        
        result = optimize_keyword_placement(sample_blog_post, keywords)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'optimize_keyword_placement'
        
        data = result['data']
        assert 'title_optimization' in data
        assert 'heading_optimization' in data
        assert 'content_optimization' in data
        assert 'meta_optimization' in data
        assert 'recommendations' in data
        
        # Check optimization for each keyword
        for keyword in keywords:
            assert keyword in data['title_optimization']
            assert keyword in data['heading_optimization']
            assert keyword in data['content_optimization']
    
    def test_optimize_keyword_placement_missing_keywords(self, sample_blog_post):
        """Test optimizing keyword placement when keywords are missing."""
        keywords = ['nonexistent', 'keywords']
        
        result = optimize_keyword_placement(sample_blog_post, keywords)
        
        assert result['success'] is True
        data = result['data']
        
        # Should recommend adding missing keywords
        recommendations = data['recommendations']
        assert any('Consider adding' in rec for rec in recommendations)
    
    def test_optimize_keyword_placement_invalid_content(self):
        """Test optimizing keyword placement for invalid content."""
        from marketing_project.core.models import BlogPostContext
        invalid_content = BlogPostContext(
            id="test",
            title="",
            content="",
            snippet=""
        )
        
        result = optimize_keyword_placement(invalid_content, ['test'])
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Content validation failed' in result['error']


class TestCalculateKeywordScores:
    """Test the calculate_keyword_scores function."""
    
    def test_calculate_keyword_scores(self, sample_blog_post, sample_seo_keywords):
        """Test calculating keyword scores."""
        result = calculate_keyword_scores(sample_seo_keywords, sample_blog_post)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'calculate_keyword_scores'
        
        data = result['data']
        assert 'scored_keywords' in data
        assert 'high_priority_count' in data
        assert 'medium_priority_count' in data
        assert 'low_priority_count' in data
        
        scored_keywords = data['scored_keywords']
        assert len(scored_keywords) == len(sample_seo_keywords)
        
        # Check that all keywords have scores
        for keyword in scored_keywords:
            assert 'relevance_score' in keyword
            assert 'difficulty_score' in keyword
            assert 'overall_score' in keyword
            assert 'priority' in keyword
            assert keyword['priority'] in ['high', 'medium', 'low']
    
    def test_calculate_keyword_scores_high_priority(self, sample_blog_post):
        """Test calculating scores for high-priority keywords."""
        high_priority_keywords = [
            {'keyword': 'artificial intelligence', 'frequency': 20, 'in_title': True, 'density': 2.5},
            {'keyword': 'machine learning', 'frequency': 15, 'in_title': True, 'density': 2.0}
        ]
        
        result = calculate_keyword_scores(high_priority_keywords, sample_blog_post)
        
        assert result['success'] is True
        scored_keywords = result['data']['scored_keywords']
        
        # High-priority keywords should have high overall scores
        for keyword in scored_keywords:
            if keyword['keyword'] in ['artificial intelligence', 'machine learning']:
                assert keyword['overall_score'] > 0.5
                assert keyword['priority'] in ['high', 'medium']
    
    def test_calculate_keyword_scores_invalid_content(self):
        """Test calculating keyword scores for invalid content."""
        from marketing_project.core.models import BlogPostContext
        invalid_content = BlogPostContext(
            id="test",
            title="",
            content="",
            snippet=""
        )
        
        result = calculate_keyword_scores([{'keyword': 'test'}], invalid_content)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Content validation failed' in result['error']


class TestIntegration:
    """Test integration between functions."""
    
    def test_full_seo_keywords_workflow(self, sample_blog_post):
        """Test the full SEO keywords workflow."""
        # Step 1: Extract primary keywords
        primary_result = extract_primary_keywords(sample_blog_post, max_keywords=5)
        assert primary_result['success'] is True
        
        primary_keywords = primary_result['data']['primary_keywords']
        primary_keyword_list = [kw['keyword'] for kw in primary_keywords]
        
        # Step 2: Extract secondary keywords
        secondary_result = extract_secondary_keywords(sample_blog_post, primary_keyword_list, max_keywords=10)
        assert secondary_result['success'] is True
        
        # Step 3: Analyze keyword density
        density_result = analyze_keyword_density(sample_blog_post, primary_keyword_list)
        assert density_result['success'] is True
        
        # Step 4: Generate keyword suggestions
        suggestions_result = generate_keyword_suggestions(
            sample_blog_post, 
            industry='technology', 
            target_audience='professionals'
        )
        assert suggestions_result['success'] is True
        
        # Step 5: Optimize keyword placement
        placement_result = optimize_keyword_placement(sample_blog_post, primary_keyword_list)
        assert placement_result['success'] is True
        
        # Step 6: Calculate keyword scores
        scores_result = calculate_keyword_scores(primary_keywords, sample_blog_post)
        assert scores_result['success'] is True
        
        # Verify all results have expected structure
        assert 'primary_keywords' in primary_result['data']
        assert 'secondary_keywords' in secondary_result['data']
        assert 'keyword_densities' in density_result['data']
        assert 'suggestions' in suggestions_result['data']
        assert 'recommendations' in placement_result['data']
        assert 'scored_keywords' in scores_result['data']


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_extract_primary_keywords_empty_content(self):
        """Test extracting keywords from empty content."""
        from marketing_project.core.models import BlogPostContext
        empty_content = BlogPostContext(
            id="test",
            title="Empty",
            content="",
            snippet="Empty"
        )
        
        result = extract_primary_keywords(empty_content)
        
        assert result['success'] is True
        assert len(result['data']['primary_keywords']) == 0
    
    def test_analyze_keyword_density_empty_keywords(self, sample_blog_post):
        """Test analyzing keyword density with empty keywords list."""
        result = analyze_keyword_density(sample_blog_post, [])
        
        assert result['success'] is True
        assert result['data']['keyword_densities'] == {}
        assert result['data']['recommendations'] == []
    
    def test_generate_keyword_suggestions_unknown_industry(self, sample_blog_post):
        """Test generating suggestions for unknown industry."""
        result = generate_keyword_suggestions(sample_blog_post, industry='unknown')
        
        assert result['success'] is True
        # Should still generate suggestions based on content
        assert len(result['data']['suggestions']) > 0
    
    def test_calculate_keyword_scores_empty_keywords(self, sample_blog_post):
        """Test calculating scores for empty keywords list."""
        result = calculate_keyword_scores([], sample_blog_post)
        
        assert result['success'] is True
        assert result['data']['scored_keywords'] == []
        assert result['data']['high_priority_count'] == 0
        assert result['data']['medium_priority_count'] == 0
        assert result['data']['low_priority_count'] == 0
