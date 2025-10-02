"""
Marketing Brief plugin for Marketing Project.

This plugin provides functionality to generate comprehensive marketing briefs
based on content analysis and SEO keywords for content strategy planning.
"""

from .tasks import (
    generate_brief_outline,
    define_target_audience,
    set_content_objectives,
    create_content_strategy,
    analyze_competitor_content,
    generate_content_calendar_suggestions
)

__all__ = [
    "generate_brief_outline",
    "define_target_audience",
    "set_content_objectives", 
    "create_content_strategy",
    "analyze_competitor_content",
    "generate_content_calendar_suggestions"
]
