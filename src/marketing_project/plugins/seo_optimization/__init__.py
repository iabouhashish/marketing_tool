"""
SEO Optimization plugin for Marketing Project.

This plugin provides functionality to optimize content for search engines
including title tags, meta descriptions, headings, and content structure.
"""

from .tasks import (
    optimize_title_tags,
    optimize_meta_descriptions,
    optimize_headings,
    optimize_content_structure,
    add_internal_links,
    analyze_seo_performance
)

__all__ = [
    "optimize_title_tags",
    "optimize_meta_descriptions",
    "optimize_headings",
    "optimize_content_structure",
    "add_internal_links",
    "analyze_seo_performance"
]
