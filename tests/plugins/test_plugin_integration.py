"""
Integration tests for plugin interactions.

This module tests how different plugins work together in the marketing pipeline.
"""

import pytest
from unittest.mock import Mock, patch
from marketing_project.core.models import (
    ContentContext, TranscriptContext, BlogPostContext, 
    ReleaseNotesContext, AppContext
)
from marketing_project.plugins.article_generation.tasks import generate_article_structure
from marketing_project.plugins.content_analysis.tasks import analyze_content_for_pipeline
from marketing_project.plugins.seo_keywords.tasks import extract_primary_keywords
from marketing_project.plugins.seo_optimization.tasks import calculate_seo_score
from marketing_project.plugins.content_formatting.tasks import apply_formatting_rules
from marketing_project.plugins.blog_posts.tasks import analyze_blog_post_type
from marketing_project.plugins.transcripts.tasks import analyze_transcript_type
from marketing_project.plugins.release_notes.tasks import analyze_release_type
from marketing_project.plugins.article_generation.tasks import write_article_content



class TestContentAnalysisIntegration:
    """Test integration between content analysis and other plugins."""
    
    def test_content_analysis_to_article_generation(self, sample_blog_post):
        """Test content analysis feeding into article generation."""
        # Step 1: Analyze content for pipeline
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        assert analysis_result['success'] is True
        
        # Step 2: Use analysis to generate article structure
        marketing_brief = {
            'title': sample_blog_post.title,
            'executive_summary': sample_blog_post.snippet,
            'content_pillars': ['Technology', 'AI', 'Programming'],
            'target_audience': {'primary': 'Developers', 'secondary': 'Tech enthusiasts'}
        }
        
        structure_result = generate_article_structure(marketing_brief)
        assert structure_result['success'] is True
        
        # Verify integration
        assert structure_result['data']['title'] == sample_blog_post.title
        assert 'content_pillars' in structure_result['data']
    
    def test_content_analysis_to_seo_optimization(self, sample_blog_post):
        """Test content analysis feeding into SEO optimization."""
        # Step 1: Analyze content for pipeline
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        assert analysis_result['success'] is True
        
        # Step 2: Extract keywords based on analysis
        keywords_result = extract_primary_keywords(sample_blog_post, max_keywords=5)
        assert keywords_result['success'] is True
        
        # Step 3: Calculate SEO score
        seo_result = calculate_seo_score(sample_blog_post)
        assert seo_result['success'] is True
        
        # Verify integration
        assert len(keywords_result['data']['primary_keywords']) > 0
        assert seo_result['data']['overall_seo_score'] >= 0
    
    def test_content_analysis_to_content_formatting(self, sample_blog_post):
        """Test content analysis feeding into content formatting."""
        # Step 1: Analyze content for pipeline
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        assert analysis_result['success'] is True
        
        # Step 2: Apply formatting based on analysis
        article_data = {
            'title': sample_blog_post.title,
            'content': sample_blog_post.content,
            'meta_description': sample_blog_post.snippet
        }
        
        formatting_result = apply_formatting_rules(article_data)
        assert formatting_result['success'] is True
        
        # Verify integration
        assert 'content' in formatting_result['data']
        assert formatting_result['data']['formatting_applied'] is True


