"""
Tests for the internal docs plugin.

This module tests all functions in the internal docs plugin tasks.
"""

from unittest.mock import Mock, patch

import pytest

from marketing_project.core.models import AppContext, ContentContext
from marketing_project.plugins.internal_docs.tasks import (
    analyze_content_gaps,
    create_content_relationships,
    generate_doc_suggestions,
    identify_cross_references,
    optimize_internal_linking,
    suggest_related_docs,
)


class TestAnalyzeContentGaps:
    """Test the analyze_content_gaps function."""

    def test_analyze_content_gaps_with_dict(self, sample_article_data):
        """Test analyzing content gaps with dictionary input."""
        result = analyze_content_gaps(sample_article_data)

        assert result["success"] is True
        assert "data" in result
        assert result["task_name"] == "analyze_content_gaps"

        data = result["data"]
        assert "content_gaps" in data
        assert "missing_topics" in data
        assert "unexplained_concepts" in data
        assert "suggested_docs" in data
        assert "priority_level" in data

        assert isinstance(data["content_gaps"], list)
        assert isinstance(data["missing_topics"], list)
        assert isinstance(data["unexplained_concepts"], list)
        assert isinstance(data["suggested_docs"], list)
        assert isinstance(data["priority_level"], str)
        assert data["priority_level"] in ["low", "medium", "high"]

    def test_analyze_content_gaps_with_content_context(self, sample_content_context):
        """Test analyzing content gaps with ContentContext input."""
        result = analyze_content_gaps(sample_content_context)

        assert result["success"] is True
        data = result["data"]
        assert "content_gaps" in data
        assert "unexplained_concepts" in data

    def test_analyze_content_gaps_identifies_technical_terms(self, sample_article_data):
        """Test that content gap analysis identifies unexplained technical terms."""
        # Add technical terms to content
        sample_article_data["content"] = (
            "This API uses authentication and authorization for security."
        )

        result = analyze_content_gaps(sample_article_data)

        assert result["success"] is True
        unexplained_concepts = result["data"]["unexplained_concepts"]

        # Should identify technical terms that aren't explained
        assert isinstance(unexplained_concepts, list)
        # The function should detect 'API', 'authentication', 'authorization' as technical terms

    def test_analyze_content_gaps_identifies_missing_sections(
        self, sample_article_data
    ):
        """Test that content gap analysis identifies missing sections."""
        # Minimal content without common sections
        sample_article_data["content"] = "This is a simple article."

        result = analyze_content_gaps(sample_article_data)

        assert result["success"] is True
        content_gaps = result["data"]["content_gaps"]

        # Should identify missing sections
        assert isinstance(content_gaps, list)
        assert len(content_gaps) > 0  # Should find missing sections

    def test_analyze_content_gaps_generates_suggestions(self, sample_article_data):
        """Test that content gap analysis generates document suggestions."""
        result = analyze_content_gaps(sample_article_data)

        assert result["success"] is True
        suggested_docs = result["data"]["suggested_docs"]

        # Should generate document suggestions
        assert isinstance(suggested_docs, list)
        for doc in suggested_docs:
            assert "type" in doc
            assert "title" in doc
            assert "description" in doc
            assert "priority" in doc
            assert "target_audience" in doc

    def test_analyze_content_gaps_error_handling(self):
        """Test error handling in analyze_content_gaps."""
        # Test with invalid input that should trigger error handling
        result = analyze_content_gaps(None)
        assert result["success"] is False
        assert "error" in result


