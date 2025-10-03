"""
Release notes processing plugin tasks for Marketing Project.

This module provides functions to analyze, process, and route release notes content
including software releases, product updates, and version announcements.

Functions:
    analyze_release_type: Analyzes the type of release notes content
    extract_release_metadata: Extracts metadata from release notes content
    validate_release_structure: Validates release notes have required fields
    route_release_processing: Routes release notes to appropriate processing agent
"""

import logging
from typing import Dict, Any, Optional, List
from marketing_project.core.models import ReleaseNotesContext, AppContext
from marketing_project.core.parsers import parse_release_notes, clean_text
from marketing_project.services.ocr import enhance_content_with_ocr, extract_images_from_content

logger = logging.getLogger("marketing_project.plugins.release_notes")

def analyze_release_type(release_notes: ReleaseNotesContext) -> str:
    """
    Analyzes the release type and returns processing category.
    
    Args:
        release_notes: Release notes context object
        
    Returns:
        str: Processing category (major, minor, patch, hotfix, etc.)
    """
    version = release_notes.version
    changes_count = len(release_notes.changes)
    breaking_count = len(release_notes.breaking_changes)
    features_count = len(release_notes.features)
    
    # Handle empty or None version
    if not version or version.strip() == "":
        # Fallback analysis based on content
        if breaking_count > 0:
            return "major"
        elif features_count > 0:
            return "minor"
        elif changes_count > 0:
            return "patch"
        else:
            return "patch"  # Default to patch for empty versions
    
    # Analyze version number (semantic versioning)
    try:
        # Handle complex version formats (e.g., "1.2.3-beta.1" -> "1.2.3")
        version_clean = version.split('-')[0].split('+')[0]
        version_parts = version_clean.split('.')
        
        # Handle incomplete versions (e.g., "1.0" -> [1, 0, 0])
        while len(version_parts) < 3:
            version_parts.append('0')
        
        major, minor, patch = map(int, version_parts[:3])
        
        # First check for breaking changes (always major)
        if breaking_count > 0:
            return "major"
        # Then check for features (minor if minor version > 0, otherwise minor for incomplete versions)
        elif features_count > 0:
            if minor > 0:
                return "minor"
            elif major > 0 and minor == 0 and patch == 0:
                # Incomplete version like "1.0" with features should be minor
                return "minor"
            else:
                return "major"
        # Then check for changes (patch if patch version > 0, otherwise minor)
        elif changes_count > 0:
            if patch > 0:
                return "patch"
            else:
                return "minor"
        # Check for hotfix (patch version > 0 with no changes, features, or breaking changes)
        elif patch > 0 and changes_count == 0 and features_count == 0 and breaking_count == 0:
            return "hotfix"
        # Check for general release (major.minor.0 with no changes, features, or breaking changes)
        elif major > 0 and minor >= 0 and patch == 0 and changes_count == 0 and features_count == 0 and breaking_count == 0:
            return "general"
        # Default cases
        elif major == 0 and minor == 0 and patch == 0:
            return "patch"  # Default to patch for 0.0.0
        elif changes_count == 0 and features_count == 0 and breaking_count == 0:
            return "patch"  # Default to patch for no changes
        else:
            return "hotfix"
    except (ValueError, IndexError):
        # Fallback analysis based on content
        if breaking_count > 0:
            return "major"
        elif features_count > 0:
            return "minor"
        elif changes_count > 0:
            return "patch"
        else:
            return "patch"  # Default to patch