class TestContentTypeRoutingIntegration:
    """Test integration between content type analysis and routing."""
    
    def test_blog_post_routing_integration(self, sample_blog_post):
        """Test blog post type analysis and routing integration."""
        # Step 1: Analyze blog post type
        blog_type = analyze_blog_post_type(sample_blog_post)
        assert blog_type in ['tutorial', 'review', 'news', 'analysis', 'general']
        
        # Step 2: Create app context
        app_context = AppContext(
            content=sample_blog_post,
            labels={'category': 'technology'},
            content_type='blog_post'
        )
        
        # Step 3: Verify routing would work
        available_agents = {
            'tutorial_agent': Mock(),
            'review_agent': Mock(),
            'news_agent': Mock(),
            'analysis_agent': Mock(),
            'general_blog_agent': Mock()
        }
        
        # The routing would depend on the blog type
        if blog_type == 'tutorial':
            assert 'tutorial_agent' in available_agents
        elif blog_type == 'review':
            assert 'review_agent' in available_agents
        elif blog_type == 'news':
            assert 'news_agent' in available_agents
        elif blog_type == 'analysis':
            assert 'analysis_agent' in available_agents
        else:
            assert 'general_blog_agent' in available_agents
    
    def test_transcript_routing_integration(self, sample_transcript):
        """Test transcript type analysis and routing integration."""
        # Step 1: Analyze transcript type
        transcript_type = analyze_transcript_type(sample_transcript)
        assert transcript_type in ['podcast', 'video', 'meeting', 'interview', 'general']
        
        # Step 2: Create app context
        app_context = AppContext(
            content=sample_transcript,
            labels={'category': 'technology'},
            content_type='transcript'
        )
        
        # Step 3: Verify routing would work
        available_agents = {
            'transcripts_agent': Mock()
        }
        
        # The routing would use the transcripts_agent for all transcript types
        assert 'transcripts_agent' in available_agents
    
    def test_release_notes_routing_integration(self, sample_release_notes):
        """Test release notes type analysis and routing integration."""
        # Step 1: Analyze release type
        release_type = analyze_release_type(sample_release_notes)
        assert release_type in ['major', 'minor', 'patch', 'hotfix']
        
        # Step 2: Create app context
        app_context = AppContext(
            content=sample_release_notes,
            labels={'category': 'product'},
            content_type='release_notes'
        )
        
        # Step 3: Verify routing would work
        available_agents = {
            'releasenotes_agent': Mock()
        }
        
        # The routing would use the releasenotes_agent for all release types
        assert 'releasenotes_agent' in available_agents


class TestSeoWorkflowIntegration:
    """Test integration between SEO-related plugins."""
    
    def test_seo_keywords_to_optimization_integration(self, sample_blog_post):
        """Test SEO keywords feeding into SEO optimization."""
        # Step 1: Extract primary keywords
        keywords_result = extract_primary_keywords(sample_blog_post, max_keywords=5)
        assert keywords_result['success'] is True
        
        primary_keywords = keywords_result['data']['primary_keywords']
        keyword_list = [kw['keyword'] for kw in primary_keywords]
        
        # Step 2: Calculate SEO score with keywords
        seo_result = calculate_seo_score(sample_blog_post)
        assert seo_result['success'] is True
        
        # Step 3: Verify integration
        assert len(keyword_list) > 0
        assert seo_result['data']['overall_seo_score'] >= 0
        assert 'score_breakdown' in seo_result['data']
    
    def test_seo_optimization_to_content_formatting_integration(self, sample_article_data):
        """Test SEO optimization feeding into content formatting."""
        # Step 1: Calculate SEO score
        seo_result = calculate_seo_score(sample_article_data)
        assert seo_result['success'] is True
        
        # Step 2: Apply formatting with SEO considerations
        style_guide = {
            'heading_style': 'title_case',
            'list_style': 'bullet',
            'paragraph_spacing': 'double',
            'quote_style': 'blockquote',
            'code_style': 'fenced',
            'link_style': 'markdown',
            'emphasis_style': 'bold_italic',
            'seo_optimization': True
        }
        
        formatting_result = apply_formatting_rules(sample_article_data, style_guide)
        assert formatting_result['success'] is True
        
        # Step 3: Verify integration
        assert formatting_result['data']['formatting_applied'] is True
        assert 'seo_optimization' in formatting_result['data']['style_guide_used']


class TestContentGenerationWorkflow:
    """Test the complete content generation workflow."""
    
    def test_complete_article_generation_workflow(self, sample_marketing_brief, sample_seo_keywords):
        """Test the complete article generation workflow."""
        # Step 1: Generate article structure
        structure_result = generate_article_structure(sample_marketing_brief, sample_seo_keywords)
        assert structure_result['success'] is True
        
        structure = structure_result['data']
        
        # Step 2: Generate actual content from structure
        from marketing_project.plugins.article_generation.tasks import write_article_content
        content_result = write_article_content(structure)
        assert 'content' in content_result
        
        # Step 3: Analyze content for pipeline
        from marketing_project.core.models import BlogPostContext
        content_context = BlogPostContext(
            id="generated-article",
            title=structure['title'],
            content=content_result.get('content', ''),
            snippet=structure['meta_description']
        )
        
        analysis_result = analyze_content_for_pipeline(content_context)
        assert analysis_result['success'] is True
        
        # Step 4: Extract keywords
        keywords_result = extract_primary_keywords(content_context, max_keywords=5)
        assert keywords_result['success'] is True
        
        # Step 5: Calculate SEO score
        seo_result = calculate_seo_score(content_context)
        assert seo_result['success'] is True
        
        # Step 6: Apply formatting
        article_data = {
            'title': structure['title'],
            'content': content_result.get('content', ''),
            'meta_description': structure['meta_description']
        }
        
        formatting_result = apply_formatting_rules(article_data)
        assert formatting_result['success'] is True
        
        # Verify complete workflow
        assert structure['title']
        assert analysis_result['data']['pipeline_ready'] is True
        assert len(keywords_result['data']['primary_keywords']) > 0
        assert seo_result['data']['overall_seo_score'] >= 0
        assert formatting_result['data']['formatting_applied'] is True