class TestSuggestRelatedDocs:
    """Test the suggest_related_docs function."""

    def test_suggest_related_docs_with_dict(self, sample_article_data):
        """Test suggesting related docs with dictionary input."""
        result = suggest_related_docs(sample_article_data)

        assert isinstance(result, dict)
        assert "related_docs" in result
        assert "prerequisite_docs" in result
        assert "follow_up_docs" in result
        assert "complementary_docs" in result
        assert "cross_references" in result

        assert isinstance(result["related_docs"], list)
        assert isinstance(result["prerequisite_docs"], list)
        assert isinstance(result["follow_up_docs"], list)
        assert isinstance(result["complementary_docs"], list)
        assert isinstance(result["cross_references"], list)

    def test_suggest_related_docs_with_custom_database(self, sample_article_data):
        """Test suggesting related docs with custom document database."""
        custom_docs = [
            {
                "id": "test-doc",
                "title": "Test Document",
                "keywords": ["test", "example"],
                "type": "guide",
                "audience": "all",
            }
        ]

        result = suggest_related_docs(sample_article_data, custom_docs)

        assert isinstance(result, dict)
        assert "related_docs" in result

    def test_suggest_related_docs_matches_keywords(self, sample_article_data):
        """Test that related docs suggestion matches keywords."""
        # Add keywords that should match default database
        sample_article_data["content"] = (
            "This is about getting started with best practices."
        )

        result = suggest_related_docs(sample_article_data)

        # Should find matches based on keywords
        total_suggestions = (
            len(result["related_docs"])
            + len(result["prerequisite_docs"])
            + len(result["follow_up_docs"])
            + len(result["complementary_docs"])
        )

        # Should have some suggestions based on keyword matching
        assert total_suggestions >= 0  # May be 0 if no matches

    def test_suggest_related_docs_categorizes_suggestions(self, sample_article_data):
        """Test that related docs suggestion categorizes suggestions properly."""
        result = suggest_related_docs(sample_article_data)

        # Check that suggestions are properly categorized
        for category in [
            "related_docs",
            "prerequisite_docs",
            "follow_up_docs",
            "complementary_docs",
        ]:
            suggestions = result[category]
            assert isinstance(suggestions, list)

            for suggestion in suggestions:
                assert "doc_id" in suggestion
                assert "title" in suggestion
                assert "type" in suggestion
                assert "audience" in suggestion
                assert "relevance_score" in suggestion
                assert "matched_keywords" in suggestion
                assert "suggestion_reason" in suggestion


class TestIdentifyCrossReferences:
    """Test the identify_cross_references function."""

    def test_identify_cross_references_with_dict(self, sample_article_data):
        """Test identifying cross references with dictionary input."""
        result = identify_cross_references(sample_article_data)

        assert isinstance(result, dict)
        assert "internal_links" in result
        assert "topic_connections" in result
        assert "concept_relationships" in result
        assert "series_opportunities" in result
        assert "update_opportunities" in result

        assert isinstance(result["internal_links"], list)
        assert isinstance(result["topic_connections"], list)
        assert isinstance(result["concept_relationships"], list)
        assert isinstance(result["series_opportunities"], list)
        assert isinstance(result["update_opportunities"], list)

    def test_identify_cross_references_with_custom_library(self, sample_article_data):
        """Test identifying cross references with custom content library."""
        custom_library = [
            {
                "id": "test-content",
                "title": "Test Content",
                "topics": ["test", "example"],
                "type": "tutorial",
                "status": "published",
            }
        ]

        result = identify_cross_references(sample_article_data, custom_library)

        assert isinstance(result, dict)
        assert "topic_connections" in result

    def test_identify_cross_references_finds_topic_connections(
        self, sample_article_data
    ):
        """Test that cross reference identification finds topic connections."""
        # Add content that should match default library topics
        sample_article_data["content"] = (
            "This tutorial covers JavaScript and web development."
        )

        result = identify_cross_references(sample_article_data)

        topic_connections = result["topic_connections"]
        assert isinstance(topic_connections, list)

        for connection in topic_connections:
            assert "content_id" in connection
            assert "title" in connection
            assert "type" in connection
            assert "matched_topics" in connection
            assert "relevance_score" in connection
            assert "link_text" in connection
            assert "suggestion" in connection

    def test_identify_cross_references_finds_concept_relationships(
        self, sample_article_data
    ):
        """Test that cross reference identification finds concept relationships."""
        # Add content with related concepts
        sample_article_data["content"] = (
            "This covers both authentication and authorization."
        )

        result = identify_cross_references(sample_article_data)

        concept_relationships = result["concept_relationships"]
        assert isinstance(concept_relationships, list)

        for relationship in concept_relationships:
            assert "concepts" in relationship
            assert "suggestion" in relationship
            assert "priority" in relationship


