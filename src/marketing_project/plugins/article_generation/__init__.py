"""
Article Generation plugin for Marketing Project.

This plugin provides functionality to generate high-quality articles
based on marketing briefs, SEO keywords, and content strategy.
"""

from .tasks import (
    generate_article_structure,
    write_article_content,
    add_supporting_elements,
    review_article_quality,
    optimize_article_flow,
    add_call_to_actions
)

__all__ = [
    "generate_article_structure",
    "write_article_content",
    "add_supporting_elements",
    "review_article_quality",
    "optimize_article_flow",
    "add_call_to_actions"
]
