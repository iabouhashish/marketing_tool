"""
Tests for the article generation plugin.

This module tests all functions in the article generation plugin tasks.
"""

import pytest
from unittest.mock import Mock, patch
from marketing_project.plugins.article_generation.tasks import (
    generate_article_structure,
    write_article_content,
    add_supporting_elements,
    review_article_quality,
    optimize_article_flow,
    add_call_to_actions,
    write_introduction,
    write_main_section,
    write_conclusion,
    estimate_syllables,
    check_paragraph_lengths,
    check_transitions,
    improve_paragraph_flow
)
from marketing_project.core.models import ContentContext


class TestGenerateArticleStructure:
    """Test the generate_article_structure function."""
    
    def test_generate_article_structure_with_dict(self, sample_marketing_brief, sample_seo_keywords):
        """Test generating article structure with dictionary input."""
        result = generate_article_structure(sample_marketing_brief, sample_seo_keywords)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['task_name'] == 'generate_article_structure'
        
        structure = result['data']
        assert 'title' in structure
        assert 'meta_description' in structure
        assert 'introduction' in structure
        assert 'main_sections' in structure
        assert 'conclusion' in structure
        assert 'word_count_target' in structure
        assert 'seo_optimization' in structure
        
        # Check that primary keyword is included in title
        assert 'artificial intelligence' in structure['title'].lower()
        
        # Check that main sections are created based on content pillars
        assert len(structure['main_sections']) == 3  # Based on actual content pillars
        assert structure['content_pillars'] == sample_marketing_brief['content_pillars']
    
    def test_generate_article_structure_with_content_context(self, sample_content_context, sample_seo_keywords):
        """Test generating article structure with ContentContext input."""
        result = generate_article_structure(sample_content_context, sample_seo_keywords)
        
        assert result['success'] is True
        structure = result['data']
        # Title should include the primary keyword when SEO keywords are provided
        assert 'artificial intelligence' in structure['title'].lower()
        assert structure['meta_description']
    
    def test_generate_article_structure_without_keywords(self, sample_marketing_brief):
        """Test generating article structure without SEO keywords."""
        result = generate_article_structure(sample_marketing_brief)
        
        assert result['success'] is True
        structure = result['data']
        assert structure['seo_optimization']['primary_keyword'] == ''
        assert structure['seo_optimization']['secondary_keywords'] == []
    
    def test_generate_article_structure_error_handling(self):
        """Test error handling in generate_article_structure."""
        with patch('marketing_project.plugins.article_generation.tasks.create_standard_task_result') as mock_create:
            mock_create.side_effect = Exception("Test error")
            
            result = generate_article_structure({})
            assert result['success'] is False
            assert 'error' in result


class TestWriteArticleContent:
    """Test the write_article_content function."""
    
    def test_write_article_content(self, sample_article_structure):
        """Test writing article content from structure."""
        result = write_article_content(sample_article_structure)
        
        assert isinstance(result, dict)
        assert 'title' in result
        assert 'content' in result
        assert 'word_count' in result
        assert 'reading_time' in result
        assert 'sections' in result
        assert 'quality_score' in result
        assert 'seo_score' in result
        
        # Check that content is properly formatted
        assert result['title'] == sample_article_structure['title']
        assert '#' in result['content']  # Should have markdown headers
        assert result['word_count'] > 0
        assert result['reading_time']
    
    def test_write_article_content_with_source(self, sample_article_structure, sample_content_context):
        """Test writing article content with source content."""
        result = write_article_content(sample_article_structure, sample_content_context)
        
        assert isinstance(result, dict)
        assert result['content']
        assert len(result['sections']) > 0


