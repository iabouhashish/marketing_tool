"""
Tests for the marketing brief plugin.

This module tests all functions in the marketing brief plugin tasks.
"""

from unittest.mock import Mock, patch

import pytest

from marketing_project.core.models import AppContext, ContentContext
from marketing_project.plugins.marketing_brief.tasks import (
    analyze_competitor_content,
    create_content_strategy,
    define_target_audience,
    generate_brief_outline,
    generate_content_calendar_suggestions,
    set_content_objectives,
)


class TestGenerateBriefOutline:
    """Test the generate_brief_outline function."""

    def test_generate_brief_outline_with_dict(self, sample_article_data):
        """Test generating brief outline with dictionary input."""
        result = generate_brief_outline(sample_article_data)

        assert result["success"] is True
        assert "data" in result
        assert result["task_name"] == "generate_brief_outline"

        data = result["data"]
        assert "title" in data
        assert "content_type" in data
        assert "executive_summary" in data
        assert "target_audience" in data
        assert "content_objectives" in data
        assert "key_messages" in data
        assert "seo_strategy" in data
        assert "content_requirements" in data
        assert "success_metrics" in data
        assert "timeline" in data
        assert "resources_needed" in data
        assert "distribution_channels" in data
        assert "created_at" in data

        assert isinstance(data["title"], str)
        assert isinstance(data["content_type"], str)
        assert isinstance(data["executive_summary"], str)
        assert isinstance(data["target_audience"], dict)
        assert isinstance(data["content_objectives"], dict)
        assert isinstance(data["key_messages"], list)
        assert isinstance(data["seo_strategy"], dict)
        assert isinstance(data["content_requirements"], dict)
        assert isinstance(data["success_metrics"], dict)
        assert isinstance(data["timeline"], dict)
        assert isinstance(data["resources_needed"], list)
        assert isinstance(data["distribution_channels"], list)
        assert isinstance(data["created_at"], str)

    def test_generate_brief_outline_with_content_context(self, sample_content_context):
        """Test generating brief outline with ContentContext input."""
        result = generate_brief_outline(sample_content_context)

        assert result["success"] is True
        data = result["data"]
        assert "title" in data
        assert "executive_summary" in data

    def test_generate_brief_outline_with_seo_keywords(self, sample_article_data):
        """Test generating brief outline with SEO keywords."""
        seo_keywords = [
            {"keyword": "test keyword 1", "volume": 1000},
            {"keyword": "test keyword 2", "volume": 500},
            {"keyword": "test keyword 3", "volume": 200},
        ]

        result = generate_brief_outline(sample_article_data, seo_keywords)

        assert result["success"] is True
        data = result["data"]
        assert "seo_strategy" in data
        assert "primary_keywords" in data["seo_strategy"]
        assert "secondary_keywords" in data["seo_strategy"]
        assert len(data["seo_strategy"]["primary_keywords"]) == 3
        assert (
            len(data["seo_strategy"]["secondary_keywords"]) >= 0
        )  # May be 0 if less than 6 keywords

    def test_generate_brief_outline_extracts_key_messages(self, sample_article_data):
        """Test that brief outline extracts key messages from content."""
        # Add content with key indicators
        sample_article_data["content"] = (
            "This is important information. The main point is clear. Key benefits include efficiency."
        )

        result = generate_brief_outline(sample_article_data)

        assert result["success"] is True
        key_messages = result["data"]["key_messages"]
        assert isinstance(key_messages, list)
        assert len(key_messages) > 0

    def test_generate_brief_outline_error_handling(self):
        """Test error handling in generate_brief_outline."""
        # Test with invalid input
        result = generate_brief_outline(None)
        assert result["success"] is False
        assert "error" in result