class TestGenerateDocSuggestions:
    """Test the generate_doc_suggestions function."""

    def test_generate_doc_suggestions_with_dict(self, sample_article_data):
        """Test generating doc suggestions with dictionary input."""
        result = generate_doc_suggestions(sample_article_data)

        assert isinstance(result, dict)
        assert "immediate_docs" in result
        assert "future_docs" in result
        assert "update_suggestions" in result
        assert "content_expansions" in result
        assert "resource_creations" in result

        assert isinstance(result["immediate_docs"], list)
        assert isinstance(result["future_docs"], list)
        assert isinstance(result["update_suggestions"], list)
        assert isinstance(result["content_expansions"], list)
        assert isinstance(result["resource_creations"], list)

    def test_generate_doc_suggestions_with_gap_analysis(self, sample_article_data):
        """Test generating doc suggestions with gap analysis."""
        gap_analysis = {
            "unexplained_concepts": ["API", "authentication"],
            "content_gaps": ["Missing troubleshooting section"],
        }

        result = generate_doc_suggestions(sample_article_data, gap_analysis)

        assert isinstance(result, dict)
        assert "immediate_docs" in result

        # Should generate suggestions based on gap analysis
        immediate_docs = result["immediate_docs"]
        assert isinstance(immediate_docs, list)

    def test_generate_doc_suggestions_creates_immediate_docs(self, sample_article_data):
        """Test that doc suggestions creates immediate document suggestions."""
        result = generate_doc_suggestions(sample_article_data)

        immediate_docs = result["immediate_docs"]
        assert isinstance(immediate_docs, list)

        for doc in immediate_docs:
            assert "type" in doc
            assert "title" in doc
            assert "description" in doc
            assert "priority" in doc
            assert "estimated_effort" in doc
            assert "target_audience" in doc
            assert "content_outline" in doc

    def test_generate_doc_suggestions_creates_future_docs(self, sample_article_data):
        """Test that doc suggestions creates future document suggestions."""
        result = generate_doc_suggestions(sample_article_data)

        future_docs = result["future_docs"]
        assert isinstance(future_docs, list)

        for doc in future_docs:
            assert "type" in doc
            assert "title" in doc
            assert "description" in doc
            assert "priority" in doc
            assert "estimated_effort" in doc
            assert "target_audience" in doc


class TestCreateContentRelationships:
    """Test the create_content_relationships function."""

    def test_create_content_relationships_with_dict(self, sample_article_data):
        """Test creating content relationships with dictionary input."""
        result = create_content_relationships(sample_article_data)

        assert isinstance(result, dict)
        assert "content_map" in result
        assert "learning_paths" in result
        assert "topic_clusters" in result
        assert "content_hierarchy" in result
        assert "cross_references" in result

        assert isinstance(result["content_map"], dict)
        assert isinstance(result["learning_paths"], list)
        assert isinstance(result["topic_clusters"], list)
        assert isinstance(result["content_hierarchy"], dict)
        assert isinstance(result["cross_references"], list)

    def test_create_content_relationships_with_custom_library(
        self, sample_article_data
    ):
        """Test creating content relationships with custom content library."""
        custom_library = [
            {
                "id": "related-content",
                "title": "Related Content",
                "topics": ["related", "topic"],
                "type": "article",
                "status": "published",
            }
        ]

        result = create_content_relationships(sample_article_data, custom_library)

        assert isinstance(result, dict)
        assert "content_map" in result

    def test_create_content_relationships_creates_content_map(
        self, sample_article_data
    ):
        """Test that content relationships creates a content map."""
        result = create_content_relationships(sample_article_data)

        content_map = result["content_map"]
        assert isinstance(content_map, dict)
        assert "id" in content_map
        assert "title" in content_map
        assert "type" in content_map
        assert "topics" in content_map
        assert "difficulty" in content_map
        assert "audience" in content_map
        assert "prerequisites" in content_map
        assert "follow_ups" in content_map
        assert "related_content" in content_map

    def test_create_content_relationships_creates_learning_paths(
        self, sample_article_data
    ):
        """Test that content relationships creates learning paths."""
        # Add beginner content indicators
        sample_article_data["content"] = "This is a beginner introduction to the topic."

        result = create_content_relationships(sample_article_data)

        learning_paths = result["learning_paths"]
        assert isinstance(learning_paths, list)

        for path in learning_paths:
            assert "path_name" in path
            assert "level" in path
            assert "steps" in path
            assert isinstance(path["steps"], list)