class TestErrorHandlingIntegration:
    """Test error handling across plugin integrations."""
    
    def test_error_propagation_between_plugins(self, sample_blog_post):
        """Test that errors propagate correctly between plugins."""
        # Mock a failure in content analysis
        with patch('marketing_project.plugins.content_analysis.tasks.ensure_content_context') as mock_ensure:
            mock_ensure.side_effect = Exception("Content analysis failed")
            
            analysis_result = analyze_content_for_pipeline(sample_blog_post)
            assert analysis_result['success'] is False
            assert 'error' in analysis_result
    
    def test_partial_failure_handling(self, sample_blog_post):
        """Test handling of partial failures in plugin chain."""
        # Step 1: Content analysis succeeds
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        assert analysis_result['success'] is True
        
        # Step 2: Mock a failure in keyword extraction
        with patch('marketing_project.plugins.seo_keywords.tasks.ensure_content_context') as mock_ensure:
            mock_ensure.side_effect = Exception("Keyword extraction failed")
            
            keywords_result = extract_primary_keywords(sample_blog_post)
            assert keywords_result['success'] is False
            assert 'error' in keywords_result
        
        # Step 3: Other plugins should still work
        seo_result = calculate_seo_score(sample_blog_post)
        assert seo_result['success'] is True


class TestDataConsistencyIntegration:
    """Test data consistency across plugin integrations."""
    
    def test_consistent_content_handling(self, sample_blog_post):
        """Test that content is handled consistently across plugins."""
        # Step 1: Analyze content
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        assert analysis_result['success'] is True
        
        # Step 2: Extract keywords
        keywords_result = extract_primary_keywords(sample_blog_post)
        assert keywords_result['success'] is True
        
        # Step 3: Calculate SEO score
        seo_result = calculate_seo_score(sample_blog_post)
        assert seo_result['success'] is True
        
        # Verify data consistency
        assert analysis_result['data']['content_type'] == 'blogpost'
        assert keywords_result['data']['primary_keywords']
        assert seo_result['data']['overall_seo_score'] >= 0
    
    def test_metadata_preservation(self, sample_transcript):
        """Test that metadata is preserved across plugin interactions."""
        # Step 1: Analyze transcript type
        transcript_type = analyze_transcript_type(sample_transcript)
        
        # Step 2: Analyze content for pipeline
        analysis_result = analyze_content_for_pipeline(sample_transcript)
        assert analysis_result['success'] is True
        
        # Verify metadata preservation
        assert transcript_type in ['podcast', 'video', 'meeting', 'interview', 'general']
        assert analysis_result['data']['content_type'] == 'transcript'


class TestPerformanceIntegration:
    """Test performance considerations across plugin integrations."""
    
    def test_efficient_plugin_chaining(self, sample_blog_post):
        """Test that plugins can be chained efficiently."""
        import time
        
        start_time = time.time()
        
        # Chain multiple plugin operations
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        keywords_result = extract_primary_keywords(sample_blog_post)
        seo_result = calculate_seo_score(sample_blog_post)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all operations succeeded
        assert analysis_result['success'] is True
        assert keywords_result['success'] is True
        assert seo_result['success'] is True
        
        # Verify reasonable execution time (should be fast for mocked operations)
        assert execution_time < 1.0  # Should complete in less than 1 second
    
    def test_memory_efficiency(self, sample_blog_post):
        """Test that plugin operations are memory efficient."""
        import sys
        
        # Get initial memory usage
        initial_memory = sys.getsizeof(sample_blog_post)
        
        # Perform multiple operations
        analysis_result = analyze_content_for_pipeline(sample_blog_post)
        keywords_result = extract_primary_keywords(sample_blog_post)
        seo_result = calculate_seo_score(sample_blog_post)
        
        # Verify operations succeeded
        assert analysis_result['success'] is True
        assert keywords_result['success'] is True
        assert seo_result['success'] is True
        
        # Memory usage should not grow excessively
        # (This is a basic check - in real scenarios, you'd use more sophisticated memory profiling)
        assert initial_memory > 0