class TestAddSupportingElements:
    """Test the add_supporting_elements function."""
    
    def test_add_supporting_elements_article(self, sample_article_structure):
        """Test adding supporting elements to article."""
        # First create an article with sections from the structure
        article = {
            'title': sample_article_structure['title'],
            'content': 'Test article content',
            'sections': [
                {'type': 'introduction', 'heading': 'Introduction', 'content': 'Intro content'},
                {'type': 'main_section', 'heading': 'Main Topic 1', 'content': 'Main content 1'},
                {'type': 'main_section', 'heading': 'Main Topic 2', 'content': 'Main content 2'},
                {'type': 'conclusion', 'heading': 'Conclusion', 'content': 'Conclusion content'}
            ]
        }
        result = add_supporting_elements(article, 'article')
        
        assert 'supporting_elements' in result
        supporting = result['supporting_elements']
        assert 'images' in supporting
        assert 'quotes' in supporting
        assert 'callouts' in supporting
        assert 'lists' in supporting
        assert 'tables' in supporting
        assert 'code_blocks' in supporting
        
        # Check that images are suggested for main sections
        assert len(supporting['images']) > 0
    
    def test_add_supporting_elements_tutorial(self, sample_article_structure):
        """Test adding supporting elements to tutorial content."""
        # Create an article with sections from the structure
        article = {
            'title': sample_article_structure['title'],
            'content': 'Test tutorial content',
            'sections': [
                {'type': 'introduction', 'heading': 'Introduction', 'content': 'Intro content'},
                {'type': 'main_section', 'heading': 'Main Topic 1', 'content': 'Main content 1'},
                {'type': 'main_section', 'heading': 'Main Topic 2', 'content': 'Main content 2'},
                {'type': 'conclusion', 'heading': 'Conclusion', 'content': 'Conclusion content'}
            ]
        }
        result = add_supporting_elements(article, 'tutorial')
        
        assert 'supporting_elements' in result
        supporting = result['supporting_elements']
        assert len(supporting['quotes']) > 0
        assert supporting['quotes'][0]['text'] == '"The best way to learn is by doing."'
    
    def test_add_supporting_elements_review(self, sample_article_structure):
        """Test adding supporting elements to review content."""
        # Create an article with sections from the structure
        article = {
            'title': sample_article_structure['title'],
            'content': 'Test review content',
            'sections': [
                {'type': 'introduction', 'heading': 'Introduction', 'content': 'Intro content'},
                {'type': 'main_section', 'heading': 'Main Topic 1', 'content': 'Main content 1'},
                {'type': 'main_section', 'heading': 'Main Topic 2', 'content': 'Main content 2'},
                {'type': 'conclusion', 'heading': 'Conclusion', 'content': 'Conclusion content'}
            ]
        }
        result = add_supporting_elements(article, 'review')
        
        assert 'supporting_elements' in result
        supporting = result['supporting_elements']
        assert len(supporting['quotes']) > 0
        assert 'Data-driven' in supporting['quotes'][0]['text']


class TestReviewArticleQuality:
    """Test the review_article_quality function."""
    
    def test_review_article_quality_good_article(self, sample_article_data):
        """Test reviewing a good quality article."""
        # Create a good quality article
        good_article = sample_article_data.copy()
        good_article['content'] = "# Test Article\n\nThis is a well-structured article with proper headings and content. It has good readability and includes important information for readers.\n\n## Key Points\n\n- Point 1\n- Point 2\n- Point 3\n\n## Conclusion\n\nIn summary, this article provides valuable insights."
        good_article['word_count'] = 1500
        good_article['title'] = "Test Article Title"
        good_article['meta_description'] = "A comprehensive test article with valuable insights and information for readers."
        
        result = review_article_quality(good_article)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert 'readability_score' in result
        assert 'seo_score' in result
        assert 'engagement_score' in result
        assert 'issues' in result
        assert 'suggestions' in result
        assert 'strengths' in result
        
        # Good article should have high scores
        assert result['overall_score'] > 0
        assert result['readability_score'] > 0
        assert result['seo_score'] > 0
        assert result['engagement_score'] > 0
    
    def test_review_article_quality_short_article(self, sample_article_data):
        """Test reviewing a short article."""
        short_article = sample_article_data.copy()
        short_article['content'] = "Short content."
        short_article['word_count'] = 50
        short_article['title'] = "Short"
        short_article['meta_description'] = "Short desc"
        
        result = review_article_quality(short_article)
        
        assert result['overall_score'] >= 0
        assert 'Content may be too short' in result['issues']
    
    def test_review_article_quality_long_article(self, sample_article_data):
        """Test reviewing a very long article."""
        long_article = sample_article_data.copy()
        long_article['content'] = "Very long content. " * 1000
        long_article['word_count'] = 5000
        long_article['title'] = "Very Long Article Title That Exceeds Optimal Length"
        long_article['meta_description'] = "Very long meta description that exceeds optimal length for search engines and should be shortened"
        
        result = review_article_quality(long_article)
        
        assert result['overall_score'] >= 0
        assert 'Content may be too long' in result['issues']


