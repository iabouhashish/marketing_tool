"""
Blog post processing plugin tasks for Marketing Project.

This module provides functions to analyze, process, and route blog post content
including articles, tutorials, and other written content.

Functions:
    analyze_blog_post_type: Analyzes the type of blog post content
    extract_blog_post_metadata: Extracts metadata from blog post content
    validate_blog_post_structure: Validates blog post has required fields
    route_blog_post_processing: Routes blog post to appropriate processing agent
"""

import logging
from typing import Dict, Any, Optional, List
from marketing_project.core.models import BlogPostContext, AppContext
from marketing_project.core.parsers import parse_blog_post, clean_text
from marketing_project.services.ocr import enhance_content_with_ocr, extract_images_from_content

logger = logging.getLogger("marketing_project.plugins.blog_posts")

def analyze_blog_post_type(blog_post: BlogPostContext) -> str:
    """
    Analyzes the blog post type and returns processing category.
    
    Args:
        blog_post: Blog post context object
        
    Returns:
        str: Processing category (tutorial, article, news, review, etc.)
    """
    title_lower = blog_post.title.lower()
    content_lower = blog_post.content.lower()
    
    # Analyze based on title and content keywords
    if any(keyword in title_lower for keyword in ["tutorial", "how to", "guide", "step by step"]):
        return "tutorial"
    elif any(keyword in title_lower for keyword in ["review", "comparison", "vs"]):
        return "review"
    elif any(keyword in title_lower for keyword in ["news", "announcement", "update"]):
        return "news"
    elif any(keyword in title_lower for keyword in ["analysis", "deep dive", "explanation"]):
        return "analysis"
    elif blog_post.category:
        return blog_post.category.lower()
    else:
        return "general"

def extract_blog_post_metadata(blog_post: BlogPostContext) -> Dict[str, Any]:
    """
    Extracts metadata from blog post for processing decisions.
    
    Args:
        blog_post: Blog post context object
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    # Parse the blog post content to extract additional metadata
    parsed_data = parse_blog_post(blog_post.content, {
        "title": blog_post.title,
        "author": blog_post.author,
        "category": blog_post.category,
        "tags": blog_post.tags
    })
    
    metadata = {
        "content_type": "blog_post",
        "id": blog_post.id,
        "title": blog_post.title or parsed_data.get("title", ""),
        "author": blog_post.author or parsed_data.get("metadata", {}).get("author", ""),
        "category": blog_post.category or parsed_data.get("metadata", {}).get("category", ""),
        "tags": blog_post.tags or parsed_data.get("tags", []),
        "word_count": blog_post.word_count or parsed_data.get("word_count", 0),
        "reading_time": blog_post.reading_time or parsed_data.get("reading_time", ""),
        "tag_count": len(blog_post.tags or parsed_data.get("tags", [])),
        "has_author": bool(blog_post.author or parsed_data.get("metadata", {}).get("author")),
        "has_category": bool(blog_post.category or parsed_data.get("metadata", {}).get("category")),
        "headings": parsed_data.get("headings", []),
        "links": parsed_data.get("links", []),
        "parsed_tags": parsed_data.get("tags", []),
        "cleaned_content": parsed_data.get("cleaned_content", blog_post.content)
    }
    
    return metadata

def validate_blog_post_structure(blog_post: BlogPostContext) -> bool:
    """
    Validates that the blog post has the required structure for processing.
    
    Args:
        blog_post: Blog post context object
        
    Returns:
        bool: True if blog post is valid, False otherwise
    """
    required_fields = ["id", "title", "content", "snippet"]
    
    for field in required_fields:
        if not hasattr(blog_post, field) or not getattr(blog_post, field):
            logger.error(f"Blog post missing required field: {field}")
            return False
    
    return True

def enhance_blog_post_with_ocr(blog_post: BlogPostContext, image_urls: List[str] = None) -> Dict[str, Any]:
    """
    Enhance blog post content with OCR text from images.
    
    Args:
        blog_post: Blog post context object
        image_urls: List of image URLs to process with OCR
        
    Returns:
        Dict[str, Any]: Enhanced blog post data with OCR text
    """
    # Extract images from content if not provided
    if not image_urls:
        image_urls = extract_images_from_content(blog_post.content)
    
    # Enhance content with OCR
    enhanced_data = enhance_content_with_ocr(
        blog_post.content, 
        "blog_post", 
        image_urls=image_urls
    )
    
    return {
        "original_blog_post": blog_post,
        "enhanced_content": enhanced_data["enhanced_content"],
        "ocr_text": enhanced_data["ocr_text"],
        "has_images": enhanced_data["has_images"],
        "image_count": enhanced_data["image_count"],
        "image_alt_text": enhanced_data["image_alt_text"]
    }

def route_blog_post_processing(app_context: AppContext, available_agents: Dict[str, Any]) -> str:
    """
    Routes blog post content to the appropriate processing agent.
    
    Args:
        app_context: Application context with blog post content
        available_agents: Dictionary of available agents
        
    Returns:
        str: Result of the routing operation
    """
    if not isinstance(app_context.content, BlogPostContext):
        return "Error: Content is not a blog post"
    
    blog_post = app_context.content
    processing_type = analyze_blog_post_type(blog_post)
    
    # Map processing types to agent names
    agent_mapping = {
        "tutorial": "tutorial_agent",
        "review": "review_agent",
        "news": "news_agent",
        "analysis": "analysis_agent",
        "general": "general_blog_agent"
    }
    
    agent_name = agent_mapping.get(processing_type, "general_blog_agent")
    
    if agent_name in available_agents and available_agents[agent_name]:
        logger.info(f"Routing {processing_type} blog post to {agent_name}")
        return f"Successfully routed {processing_type} blog post to {agent_name}"
    else:
        logger.warning(f"No agent available for {processing_type} blog post, using general processing")
        return f"No specialized agent for {processing_type} blog post, using general processing"
