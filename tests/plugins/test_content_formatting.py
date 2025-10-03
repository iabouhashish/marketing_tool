"""
Tests for content formatting plugin tasks.

This module tests the core content formatting functions that work with
content to apply styling, structure, and visual elements.
"""

from unittest.mock import Mock, patch

import pytest

from marketing_project.plugins.content_formatting.tasks import (
    add_visual_elements,
    apply_formatting_rules,
    calculate_readability_metrics,
    calculate_reading_time,
    estimate_syllables,
    finalize_content,
    format_code_fenced,
    format_emphasis_bold_italic,
    format_headings_sentence_case,
    format_headings_title_case,
    format_links_markdown,
    format_lists_bullet,
    format_lists_numbered,
    format_paragraph_spacing,
    format_quotes_blockquote,
    generate_publication_ready_content,
    optimize_readability,
    validate_formatting,
)


class TestApplyFormattingRules:
    """Test the apply_formatting_rules function."""

    def test_apply_formatting_rules_with_dict(self, sample_style_guide):
        """Test applying formatting rules with dictionary input."""
        article = {
            "content": "# Test Heading\nThis is test content.",
            "title": "Test Article",
            "meta_description": "Test description",
        }

        result = apply_formatting_rules(article, sample_style_guide)

        assert result["success"] is True
        assert "data" in result
        assert "content" in result["data"]
        assert "formatting_applied" in result["data"]
        assert result["data"]["formatting_applied"] is True

    def test_apply_formatting_rules_with_content_context(
        self, sample_blog_post, sample_style_guide
    ):
        """Test applying formatting rules with ContentContext input."""
        result = apply_formatting_rules(sample_blog_post, sample_style_guide)

        assert result["success"] is True
        assert "data" in result
        assert "content" in result["data"]
        assert "formatting_applied" in result["data"]
        assert result["data"]["formatting_applied"] is True

    def test_apply_formatting_rules_default_style_guide(self):
        """Test applying formatting rules with default style guide."""
        article = {
            "content": "# Test Heading\nThis is test content.",
            "title": "Test Article",
            "meta_description": "Test description",
        }

        result = apply_formatting_rules(article)

        assert result["success"] is True
        assert "data" in result
        assert "style_guide_used" in result["data"]

    def test_apply_formatting_rules_error_handling(self):
        """Test error handling in apply_formatting_rules."""
        # Test with invalid input that should cause an error
        result = apply_formatting_rules(None)

        assert result["success"] is False
        assert "error" in result


class TestOptimizeReadability:
    """Test the optimize_readability function."""

    def test_optimize_readability_with_dict(self):
        """Test optimizing readability with dictionary input."""
        article = {
            "content": "This is a test article with some content for testing purposes.",
            "title": "Test Article",
            "meta_description": "Test description",
        }

        result = optimize_readability(article)

        assert result["success"] is True
        assert "data" in result
        assert "content" in result["data"]
        assert "readability_metrics" in result["data"]

    def test_optimize_readability_with_content_context(self, sample_blog_post):
        """Test optimizing readability with ContentContext input."""
        result = optimize_readability(sample_blog_post)

        assert result["success"] is True
        assert "data" in result
        assert "content" in result["data"]
        assert "readability_metrics" in result["data"]

    def test_optimize_readability_error_handling(self):
        """Test error handling in optimize_readability."""
        # Test with invalid input that should cause an error
        result = optimize_readability(None)

        assert result["success"] is False
        assert "error" in result


class TestAddVisualElements:
    """Test the add_visual_elements function."""

    def test_add_visual_elements_with_dict(self):
        """Test adding visual elements with dictionary input."""
        article = {
            "content": "This is test content with some text.",
            "title": "Test Article",
        }

        result = add_visual_elements(article)

        assert "content" in result
        assert "visual_elements_added" in result
        assert result["visual_elements_added"] is True

    def test_add_visual_elements_with_content_context(self, sample_blog_post):
        """Test adding visual elements with ContentContext input."""
        # Convert ContentContext to dict for the function
        article = {"content": sample_blog_post.content, "title": sample_blog_post.title}

        result = add_visual_elements(article)

        assert "content" in result
        assert "visual_elements_added" in result
        assert result["visual_elements_added"] is True


