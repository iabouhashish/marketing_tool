"""
SEO Keywords plugin for Marketing Project.

This plugin provides functionality to extract, analyze, and optimize SEO keywords
from content for better search engine visibility and content strategy.
"""

from .tasks import (
    extract_primary_keywords,
    extract_secondary_keywords,
    analyze_keyword_density,
    generate_keyword_suggestions,
    optimize_keyword_placement,
    calculate_keyword_scores
)

__all__ = [
    "extract_primary_keywords",
    "extract_secondary_keywords", 
    "analyze_keyword_density",
    "generate_keyword_suggestions",
    "optimize_keyword_placement",
    "calculate_keyword_scores"
]
