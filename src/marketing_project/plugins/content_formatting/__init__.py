"""
Content Formatting plugin for Marketing Project.

This plugin provides functionality to format and finalize content
for publication with proper styling, structure, and visual elements.
"""

from .tasks import (
    add_visual_elements,
    apply_formatting_rules,
    finalize_content,
    generate_publication_ready_content,
    optimize_readability,
    validate_formatting,
)

__all__ = [
    "apply_formatting_rules",
    "optimize_readability",
    "add_visual_elements",
    "finalize_content",
    "validate_formatting",
    "generate_publication_ready_content",
]