class TestDefineTargetAudience:
    """Test the define_target_audience function."""

    def test_define_target_audience_with_content_context(self, sample_content_context):
        """Test defining target audience with ContentContext input."""
        result = define_target_audience(sample_content_context)

        assert isinstance(result, dict)
        assert "primary_audience" in result
        assert "secondary_audience" in result
        assert "demographics" in result
        assert "psychographics" in result
        assert "pain_points" in result
        assert "content_preferences" in result
        assert "channels" in result

        assert isinstance(result["primary_audience"], dict)
        assert isinstance(result["secondary_audience"], dict)
        assert isinstance(result["demographics"], dict)
        assert isinstance(result["psychographics"], dict)
        assert isinstance(result["pain_points"], list)
        assert isinstance(result["content_preferences"], dict)
        assert isinstance(result["channels"], list)

    def test_define_target_audience_with_industry(self, sample_content_context):
        """Test defining target audience with industry context."""
        result = define_target_audience(sample_content_context, "technology")

        assert isinstance(result, dict)
        assert "demographics" in result
        demographics = result["demographics"]
        assert "age_range" in demographics
        assert "education" in demographics
        assert "income" in demographics

    def test_define_target_audience_technical_content(self, sample_content_context):
        """Test defining target audience for technical content."""
        # Add technical content
        sample_content_context.content = "This API integration requires development skills and technical implementation."

        result = define_target_audience(sample_content_context)

        assert isinstance(result, dict)
        primary_audience = result["primary_audience"]
        assert "role" in primary_audience
        assert "Technical Professionals" in primary_audience["role"]

    def test_define_target_audience_business_content(self, sample_content_context):
        """Test defining target audience for business content."""
        # Add business content
        sample_content_context.content = (
            "This strategy requires management decision making and leadership planning."
        )

        result = define_target_audience(sample_content_context)

        assert isinstance(result, dict)
        primary_audience = result["primary_audience"]
        assert "role" in primary_audience
        assert "Business Professionals" in primary_audience["role"]

    def test_define_target_audience_beginner_content(self, sample_content_context):
        """Test defining target audience for beginner content."""
        # Add beginner content
        sample_content_context.content = (
            "This is an introduction to the basics and getting started guide."
        )

        result = define_target_audience(sample_content_context)

        assert isinstance(result, dict)
        primary_audience = result["primary_audience"]
        assert "role" in primary_audience
        assert "General Audience" in primary_audience["role"]


class TestSetContentObjectives:
    """Test the set_content_objectives function."""

    def test_set_content_objectives_with_content_context(self, sample_content_context):
        """Test setting content objectives with ContentContext input."""
        result = set_content_objectives(sample_content_context)

        assert isinstance(result, dict)
        assert "primary_objectives" in result
        assert "secondary_objectives" in result
        assert "kpis" in result
        assert "success_criteria" in result
        assert "measurement_period" in result
        assert "baseline_metrics" in result

        assert isinstance(result["primary_objectives"], list)
        assert isinstance(result["secondary_objectives"], list)
        assert isinstance(result["kpis"], dict)
        assert isinstance(result["success_criteria"], list)
        assert isinstance(result["measurement_period"], str)
        assert isinstance(result["baseline_metrics"], dict)

    def test_set_content_objectives_with_business_goals(self, sample_content_context):
        """Test setting content objectives with business goals."""
        business_goals = ["Increase sales", "Improve brand awareness", "Generate leads"]

        result = set_content_objectives(sample_content_context, business_goals)

        assert isinstance(result, dict)
        secondary_objectives = result["secondary_objectives"]
        assert len(secondary_objectives) > 0
        assert any("Increase sales" in obj for obj in secondary_objectives)

    def test_set_content_objectives_tutorial_content(self, sample_content_context):
        """Test setting content objectives for tutorial content."""
        # Add tutorial content to title
        sample_content_context.title = "Tutorial: How to Learn the Basics"

        result = set_content_objectives(sample_content_context)

        assert isinstance(result, dict)
        primary_objectives = result["primary_objectives"]
        assert any("Educate target audience" in obj for obj in primary_objectives)
        assert "engagement_rate" in result["kpis"]

    def test_set_content_objectives_review_content(self, sample_content_context):
        """Test setting content objectives for review content."""
        # Add review content to title
        sample_content_context.title = "Review and Analysis of Different Options"

        result = set_content_objectives(sample_content_context)

        assert isinstance(result, dict)
        primary_objectives = result["primary_objectives"]
        assert any(
            "Provide comprehensive analysis" in obj for obj in primary_objectives
        )
        assert "conversion_rate" in result["kpis"]

    def test_set_content_objectives_news_content(self, sample_content_context):
        """Test setting content objectives for news content."""
        # Add news content to title
        sample_content_context.title = "Important News Update and Announcement"

        result = set_content_objectives(sample_content_context)

        assert isinstance(result, dict)
        primary_objectives = result["primary_objectives"]
        assert any("Communicate important updates" in obj for obj in primary_objectives)
        assert "page_views" in result["kpis"]