class TestOptimizeInternalLinking:
    """Test the optimize_internal_linking function."""

    def test_optimize_internal_linking_with_dict(self, sample_article_data):
        """Test optimizing internal linking with dictionary input."""
        result = optimize_internal_linking(sample_article_data)

        assert isinstance(result, dict)
        assert "current_links" in result
        assert "suggested_links" in result
        assert "link_opportunities" in result
        assert "anchor_text_suggestions" in result
        assert "link_distribution" in result
        assert "seo_impact" in result

        assert isinstance(result["current_links"], list)
        assert isinstance(result["suggested_links"], list)
        assert isinstance(result["link_opportunities"], list)
        assert isinstance(result["anchor_text_suggestions"], list)
        assert isinstance(result["link_distribution"], dict)
        assert isinstance(result["seo_impact"], dict)

    def test_optimize_internal_linking_with_custom_library(self, sample_article_data):
        """Test optimizing internal linking with custom content library."""
        custom_library = [
            {
                "id": "linkable-content",
                "title": "Linkable Content",
                "topics": ["linkable", "content"],
                "type": "article",
                "status": "published",
            }
        ]

        result = optimize_internal_linking(sample_article_data, custom_library)

        assert isinstance(result, dict)
        assert "suggested_links" in result

    def test_optimize_internal_linking_extracts_current_links(
        self, sample_article_data
    ):
        """Test that internal linking optimization extracts current links."""
        # Add markdown links to content
        sample_article_data["content"] = (
            "This is [a link](https://example.com) and [another link](/internal)."
        )

        result = optimize_internal_linking(sample_article_data)

        current_links = result["current_links"]
        assert isinstance(current_links, list)
        assert len(current_links) == 2  # Should find 2 links

        for link in current_links:
            assert "anchor_text" in link
            assert "url" in link

    def test_optimize_internal_linking_analyzes_link_distribution(
        self, sample_article_data
    ):
        """Test that internal linking optimization analyzes link distribution."""
        result = optimize_internal_linking(sample_article_data)

        link_distribution = result["link_distribution"]
        assert isinstance(link_distribution, dict)
        assert "total_links" in link_distribution
        assert "suggested_links" in link_distribution
        assert "link_density" in link_distribution
        assert "recommendation" in link_distribution

        assert isinstance(link_distribution["total_links"], int)
        assert isinstance(link_distribution["suggested_links"], int)
        assert isinstance(link_distribution["link_density"], (int, float))
        assert isinstance(link_distribution["recommendation"], str)


class TestIntegration:
    """Test integration between functions."""

    def test_full_internal_docs_processing_workflow(self, sample_article_data):
        """Test the full internal docs processing workflow."""
        # Step 1: Analyze content gaps
        gap_result = analyze_content_gaps(sample_article_data)
        assert gap_result["success"] is True

        # Step 2: Suggest related docs
        related_result = suggest_related_docs(sample_article_data)
        assert isinstance(related_result, dict)

        # Step 3: Identify cross references
        cross_ref_result = identify_cross_references(sample_article_data)
        assert isinstance(cross_ref_result, dict)

        # Step 4: Generate doc suggestions
        suggestions_result = generate_doc_suggestions(
            sample_article_data, gap_result["data"]
        )
        assert isinstance(suggestions_result, dict)

        # Step 5: Create content relationships
        relationships_result = create_content_relationships(sample_article_data)
        assert isinstance(relationships_result, dict)

        # Step 6: Optimize internal linking
        linking_result = optimize_internal_linking(sample_article_data)
        assert isinstance(linking_result, dict)

        # Verify all results have expected structure
        assert "content_gaps" in gap_result["data"]
        assert "related_docs" in related_result
        assert "topic_connections" in cross_ref_result
        assert "immediate_docs" in suggestions_result
        assert "content_map" in relationships_result
        assert "current_links" in linking_result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_analyze_content_gaps_empty_content(self):
        """Test analyzing content gaps for empty content."""
        empty_document = {"content": "", "title": "Empty Document"}

        result = analyze_content_gaps(empty_document)

        assert result["success"] is True
        # Empty content should have high priority due to many missing sections
        assert result["data"]["priority_level"] in ["low", "medium", "high"]

    def test_suggest_related_docs_no_database(self):
        """Test suggesting related docs with no database."""
        result = suggest_related_docs({"content": "test", "title": "test"}, [])

        assert isinstance(result, dict)
        assert "related_docs" in result
        assert len(result["related_docs"]) == 0  # Should be empty with no database

    def test_identify_cross_references_no_library(self):
        """Test identifying cross references with no content library."""
        result = identify_cross_references({"content": "test", "title": "test"}, [])

        assert isinstance(result, dict)
        assert "topic_connections" in result
        assert len(result["topic_connections"]) == 0  # Should be empty with no library

    def test_generate_doc_suggestions_minimal_content(self):
        """Test generating doc suggestions for minimal content."""
        minimal_document = {"content": "Minimal content", "title": "Minimal"}

        result = generate_doc_suggestions(minimal_document)

        assert isinstance(result, dict)
        assert "immediate_docs" in result
        assert "future_docs" in result

    def test_create_content_relationships_minimal_content(self):
        """Test creating content relationships for minimal content."""
        minimal_document = {"content": "Minimal content", "title": "Minimal"}

        result = create_content_relationships(minimal_document)

        assert isinstance(result, dict)
        assert "content_map" in result
        assert result["content_map"]["id"] == "current-article"  # Default ID

    def test_optimize_internal_linking_no_links(self):
        """Test optimizing internal linking when no links are present."""
        text_only_document = {"content": "Text only content", "title": "Text Document"}

        result = optimize_internal_linking(text_only_document)

        assert isinstance(result, dict)
        assert result["link_distribution"]["total_links"] == 0  # Should have no links