class TestFinalizeContent:
    """Test the finalize_content function."""

    def test_finalize_content_with_dict(self):
        """Test finalizing content with dictionary input."""
        article = {
            "content": "This is test content.",
            "title": "Test Article",
            "author": "Test Author",
        }

        result = finalize_content(article)

        assert "content" in result
        assert "finalized" in result
        assert result["finalized"] is True

    def test_finalize_content_with_content_context(self, sample_blog_post):
        """Test finalizing content with ContentContext input."""
        # Convert ContentContext to dict for the function
        article = {
            "content": sample_blog_post.content,
            "title": sample_blog_post.title,
            "author": sample_blog_post.author,
        }

        result = finalize_content(article)

        assert "content" in result
        assert "finalized" in result
        assert result["finalized"] is True


class TestValidateFormatting:
    """Test the validate_formatting function."""

    def test_validate_formatting_with_dict(self):
        """Test validating formatting with dictionary input."""
        article = {
            "content": "# Test Heading\n\nThis is test content with proper formatting.",
            "title": "Test Article",
        }

        result = validate_formatting(article)

        assert "overall_score" in result
        assert "issues" in result
        assert "recommendations" in result
        assert isinstance(result["overall_score"], (int, float))

    def test_validate_formatting_with_content_context(self, sample_blog_post):
        """Test validating formatting with ContentContext input."""
        # Convert ContentContext to dict for the function
        article = {"content": sample_blog_post.content, "title": sample_blog_post.title}

        result = validate_formatting(article)

        assert "overall_score" in result
        assert "issues" in result
        assert "recommendations" in result


class TestGeneratePublicationReadyContent:
    """Test the generate_publication_ready_content function."""

    def test_generate_publication_ready_content_with_dict(self):
        """Test generating publication-ready content with dictionary input."""
        article = {
            "content": "This is test content for publication.",
            "title": "Test Article",
            "author": "Test Author",
        }

        result = generate_publication_ready_content(article)

        assert "content" in result
        assert "final_validation" in result
        assert "publication_summary" in result
        assert "word_count" in result["publication_summary"]
        assert "reading_time" in result["publication_summary"]

    def test_generate_publication_ready_content_with_content_context(
        self, sample_blog_post
    ):
        """Test generating publication-ready content with ContentContext input."""
        # Convert ContentContext to dict for the function
        article = {
            "content": sample_blog_post.content,
            "title": sample_blog_post.title,
            "author": sample_blog_post.author,
        }

        result = generate_publication_ready_content(article)

        assert "content" in result
        assert "final_validation" in result
        assert "publication_summary" in result


class TestHelperFunctions:
    """Test helper formatting functions."""

    def test_format_headings_title_case(self):
        """Test formatting headings to title case."""
        content = "# test heading\nSome content here."
        result = format_headings_title_case(content)
        assert "# Test Heading" in result

    def test_format_headings_sentence_case(self):
        """Test formatting headings to sentence case."""
        content = "# TEST HEADING\nSome content here."
        result = format_headings_sentence_case(content)
        assert "# Test heading" in result

    def test_format_lists_bullet(self):
        """Test formatting lists with bullet points."""
        content = "1. First item\n2. Second item"
        result = format_lists_bullet(content)
        assert "- First item" in result
        assert "- Second item" in result

    def test_format_lists_numbered(self):
        """Test formatting lists with numbers."""
        content = "- First item\n- Second item"
        result = format_lists_numbered(content)
        assert "1. First item" in result
        assert "2. Second item" in result

    def test_format_paragraph_spacing(self):
        """Test formatting paragraph spacing."""
        content = "First paragraph.\n\n\nSecond paragraph."
        result = format_paragraph_spacing(content, double=True)
        assert "\n\n" in result

    def test_format_quotes_blockquote(self):
        """Test formatting quotes as blockquotes."""
        content = 'He said "Hello world" to everyone.'
        result = format_quotes_blockquote(content)
        assert "> Hello world" in result

    def test_format_code_fenced(self):
        """Test formatting code with fenced syntax."""
        content = "    def hello():\n        return 'world'"
        result = format_code_fenced(content)
        assert "```" in result

    def test_format_links_markdown(self):
        """Test formatting links in markdown."""
        content = "Visit https://example.com for more info."
        result = format_links_markdown(content)
        assert "[https://example.com](https://example.com)" in result

    def test_format_emphasis_bold_italic(self):
        """Test formatting emphasis with bold and italic."""
        content = "This is *important* text."
        result = format_emphasis_bold_italic(content)
        assert "**important**" in result