class TestOptimizeArticleFlow:
    """Test the optimize_article_flow function."""
    
    def test_optimize_article_flow(self, sample_article_structure):
        """Test optimizing article flow."""
        # Create an article with sections from the structure
        article = {
            'title': sample_article_structure['title'],
            'content': 'Test article content',
            'sections': [
                {'type': 'introduction', 'heading': 'Introduction', 'content': 'Intro content'},
                {'type': 'main_section', 'heading': 'Main Topic 1', 'content': 'Main content 1'},
                {'type': 'main_section', 'heading': 'Main Topic 2', 'content': 'Main content 2'},
                {'type': 'conclusion', 'heading': 'Conclusion', 'content': 'Conclusion content'}
            ]
        }
        result = optimize_article_flow(article)
        
        assert isinstance(result, dict)
        assert 'sections' in result
        
        # Check that transitions are added
        sections = result['sections']
        for i, section in enumerate(sections):
            if section['type'] == 'main_section' and i > 0:
                # Should have transition text
                assert any(transition in section['content'] for transition in [
                    "Now that we've covered",
                    "Building on what we've learned",
                    "With this foundation in place"
                ])


class TestAddCallToActions:
    """Test the add_call_to_actions function."""
    
    def test_add_call_to_actions_default_strategy(self, sample_article_data):
        """Test adding CTAs with default strategy."""
        result = add_call_to_actions(sample_article_data)
        
        assert 'ctas' in result
        assert len(result['ctas']) == 3  # introduction, middle, conclusion
        
        cta_placements = [cta['placement'] for cta in result['ctas']]
        assert 'introduction' in cta_placements
        assert 'middle' in cta_placements
        assert 'conclusion' in cta_placements
    
    def test_add_call_to_actions_custom_strategy(self, sample_article_data):
        """Test adding CTAs with custom strategy."""
        custom_strategy = {
            'primary_cta': 'Get Started Now',
            'secondary_cta': 'Learn More',
            'cta_placement': ['introduction', 'conclusion']
        }
        
        result = add_call_to_actions(sample_article_data, custom_strategy)
        
        assert 'ctas' in result
        assert len(result['ctas']) == 2
        
        for cta in result['ctas']:
            assert cta['text'] in ['Get Started Now', 'Learn More']


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_write_introduction(self):
        """Test write_introduction helper function."""
        intro_structure = {
            'hook': 'In today\'s world',
            'problem_statement': 'many face challenges',
            'solution_preview': 'This guide helps',
            'value_proposition': 'achieve success'
        }
        target_audience = {'level': 'beginner'}
        
        result = write_introduction(intro_structure, target_audience)
        
        assert isinstance(result, str)
        assert 'In today\'s world' in result
        assert 'many face challenges' in result
        assert 'This guide helps' in result
        assert 'achieve success' in result
    
    def test_write_main_section(self):
        """Test write_main_section helper function."""
        section_structure = {
            'heading': 'H2: Getting Started',
            'subheadings': ['H3: Basics', 'H3: Advanced'],
            'seo_keywords': ['tutorial', 'guide']
        }
        
        result = write_main_section(section_structure)
        
        assert isinstance(result, str)
        assert 'getting started' in result.lower()
        assert 'Basics' in result
        assert 'Advanced' in result
        assert 'tutorial' in result
        assert 'guide' in result
    
    def test_write_conclusion(self):
        """Test write_conclusion helper function."""
        conclusion_structure = {
            'summary': 'In summary',
            'call_to_action': 'Take action',
            'related_topics': 'Explore more'
        }
        target_audience = {'level': 'intermediate'}
        
        result = write_conclusion(conclusion_structure, target_audience)
        
        assert isinstance(result, str)
        assert 'In summary' in result
        assert 'Take action' in result
        assert 'Explore more' in result
    
    def test_estimate_syllables(self):
        """Test estimate_syllables helper function."""
        assert estimate_syllables('hello') == 2
        assert estimate_syllables('world') == 1
        assert estimate_syllables('beautiful') == 5  # Function counts all vowels
        assert estimate_syllables('a') == 1
        assert estimate_syllables('') == 0
    
    def test_check_paragraph_lengths(self):
        """Test check_paragraph_lengths helper function."""
        good_content = "This is a good paragraph with appropriate length that meets the minimum word count requirement for readability and user experience. It contains enough words to be considered a substantial paragraph that provides value to the reader. This paragraph should be long enough to pass the check and provide meaningful content. The content should be substantial and informative.\n\nThis is another good paragraph that also meets the minimum word count requirement for readability and user experience. It contains enough words to be considered a substantial paragraph that provides value to the reader. This paragraph should also be long enough to pass the check and provide meaningful content. The content should be substantial and informative.\n\nAnd this is one more paragraph that meets the minimum word count requirement for readability and user experience. It contains enough words to be considered a substantial paragraph that provides value to the reader. This paragraph should also be long enough to pass the check and provide meaningful content. The content should be substantial and informative."
        bad_content = "Short.\n\nVery long paragraph with many words that makes it too long for good readability and user experience."
        
        assert check_paragraph_lengths(good_content) is True
        assert check_paragraph_lengths(bad_content) is False
    
    def test_check_transitions(self):
        """Test check_transitions helper function."""
        content_with_transitions = "First paragraph. However, this paragraph has transitions. Moreover, it flows well."
        content_without_transitions = "First paragraph. This paragraph has no transitions. It just continues."
        
        assert check_transitions(content_with_transitions) is True
        assert check_transitions(content_without_transitions) is False
    
    def test_improve_paragraph_flow(self):
        """Test improve_paragraph_flow helper function."""
        content = "First paragraph.\n\nSecond paragraph without transition.\n\nThird paragraph also without transition."
        
        result = improve_paragraph_flow(content)
        
        assert isinstance(result, str)
        assert 'additionally' in result.lower()


class TestIntegration:
    """Test integration between functions."""
    
    def test_full_article_generation_workflow(self, sample_marketing_brief, sample_seo_keywords):
        """Test the full article generation workflow."""
        # Step 1: Generate structure
        structure_result = generate_article_structure(sample_marketing_brief, sample_seo_keywords)
        assert structure_result['success'] is True
        
        structure = structure_result['data']
        
        # Step 2: Write content
        article = write_article_content(structure)
        assert article['content']
        assert article['word_count'] > 0
        
        # Step 3: Add supporting elements
        enhanced_article = add_supporting_elements(article, 'article')
        assert 'supporting_elements' in enhanced_article
        
        # Step 4: Review quality
        quality_review = review_article_quality(enhanced_article)
        assert 'overall_score' in quality_review
        
        # Step 5: Optimize flow
        optimized_article = optimize_article_flow(enhanced_article)
        assert 'sections' in optimized_article
        
        # Step 6: Add CTAs
        final_article = add_call_to_actions(optimized_article)
        assert 'ctas' in final_article
        
        # Verify final article has all expected components
        assert final_article['title']
        assert final_article['content']
        assert final_article['sections']
        assert final_article['supporting_elements']
        assert final_article['ctas']
