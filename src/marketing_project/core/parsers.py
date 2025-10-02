"""
Content parsing utilities for Marketing Project.

This module provides parsing functions for different content types including
transcripts, blog posts, and release notes. It handles text extraction,
cleaning, and formatting for content processing.

Functions:
    parse_datetime: Parse datetime strings from various formats
    parse_transcript: Parse and clean transcript content
    parse_blog_post: Parse and clean blog post content
    parse_release_notes: Parse and clean release notes content
    clean_text: General text cleaning and normalization
"""

import re
import unicodedata
from bs4 import BeautifulSoup
from dateparser import parse
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("marketing_project.core.parsers")

def parse_datetime(text: str) -> Optional[datetime]:
    """
    Parse datetime strings from various formats.
    
    Args:
        text: String containing date/time information
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        return parse(text)
    except Exception as e:
        logger.warning(f"Failed to parse datetime '{text}': {e}")
        return None

def clean_text(raw_text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        raw_text: Raw text content
        
    Returns:
        Cleaned and normalized text
    """
    if not raw_text:
        return ""
    
    # Use BeautifulSoup to convert HTML to plain text if needed
    soup = BeautifulSoup(raw_text, 'html.parser')
    text = soup.get_text(separator=' ')

    # Normalize unicode (NFKC = Compatibility Decomposition, then Composition)
    text = unicodedata.normalize('NFKC', text)

    # Remove control/non-printable characters (except basic whitespace)
    text = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]+', '', text)

    # Replace specific unicode whitespace
    text = text.replace('\u00A0', ' ')  # Non-breaking space -> regular space

    # Collapse extra whitespace
    text = ' '.join(text.split())
    return text

def parse_transcript(raw_content: str, content_type: str = "podcast") -> Dict[str, Any]:
    """
    Parse transcript content and extract structured information.
    
    Args:
        raw_content: Raw transcript text
        content_type: Type of transcript (podcast, video, meeting, etc.)
        
    Returns:
        Dictionary with parsed transcript data
    """
    cleaned_content = clean_text(raw_content)
    
    # Extract speakers (look for patterns like "Speaker 1:", "John:", etc.)
    speaker_pattern = r'^([A-Za-z\s]+):\s*(.*)$'
    speakers = set()
    lines = cleaned_content.split('\n')
    
    for line in lines:
        match = re.match(speaker_pattern, line.strip())
        if match:
            speaker = match.group(1).strip()
            if len(speaker) < 50:  # Reasonable speaker name length
                speakers.add(speaker)
    
    # Extract timestamps (look for patterns like [00:30], (1:23), etc.)
    timestamp_pattern = r'[\[\(](\d{1,2}:\d{2}(?::\d{2})?)[\]\)]'
    timestamps = {}
    
    for line in lines:
        matches = re.findall(timestamp_pattern, line)
        for timestamp in matches:
            timestamps[timestamp] = line.strip()
    
    # Estimate duration based on content length (rough estimate)
    word_count = len(cleaned_content.split())
    estimated_duration = f"{word_count // 150}:00"  # ~150 words per minute
    
    return {
        "cleaned_content": cleaned_content,
        "speakers": list(speakers),
        "timestamps": timestamps,
        "word_count": word_count,
        "estimated_duration": estimated_duration,
        "content_type": content_type
    }

def parse_blog_post(raw_content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Parse blog post content and extract structured information.
    
    Args:
        raw_content: Raw blog post HTML/text
        metadata: Optional metadata dictionary
        
    Returns:
        Dictionary with parsed blog post data
    """
    cleaned_content = clean_text(raw_content)
    
    # Extract title if not provided in metadata
    title = ""
    if metadata and "title" in metadata:
        title = metadata["title"]
    else:
        # Try to extract title from content (first heading or first line)
        lines = cleaned_content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line.strip()) > 10 and len(line.strip()) < 200:
                title = line.strip()
                break
    
    # Extract headings (look for patterns like # Heading, ## Heading, etc.)
    heading_pattern = r'^#{1,6}\s+(.+)$'
    headings = []
    for line in cleaned_content.split('\n'):
        match = re.match(heading_pattern, line.strip())
        if match:
            headings.append(match.group(1).strip())
    
    # Extract links
    link_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    links = re.findall(link_pattern, cleaned_content)
    
    # Extract tags (look for #hashtag patterns)
    tag_pattern = r'#([a-zA-Z0-9_]+)'
    tags = re.findall(tag_pattern, cleaned_content)
    
    # Calculate reading time (average 200 words per minute)
    word_count = len(cleaned_content.split())
    reading_time = f"{max(1, word_count // 200)} min"
    
    return {
        "cleaned_content": cleaned_content,
        "title": title,
        "headings": headings,
        "links": links,
        "tags": tags,
        "word_count": word_count,
        "reading_time": reading_time,
        "metadata": metadata or {}
    }

def parse_release_notes(raw_content: str, version: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse release notes content and extract structured information.
    
    Args:
        raw_content: Raw release notes text
        version: Optional version string
        
    Returns:
        Dictionary with parsed release notes data
    """
    cleaned_content = clean_text(raw_content)
    
    # Extract version if not provided
    if not version:
        version_pattern = r'v?(\d+\.\d+\.\d+)'
        version_match = re.search(version_pattern, cleaned_content)
        if version_match:
            version = version_match.group(1)
    
    # Extract different types of changes
    changes = []
    features = []
    bug_fixes = []
    breaking_changes = []
    
    lines = cleaned_content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        if re.match(r'^(features?|new|added)', line, re.IGNORECASE):
            current_section = 'features'
        elif re.match(r'^(fixes?|bugs?|issues?)', line, re.IGNORECASE):
            current_section = 'bug_fixes'
        elif re.match(r'^(breaking|breaking changes?)', line, re.IGNORECASE):
            current_section = 'breaking'
        elif re.match(r'^(changes?|updates?)', line, re.IGNORECASE):
            current_section = 'changes'
        elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
            # Extract bullet point
            item = re.sub(r'^[-*•]\s*', '', line).strip()
            if item:
                if current_section == 'features':
                    features.append(item)
                elif current_section == 'bug_fixes':
                    bug_fixes.append(item)
                elif current_section == 'breaking':
                    breaking_changes.append(item)
                else:
                    changes.append(item)
    
    # Extract release date if present
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})'
    date_match = re.search(date_pattern, cleaned_content)
    release_date = date_match.group(1) if date_match else None
    
    return {
        "cleaned_content": cleaned_content,
        "version": version,
        "release_date": release_date,
        "changes": changes,
        "features": features,
        "bug_fixes": bug_fixes,
        "breaking_changes": breaking_changes,
        "word_count": len(cleaned_content.split())
    }

def extract_metadata_from_content(content: str, content_type: str) -> Dict[str, Any]:
    """
    Extract metadata from content based on its type.
    
    Args:
        content: Content text
        content_type: Type of content (transcript, blog_post, release_notes)
        
    Returns:
        Dictionary with extracted metadata
    """
    if content_type == "transcript":
        return parse_transcript(content)
    elif content_type == "blog_post":
        return parse_blog_post(content)
    elif content_type == "release_notes":
        return parse_release_notes(content)
    else:
        return {"cleaned_content": clean_text(content)}