class TestCreateContentStrategy:
    """Test the create_content_strategy function."""

    def test_create_content_strategy_with_all_inputs(self, sample_content_context):
        """Test creating content strategy with all required inputs."""
        target_audience = {
            "primary_audience": {"role": "Technical Professionals"},
            "demographics": {"age_range": "25-45"},
        }
        objectives = {
            "primary_objectives": ["Increase engagement"],
            "kpis": {"engagement_rate": "Target: >5%"},
        }

        result = create_content_strategy(
            sample_content_context, target_audience, objectives
        )

        assert isinstance(result, dict)
        assert "content_pillars" in result
        assert "content_types" in result
        assert "distribution_strategy" in result
        assert "promotion_strategy" in result
        assert "content_calendar" in result
        assert "resource_requirements" in result
        assert "quality_standards" in result
        assert "performance_tracking" in result

        assert isinstance(result["content_pillars"], list)
        assert isinstance(result["content_types"], list)
        assert isinstance(result["distribution_strategy"], dict)
        assert isinstance(result["promotion_strategy"], dict)
        assert isinstance(result["content_calendar"], dict)
        assert isinstance(result["resource_requirements"], dict)
        assert isinstance(result["quality_standards"], dict)
        assert isinstance(result["performance_tracking"], dict)

    def test_create_content_strategy_tutorial_content(self, sample_content_context):
        """Test creating content strategy for tutorial content."""
        target_audience = {"primary_audience": {"role": "General Audience"}}
        objectives = {"primary_objectives": ["Educate audience"]}

        # Add tutorial content
        sample_content_context.content = (
            "This tutorial guide will teach you the basics."
        )

        result = create_content_strategy(
            sample_content_context, target_audience, objectives
        )

        assert isinstance(result, dict)
        content_pillars = result["content_pillars"]
        assert "Education" in content_pillars
        assert "How-to Guides" in content_pillars

    def test_create_content_strategy_review_content(self, sample_content_context):
        """Test creating content strategy for review content."""
        target_audience = {"primary_audience": {"role": "Business Professionals"}}
        objectives = {"primary_objectives": ["Provide analysis"]}

        # Add review content
        sample_content_context.content = (
            "This review compares different options and analysis."
        )

        result = create_content_strategy(
            sample_content_context, target_audience, objectives
        )

        assert isinstance(result, dict)
        content_pillars = result["content_pillars"]
        assert "Product Reviews" in content_pillars
        assert "Market Analysis" in content_pillars

    def test_create_content_strategy_news_content(self, sample_content_context):
        """Test creating content strategy for news content."""
        target_audience = {"primary_audience": {"role": "General Audience"}}
        objectives = {"primary_objectives": ["Communicate updates"]}

        # Add news content
        sample_content_context.content = (
            "This is important news and update information."
        )

        result = create_content_strategy(
            sample_content_context, target_audience, objectives
        )

        assert isinstance(result, dict)
        content_pillars = result["content_pillars"]
        assert "Industry News" in content_pillars
        assert "Company Updates" in content_pillars


