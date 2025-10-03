"""
SEO Optimization plugin for Marketing Project.

This plugin provides functionality to optimize content for search engines
including title tags, meta descriptions, headings, and content structure.
"""

from .tasks import (
    add_internal_links,
    analyze_seo_performance,
    optimize_content_structure,
    optimize_headings,
    optimize_meta_descriptions,
    optimize_title_tags,
)

__all__ = [
    "optimize_title_tags",
    "optimize_meta_descriptions",
    "optimize_headings",
    "optimize_content_structure",
    "add_internal_links",
    "analyze_seo_performance",
]