class TestReadabilityFunctions:
    """Test readability-related functions."""

    def test_calculate_readability_metrics(self):
        """Test calculating readability metrics."""
        content = "This is a simple sentence. It has good readability. The words are easy to understand."
        result = calculate_readability_metrics(content)

        assert "score" in result
        assert "level" in result
        assert "avg_sentence_length" in result
        assert "avg_syllables_per_word" in result
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 100

    def test_calculate_reading_time(self):
        """Test calculating reading time."""
        content = "This is a test article with some content for testing purposes. " * 10
        result = calculate_reading_time(content)

        assert isinstance(result, str)
        assert "minute" in result

    def test_estimate_syllables(self):
        """Test estimating syllable count."""
        assert estimate_syllables("hello") == 2
        assert estimate_syllables("computer") == 3
        assert estimate_syllables("a") == 1
        assert estimate_syllables("") == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_apply_formatting_rules_empty_content(self):
        """Test applying formatting rules to empty content."""
        article = {"content": "", "title": "Empty Article", "meta_description": ""}

        result = apply_formatting_rules(article)

        assert result["success"] is True
        assert "data" in result
        assert result["data"]["content"] == ""

    def test_optimize_readability_short_content(self):
        """Test optimizing readability for short content."""
        article = {"content": "Short.", "title": "Short Article"}

        result = optimize_readability(article)

        assert result["success"] is True
        assert "data" in result
        assert "readability_metrics" in result["data"]

    def test_add_visual_elements_no_content(self):
        """Test adding visual elements to content with no content."""
        article = {"content": "", "title": "No Content Article"}

        result = add_visual_elements(article)

        assert "content" in result
        assert "visual_elements_added" in result

    def test_validate_formatting_perfect_content(self):
        """Test validating perfectly formatted content."""
        article = {
            "content": "# Perfect Article\n\nThis is perfectly formatted content with proper structure.",
            "title": "Perfect Article",
        }

        result = validate_formatting(article)

        assert "overall_score" in result
        assert "issues" in result
        assert "recommendations" in result
        assert isinstance(result["overall_score"], (int, float))


class TestIntegration:
    """Test integration between formatting functions."""

    def test_full_content_formatting_workflow(
        self, sample_blog_post, sample_style_guide
    ):
        """Test full content formatting workflow."""
        # Convert ContentContext to dict for the functions
        article = {
            "content": sample_blog_post.content,
            "title": sample_blog_post.title,
            "author": sample_blog_post.author,
            "meta_description": "Test description",
        }

        # Apply formatting rules
        formatting_result = apply_formatting_rules(article, sample_style_guide)
        assert formatting_result["success"] is True

        # Optimize readability
        readability_result = optimize_readability(article)
        assert readability_result["success"] is True

        # Add visual elements
        visual_result = add_visual_elements(article)
        assert "visual_elements_added" in visual_result

        # Validate formatting
        validation_result = validate_formatting(article)
        assert "overall_score" in validation_result

        # Generate publication-ready content
        publication_result = generate_publication_ready_content(article)
        assert "publication_summary" in publication_result