def extract_release_metadata(release_notes: ReleaseNotesContext) -> Dict[str, Any]:
    """
    Extracts metadata from release notes for processing decisions.
    
    Args:
        release_notes: Release notes context object
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    # Parse the release notes content to extract additional metadata
    parsed_data = parse_release_notes(release_notes.content, release_notes.version)
    
    metadata = {
        "content_type": "release_notes",
        "id": release_notes.id,
        "title": release_notes.title,
        "version": release_notes.version or parsed_data.get("version", ""),
        "release_date": release_notes.release_date,
        "changes_count": len(release_notes.changes or parsed_data.get("changes", [])),
        "breaking_changes_count": len(release_notes.breaking_changes or parsed_data.get("breaking_changes", [])),
        "features_count": len(release_notes.features or parsed_data.get("features", [])),
        "bug_fixes_count": len(release_notes.bug_fixes or parsed_data.get("bug_fixes", [])),
        "total_changes": len(release_notes.changes or parsed_data.get("changes", [])) + 
                        len(release_notes.breaking_changes or parsed_data.get("breaking_changes", [])) + 
                        len(release_notes.features or parsed_data.get("features", [])) + 
                        len(release_notes.bug_fixes or parsed_data.get("bug_fixes", [])),
        "has_breaking_changes": len(release_notes.breaking_changes or parsed_data.get("breaking_changes", [])) > 0,
        "has_new_features": len(release_notes.features or parsed_data.get("features", [])) > 0,
        "parsed_changes": parsed_data.get("changes", []),
        "parsed_features": parsed_data.get("features", []),
        "parsed_bug_fixes": parsed_data.get("bug_fixes", []),
        "parsed_breaking_changes": parsed_data.get("breaking_changes", []),
        "cleaned_content": parsed_data.get("cleaned_content", release_notes.content)
    }
    
    return metadata

def validate_release_structure(release_notes: ReleaseNotesContext) -> bool:
    """
    Validates that the release notes have the required structure for processing.
    
    Args:
        release_notes: Release notes context object
        
    Returns:
        bool: True if release notes are valid, False otherwise
    """
    required_fields = ["id", "title", "content", "snippet", "version"]
    
    for field in required_fields:
        if not hasattr(release_notes, field) or not getattr(release_notes, field):
            logger.error(f"Release notes missing required field: {field}")
            return False
    
    # Validate version format
    if not release_notes.version or not isinstance(release_notes.version, str):
        logger.error("Release notes missing valid version")
        return False
    
    return True

def enhance_release_notes_with_ocr(release_notes: ReleaseNotesContext, image_urls: List[str] = None) -> Dict[str, Any]:
    """
    Enhance release notes content with OCR text from images.
    
    Args:
        release_notes: Release notes context object
        image_urls: List of image URLs to process with OCR
        
    Returns:
        Dict[str, Any]: Enhanced release notes data with OCR text
    """
    # Extract images from content if not provided
    if not image_urls:
        image_urls = extract_images_from_content(release_notes.content)
    
    # Enhance content with OCR
    enhanced_data = enhance_content_with_ocr(
        release_notes.content, 
        "release_notes", 
        image_urls=image_urls
    )
    
    return {
        "original_release_notes": release_notes,
        "enhanced_content": enhanced_data["enhanced_content"],
        "ocr_text": enhanced_data["ocr_text"],
        "has_screenshots": enhanced_data["has_screenshots"],
        "image_count": enhanced_data["image_count"],
        "screenshot_text": enhanced_data["screenshot_text"]
    }

def route_release_processing(app_context: AppContext, available_agents: Dict[str, Any]) -> str:
    """
    Routes release notes content to the appropriate processing agent.
    
    Args:
        app_context: Application context with release notes content
        available_agents: Dictionary of available agents
        
    Returns:
        str: Result of the routing operation
    """
    if not isinstance(app_context.content, ReleaseNotesContext):
        return "Error: Content is not release notes"
    
    release_notes = app_context.content
    processing_type = analyze_release_type(release_notes)
    
    # Map processing types to agent names - use the actual releasenotes_agent for all types
    agent_mapping = {
        "major": "releasenotes_agent",
        "minor": "releasenotes_agent",
        "patch": "releasenotes_agent",
        "hotfix": "releasenotes_agent",
        "general": "releasenotes_agent"
    }
    
    agent_name = agent_mapping.get(processing_type, "releasenotes_agent")
    
    if agent_name in available_agents and available_agents[agent_name]:
        logger.info(f"Routing {processing_type} release to {agent_name}")
        return f"Successfully routed {processing_type} release to {agent_name}"
    else:
        logger.warning(f"No agent available for {processing_type} release, using general processing")
        return f"No specialized agent for {processing_type} release, using general processing"