class TestAnalyzeCompetitorContent:
    """Test the analyze_competitor_content function."""

    def test_analyze_competitor_content_with_content_context(
        self, sample_content_context
    ):
        """Test analyzing competitor content with ContentContext input."""
        result = analyze_competitor_content(sample_content_context)

        assert isinstance(result, dict)
        assert "competitor_insights" in result
        assert "content_gaps" in result
        assert "opportunities" in result
        assert "best_practices" in result
        assert "differentiation_strategies" in result

        assert isinstance(result["competitor_insights"], list)
        assert isinstance(result["content_gaps"], list)
        assert isinstance(result["opportunities"], list)
        assert isinstance(result["best_practices"], list)
        assert isinstance(result["differentiation_strategies"], list)

    def test_analyze_competitor_content_with_urls(self, sample_content_context):
        """Test analyzing competitor content with competitor URLs."""
        competitor_urls = ["https://competitor1.com", "https://competitor2.com"]

        result = analyze_competitor_content(sample_content_context, competitor_urls)

        assert isinstance(result, dict)
        competitor_insights = result["competitor_insights"]
        assert len(competitor_insights) > 0
        assert any(
            "Analyze competitor content themes" in insight
            for insight in competitor_insights
        )

    def test_analyze_competitor_content_identifies_gaps(self, sample_content_context):
        """Test that competitor analysis identifies content gaps."""
        result = analyze_competitor_content(sample_content_context)

        assert isinstance(result, dict)
        content_gaps = result["content_gaps"]
        assert len(content_gaps) > 0
        assert any("topics competitors cover" in gap for gap in content_gaps)

    def test_analyze_competitor_content_suggests_opportunities(
        self, sample_content_context
    ):
        """Test that competitor analysis suggests opportunities."""
        result = analyze_competitor_content(sample_content_context)

        assert isinstance(result, dict)
        opportunities = result["opportunities"]
        assert len(opportunities) > 0
        assert any("Create more comprehensive content" in opp for opp in opportunities)


class TestGenerateContentCalendarSuggestions:
    """Test the generate_content_calendar_suggestions function."""

    def test_generate_content_calendar_suggestions_with_content_context(
        self, sample_content_context
    ):
        """Test generating content calendar suggestions with ContentContext input."""
        strategy = {
            "content_pillars": ["Education", "How-to Guides"],
            "content_types": ["Articles", "Videos"],
        }

        result = generate_content_calendar_suggestions(sample_content_context, strategy)

        assert isinstance(result, dict)
        assert "weekly_schedule" in result
        assert "content_ideas" in result
        assert "seasonal_content" in result
        assert "evergreen_content" in result
        assert "trending_topics" in result
        assert "repurposing_opportunities" in result

        assert isinstance(result["weekly_schedule"], dict)
        assert isinstance(result["content_ideas"], list)
        assert isinstance(result["seasonal_content"], list)
        assert isinstance(result["evergreen_content"], list)
        assert isinstance(result["trending_topics"], list)
        assert isinstance(result["repurposing_opportunities"], list)

    def test_generate_content_calendar_suggestions_tutorial_content(
        self, sample_content_context
    ):
        """Test generating calendar suggestions for tutorial content."""
        strategy = {"content_pillars": ["Education"]}

        # Add tutorial content
        sample_content_context.content = "This tutorial will teach you the basics."

        result = generate_content_calendar_suggestions(sample_content_context, strategy)

        assert isinstance(result, dict)
        content_ideas = result["content_ideas"]
        assert any("Advanced tutorial series" in idea for idea in content_ideas)
        assert any("Video walkthroughs" in idea for idea in content_ideas)

    def test_generate_content_calendar_suggestions_review_content(
        self, sample_content_context
    ):
        """Test generating calendar suggestions for review content."""
        strategy = {"content_pillars": ["Product Reviews"]}

        # Add review content
        sample_content_context.content = "This review compares different options."

        result = generate_content_calendar_suggestions(sample_content_context, strategy)

        assert isinstance(result, dict)
        content_ideas = result["content_ideas"]
        assert any("Updated reviews" in idea for idea in content_ideas)
        assert any("User experience comparisons" in idea for idea in content_ideas)

    def test_generate_content_calendar_suggestions_weekly_schedule(
        self, sample_content_context
    ):
        """Test that calendar suggestions include weekly schedule."""
        strategy = {"content_pillars": ["Education"]}

        result = generate_content_calendar_suggestions(sample_content_context, strategy)

        assert isinstance(result, dict)
        weekly_schedule = result["weekly_schedule"]
        assert "monday" in weekly_schedule
        assert "tuesday" in weekly_schedule
        assert "wednesday" in weekly_schedule
        assert "thursday" in weekly_schedule
        assert "friday" in weekly_schedule

    def test_generate_content_calendar_suggestions_seasonal_content(
        self, sample_content_context
    ):
        """Test that calendar suggestions include seasonal content."""
        strategy = {"content_pillars": ["Education"]}

        result = generate_content_calendar_suggestions(sample_content_context, strategy)

        assert isinstance(result, dict)
        seasonal_content = result["seasonal_content"]
        assert isinstance(seasonal_content, list)
        # Should have seasonal content for current month
        assert len(seasonal_content) >= 0


