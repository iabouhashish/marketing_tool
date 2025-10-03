"""
Transcript processing plugin tasks for Marketing Project.

This module provides functions to analyze, process, and route transcript content
including podcasts, videos, meetings, and interviews.

Functions:
    analyze_transcript_type: Analyzes the type of transcript content
    extract_transcript_metadata: Extracts metadata from transcript content
    validate_transcript_structure: Validates transcript has required fields
    route_transcript_processing: Routes transcript to appropriate processing agent
"""

import logging
from typing import Dict, Any, Optional, List
from marketing_project.core.models import TranscriptContext, AppContext
from marketing_project.core.parsers import parse_transcript, clean_text
from marketing_project.services.ocr import enhance_content_with_ocr, extract_images_from_content

logger = logging.getLogger("marketing_project.plugins.transcripts")

def analyze_transcript_type(transcript: TranscriptContext) -> str:
    """
    Analyzes the transcript type and returns processing category.
    
    Args:
        transcript: Transcript context object
        
    Returns:
        str: Processing category (podcast, video, meeting, interview, etc.)
    """
    transcript_type = transcript.transcript_type.lower()
    
    if "podcast" in transcript_type:
        return "podcast"
    elif "video" in transcript_type or "youtube" in transcript_type:
        return "video"
    elif "meeting" in transcript_type or "call" in transcript_type:
        return "meeting"
    elif "interview" in transcript_type:
        return "interview"
    else:
        return "general"

def extract_transcript_metadata(transcript: TranscriptContext) -> Dict[str, Any]:
    """
    Extracts metadata from transcript for processing decisions.
    
    Args:
        transcript: Transcript context object
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    # Parse the transcript content to extract additional metadata
    parsed_data = parse_transcript(transcript.content, transcript.transcript_type)
    
    metadata = {
        "content_type": "transcript",
        "id": transcript.id,
        "title": transcript.title,
        "speakers": transcript.speakers or parsed_data.get("speakers", []),
        "duration": transcript.duration or parsed_data.get("estimated_duration"),
        "transcript_type": transcript.transcript_type,
        "has_timestamps": bool(transcript.timestamps or parsed_data.get("timestamps")),
        "speaker_count": len(transcript.speakers or parsed_data.get("speakers", [])),
        "word_count": len(transcript.content.split()) if transcript.content else 0,
        "parsed_speakers": parsed_data.get("speakers", []),
        "parsed_timestamps": parsed_data.get("timestamps", {}),
        "cleaned_content": parsed_data.get("cleaned_content", transcript.content)
    }
    
    if transcript.timestamps or parsed_data.get("timestamps"):
        metadata["timestamp_count"] = len(transcript.timestamps or parsed_data.get("timestamps", {}))
    
    return metadata

def validate_transcript_structure(transcript: TranscriptContext) -> bool:
    """
    Validates that the transcript has the required structure for processing.
    
    Args:
        transcript: Transcript context object
        
    Returns:
        bool: True if transcript is valid, False otherwise
    """
    required_fields = ["id", "title", "content", "snippet", "transcript_type"]
    
    for field in required_fields:
        if not hasattr(transcript, field) or not getattr(transcript, field):
            logger.error(f"Transcript missing required field: {field}")
            return False
    
    # Validate transcript-specific fields
    if not transcript.speakers:
        logger.warning("Transcript has no speakers defined")
    
    return True

def enhance_transcript_with_ocr(transcript: TranscriptContext, image_urls: List[str] = None) -> Dict[str, Any]:
    """
    Enhance transcript content with OCR text from images.
    
    Args:
        transcript: Transcript context object
        image_urls: List of image URLs to process with OCR
        
    Returns:
        Dict[str, Any]: Enhanced transcript data with OCR text
    """
    # Extract images from content if not provided
    if not image_urls:
        image_urls = extract_images_from_content(transcript.content)
    
    # Enhance content with OCR
    enhanced_data = enhance_content_with_ocr(
        transcript.content, 
        "transcript", 
        image_urls=image_urls
    )
    
    return {
        "original_transcript": transcript,
        "enhanced_content": enhanced_data["enhanced_content"],
        "ocr_text": enhanced_data["ocr_text"],
        "has_visual_content": enhanced_data["has_visual_content"],
        "image_count": enhanced_data["image_count"],
        "visual_transcript": enhanced_data["visual_transcript"]
    }

def route_transcript_processing(app_context: AppContext, available_agents: Dict[str, Any]) -> str:
    """
    Routes transcript content to the appropriate processing agent.
    
    Args:
        app_context: Application context with transcript content
        available_agents: Dictionary of available agents
        
    Returns:
        str: Result of the routing operation
    """
    if not isinstance(app_context.content, TranscriptContext):
        return "Error: Content is not a transcript"
    
    transcript = app_context.content
    processing_type = analyze_transcript_type(transcript)
    
    # Map processing types to agent names - use the actual transcripts_agent for all types
    agent_mapping = {
        "podcast": "transcripts_agent",
        "video": "transcripts_agent", 
        "meeting": "transcripts_agent",
        "interview": "transcripts_agent",
        "general": "transcripts_agent"
    }
    
    agent_name = agent_mapping.get(processing_type, "transcripts_agent")
    
    if agent_name in available_agents and available_agents[agent_name]:
        logger.info(f"Routing {processing_type} transcript to {agent_name}")
        return f"Successfully routed {processing_type} transcript to {agent_name}"
    else:
        logger.warning(f"No agent available for {processing_type} transcript, using general processing")
        return f"No specialized agent for {processing_type} transcript, using general processing"
