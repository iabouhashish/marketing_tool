"""
Internal Documents plugin for Marketing Project.

This plugin provides functionality to suggest internal documents
and cross-references to enhance content and improve internal linking.
"""

from .tasks import (
    analyze_content_gaps,
    create_content_relationships,
    generate_doc_suggestions,
    identify_cross_references,
    optimize_internal_linking,
    suggest_related_docs,
)

__all__ = [
    "analyze_content_gaps",
    "suggest_related_docs",
    "identify_cross_references",
    "generate_doc_suggestions",
    "create_content_relationships",
    "optimize_internal_linking",
]