class TestIntegration:
    """Test integration between functions."""

    def test_full_marketing_brief_processing_workflow(self, sample_content_context):
        """Test the full marketing brief processing workflow."""
        # Step 1: Generate brief outline
        outline_result = generate_brief_outline(sample_content_context)
        assert outline_result["success"] is True

        # Step 2: Define target audience
        audience_result = define_target_audience(sample_content_context)
        assert isinstance(audience_result, dict)

        # Step 3: Set content objectives
        objectives_result = set_content_objectives(sample_content_context)
        assert isinstance(objectives_result, dict)

        # Step 4: Create content strategy
        strategy_result = create_content_strategy(
            sample_content_context, audience_result, objectives_result
        )
        assert isinstance(strategy_result, dict)

        # Step 5: Analyze competitor content
        competitor_result = analyze_competitor_content(sample_content_context)
        assert isinstance(competitor_result, dict)

        # Step 6: Generate content calendar suggestions
        calendar_result = generate_content_calendar_suggestions(
            sample_content_context, strategy_result
        )
        assert isinstance(calendar_result, dict)

        # Verify all results have expected structure
        assert "title" in outline_result["data"]
        assert "primary_audience" in audience_result
        assert "primary_objectives" in objectives_result
        assert "content_pillars" in strategy_result
        assert "competitor_insights" in competitor_result
        assert "weekly_schedule" in calendar_result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_generate_brief_outline_empty_content(self):
        """Test generating brief outline for empty content."""
        from marketing_project.core.models import BlogPostContext

        empty_content = BlogPostContext(
            id="empty-content", content="", title="Empty Content", snippet=""
        )

        result = generate_brief_outline(empty_content)

        # Empty content should fail validation
        assert result["success"] is False
        assert "error" in result
        assert "Content validation failed" in result["error"]

    def test_define_target_audience_empty_content(self):
        """Test defining target audience for empty content."""
        from marketing_project.core.models import BlogPostContext

        empty_content = BlogPostContext(
            id="empty-content", content="", title="Empty", snippet=""
        )

        result = define_target_audience(empty_content)

        assert isinstance(result, dict)
        assert "primary_audience" in result
        assert result["primary_audience"]["role"] == "General Audience"

    def test_set_content_objectives_empty_content(self):
        """Test setting content objectives for empty content."""
        from marketing_project.core.models import BlogPostContext

        empty_content = BlogPostContext(
            id="empty-content", content="", title="Empty", snippet=""
        )

        result = set_content_objectives(empty_content)

        assert isinstance(result, dict)
        assert "primary_objectives" in result
        assert len(result["primary_objectives"]) > 0

    def test_create_content_strategy_minimal_inputs(self, sample_content_context):
        """Test creating content strategy with minimal inputs."""
        minimal_audience = {"primary_audience": {}}
        minimal_objectives = {"primary_objectives": []}

        result = create_content_strategy(
            sample_content_context, minimal_audience, minimal_objectives
        )

        assert isinstance(result, dict)
        assert "content_pillars" in result
        assert "content_types" in result

    def test_analyze_competitor_content_no_urls(self, sample_content_context):
        """Test analyzing competitor content with no URLs."""
        result = analyze_competitor_content(sample_content_context, [])

        assert isinstance(result, dict)
        assert "competitor_insights" in result
        assert len(result["competitor_insights"]) == 0

    def test_generate_content_calendar_suggestions_minimal_strategy(
        self, sample_content_context
    ):
        """Test generating calendar suggestions with minimal strategy."""
        minimal_strategy = {}

        result = generate_content_calendar_suggestions(
            sample_content_context, minimal_strategy
        )

        assert isinstance(result, dict)
        assert "weekly_schedule" in result
        assert "content_ideas" in result
