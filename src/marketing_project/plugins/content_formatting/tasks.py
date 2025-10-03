"""
Content Formatting processing plugin tasks for Marketing Project.

This module provides functions to format and finalize content
for publication with proper styling, structure, and visual elements.

Functions:
    apply_formatting_rules: Applies consistent formatting rules
    optimize_readability: Optimizes content for better readability
    add_visual_elements: Adds visual elements and formatting
    finalize_content: Finalizes content for publication
    validate_formatting: Validates formatting compliance
    generate_publication_ready_content: Generates final publication-ready content
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from marketing_project.core.models import ContentContext, AppContext
from marketing_project.core.utils import (
    ensure_content_context, create_standard_task_result,
    validate_content_for_processing, extract_content_metadata_for_pipeline
)

logger = logging.getLogger("marketing_project.plugins.content_formatting")

def apply_formatting_rules(article: Union[Dict[str, Any], ContentContext], style_guide: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Applies consistent formatting rules to content.
    
    Args:
        article: Article dictionary with content or ContentContext
        style_guide: Style guide configuration
        
    Returns:
        Dict[str, Any]: Standardized task result with formatted content
    """
    try:
        # Handle both dict and ContentContext inputs
        if isinstance(article, ContentContext):
            article_data = {
                'content': article.content,
                'title': article.title,
                'meta_description': ''
            }
        else:
            article_data = article
        
        if not style_guide:
            style_guide = {
                'heading_style': 'title_case',
                'list_style': 'bullet',
                'paragraph_spacing': 'double',
                'quote_style': 'blockquote',
                'code_style': 'fenced',
                'link_style': 'markdown',
                'emphasis_style': 'bold_italic'
            }
        
        formatted_article = article_data.copy()
        content = article_data.get('content', '')
        
        # Apply heading formatting
        if style_guide['heading_style'] == 'title_case':
            content = format_headings_title_case(content)
        elif style_guide['heading_style'] == 'sentence_case':
            content = format_headings_sentence_case(content)
        
        # Apply list formatting
        if style_guide['list_style'] == 'bullet':
            content = format_lists_bullet(content)
        elif style_guide['list_style'] == 'numbered':
            content = format_lists_numbered(content)
        
        # Apply paragraph spacing
        if style_guide['paragraph_spacing'] == 'double':
            content = format_paragraph_spacing(content, double=True)
        else:
            content = format_paragraph_spacing(content, double=False)
        
        # Apply quote formatting
        if style_guide['quote_style'] == 'blockquote':
            content = format_quotes_blockquote(content)
        
        # Apply code formatting
        if style_guide['code_style'] == 'fenced':
            content = format_code_fenced(content)
        
        # Apply link formatting
        if style_guide['link_style'] == 'markdown':
            content = format_links_markdown(content)
        
        # Apply emphasis formatting
        if style_guide['emphasis_style'] == 'bold_italic':
            content = format_emphasis_bold_italic(content)
        
        formatted_article['content'] = content
        formatted_article['formatting_applied'] = True
        formatted_article['style_guide_used'] = style_guide
        
        return create_standard_task_result(
            success=True,
            data=formatted_article,
            task_name='apply_formatting_rules',
            metadata={
                'style_guide_used': style_guide,
                'content_length': len(content),
                'formatting_applied': True
            }
        )
        
    except Exception as e:
        logger.error(f"Error in apply_formatting_rules: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Formatting failed: {str(e)}",
            task_name='apply_formatting_rules'
        )

def optimize_readability(article: Union[Dict[str, Any], ContentContext]) -> Dict[str, Any]:
    """
    Optimizes content for better readability.
    
    Args:
        article: Article dictionary with content or ContentContext
        
    Returns:
        Dict[str, Any]: Standardized task result with optimized content
    """
    try:
        # Handle both dict and ContentContext inputs
        if isinstance(article, ContentContext):
            article_data = {
                'content': article.content,
                'title': article.title,
                'meta_description': ''
            }
        else:
            article_data = article
        
        optimized_article = article_data.copy()
        content = article_data.get('content', '')
        
        # Break up long paragraphs
        content = break_long_paragraphs(content, max_sentences=4)
        
        # Add subheadings for long sections
        content = add_subheadings_for_sections(content)
        
        # Improve sentence structure
        content = improve_sentence_structure(content)
        
        # Add transition words
        content = add_transition_words(content)
        
        # Format lists for better readability
        content = format_lists_for_readability(content)
        
        # Add white space for visual breathing room
        content = add_visual_breathing_room(content)
        
        optimized_article['content'] = content
        optimized_article['readability_optimized'] = True
        
        # Calculate readability metrics
        readability_metrics = calculate_readability_metrics(content)
        optimized_article['readability_metrics'] = readability_metrics
        
        return create_standard_task_result(
            success=True,
            data=optimized_article,
            task_name='optimize_readability',
            metadata={
                'readability_optimized': True,
                'content_length': len(content),
                'readability_metrics': readability_metrics
            }
        )
        
    except Exception as e:
        logger.error(f"Error in optimize_readability: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Readability optimization failed: {str(e)}",
            task_name='optimize_readability'
        )

def add_visual_elements(article: Dict[str, Any], visual_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Adds visual elements and formatting to enhance content.
    
    Args:
        article: Article dictionary with content
        visual_config: Visual configuration settings
        
    Returns:
        Dict[str, Any]: Content with visual elements added
    """
    if not visual_config:
        visual_config = {
            'add_images': True,
            'add_callouts': True,
            'add_quotes': True,
            'add_code_blocks': True,
            'add_tables': True,
            'add_icons': False
        }
    
    enhanced_article = article.copy()
    content = article.get('content', '')
    
    # Add image placeholders
    if visual_config['add_images']:
        content = add_image_placeholders(content)
    
    # Add callout boxes
    if visual_config['add_callouts']:
        content = add_callout_boxes(content)
    
    # Add quote blocks
    if visual_config['add_quotes']:
        content = add_quote_blocks(content)
    
    # Add code blocks
    if visual_config['add_code_blocks']:
        content = add_code_blocks(content)
    
    # Add tables
    if visual_config['add_tables']:
        content = add_tables(content)
    
    # Add icons
    if visual_config['add_icons']:
        content = add_icons(content)
    
    enhanced_article['content'] = content
    enhanced_article['visual_elements_added'] = True
    enhanced_article['visual_config'] = visual_config
    
    return enhanced_article

def finalize_content(article: Dict[str, Any], publication_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Finalizes content for publication.
    
    Args:
        article: Article dictionary with content
        publication_config: Publication configuration settings
        
    Returns:
        Dict[str, Any]: Finalized content ready for publication
    """
    if not publication_config:
        publication_config = {
            'add_metadata': True,
            'add_toc': True,
            'add_footer': True,
            'add_author_info': True,
            'add_publication_date': True,
            'add_tags': True
        }
    
    finalized_article = article.copy()
    content = article.get('content', '')
    
    # Add table of contents
    if publication_config['add_toc']:
        toc = generate_table_of_contents(content)
        if toc:
            content = f"{toc}\n\n{content}"
    
    # Add metadata header
    if publication_config['add_metadata']:
        metadata = generate_metadata_header(article, publication_config)
        content = f"{metadata}\n\n{content}"
    
    # Add footer
    if publication_config['add_footer']:
        footer = generate_footer(article, publication_config)
        content = f"{content}\n\n{footer}"
    
    # Clean up formatting
    content = clean_up_formatting(content)
    
    # Validate final content
    validation_results = validate_final_content(content)
    
    finalized_article['content'] = content
    finalized_article['finalized'] = True
    finalized_article['publication_config'] = publication_config
    finalized_article['validation_results'] = validation_results
    
    return finalized_article

def validate_formatting(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates formatting compliance and quality.
    
    Args:
        article: Article dictionary with content
        
    Returns:
        Dict[str, Any]: Formatting validation results
    """
    validation = {
        'overall_score': 0,
        'checks_passed': 0,
        'total_checks': 0,
        'issues': [],
        'recommendations': [],
        'compliance_status': 'unknown'
    }
    
    content = article.get('content', '')
    
    # Define formatting checks
    checks = [
        ('has_title', bool(article.get('title'))),
        ('has_meta_description', bool(article.get('meta_description'))),
        ('has_headings', '#' in content),
        ('has_proper_heading_hierarchy', check_heading_hierarchy(content)),
        ('has_lists', any(marker in content for marker in ['- ', '* ', '1. ', '2. '])),
        ('has_links', '](' in content),
        ('has_images', '![' in content),
        ('paragraph_length_ok', check_paragraph_lengths(content)),
        ('sentence_length_ok', check_sentence_lengths(content)),
        ('has_proper_spacing', check_proper_spacing(content)),
        ('has_call_to_action', check_call_to_action(content)),
        ('has_metadata', '---' in content or 'metadata:' in content)
    ]
    
    # Run checks
    for check_name, check_result in checks:
        validation['total_checks'] += 1
        if check_result:
            validation['checks_passed'] += 1
        else:
            validation['issues'].append(f"Failed check: {check_name}")
    
    # Calculate overall score
    validation['overall_score'] = (validation['checks_passed'] / validation['total_checks']) * 100
    
    # Determine compliance status
    if validation['overall_score'] >= 90:
        validation['compliance_status'] = 'excellent'
    elif validation['overall_score'] >= 80:
        validation['compliance_status'] = 'good'
    elif validation['overall_score'] >= 70:
        validation['compliance_status'] = 'acceptable'
    else:
        validation['compliance_status'] = 'needs_improvement'
    
    # Generate recommendations
    if validation['overall_score'] < 80:
        validation['recommendations'] = [
            'Add more visual elements (images, callouts)',
            'Improve heading structure',
            'Add more internal links',
            'Optimize paragraph and sentence lengths',
            'Add call-to-action elements'
        ]
    
    return validation

def generate_publication_ready_content(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates final publication-ready content with all optimizations applied.
    
    Args:
        article: Article dictionary with content
        
    Returns:
        Dict[str, Any]: Publication-ready content
    """
    publication_ready = article.copy()
    
    # Apply all formatting steps
    publication_ready = apply_formatting_rules(publication_ready)
    publication_ready = optimize_readability(publication_ready)
    publication_ready = add_visual_elements(publication_ready)
    publication_ready = finalize_content(publication_ready)
    
    # Final validation
    validation = validate_formatting(publication_ready)
    publication_ready['final_validation'] = validation
    
    # Generate summary
    publication_ready['publication_summary'] = {
        'word_count': len(publication_ready['content'].split()),
        'reading_time': calculate_reading_time(publication_ready['content']),
        'formatting_score': validation['overall_score'],
        'ready_for_publication': validation['overall_score'] >= 70,
        'last_updated': datetime.now().isoformat()
    }
    
    return publication_ready

# Helper functions

def format_headings_title_case(content: str) -> str:
    """Format headings to title case."""
    def title_case_heading(match):
        heading_text = match.group(1)
        return f"# {heading_text.title()}"
    
    content = re.sub(r'^# (.+)$', title_case_heading, content, flags=re.MULTILINE)
    return content

def format_headings_sentence_case(content: str) -> str:
    """Format headings to sentence case."""
    def sentence_case_heading(match):
        heading_text = match.group(1)
        return f"# {heading_text.capitalize()}"
    
    content = re.sub(r'^# (.+)$', sentence_case_heading, content, flags=re.MULTILINE)
    return content

def format_lists_bullet(content: str) -> str:
    """Format lists with bullet points."""
    # Convert numbered lists to bullet lists
    content = re.sub(r'^\d+\. ', '- ', content, flags=re.MULTILINE)
    return content

def format_lists_numbered(content: str) -> str:
    """Format lists with numbers."""
    # Convert bullet lists to numbered lists
    lines = content.split('\n')
    in_list = False
    list_counter = 1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('- '):
            if not in_list:
                in_list = True
                list_counter = 1
            lines[i] = re.sub(r'^- ', f'{list_counter}. ', line)
            list_counter += 1
        else:
            in_list = False
    
    return '\n'.join(lines)

def format_paragraph_spacing(content: str, double: bool = True) -> str:
    """Format paragraph spacing."""
    if double:
        # Ensure double spacing between paragraphs
        content = re.sub(r'\n\n+', '\n\n', content)
    else:
        # Ensure single spacing between paragraphs
        content = re.sub(r'\n+', '\n', content)
    
    return content

def format_quotes_blockquote(content: str) -> str:
    """Format quotes as blockquotes."""
    # Find quoted text and convert to blockquotes
    quote_pattern = r'"([^"]+)"'
    content = re.sub(quote_pattern, r'> \1', content)
    return content

def format_code_fenced(content: str) -> str:
    """Format code blocks with fenced syntax."""
    # Convert indented code blocks to fenced blocks
    code_pattern = r'^    (.+)$'
    content = re.sub(code_pattern, r'```\n\1\n```', content, flags=re.MULTILINE)
    return content

def format_links_markdown(content: str) -> str:
    """Ensure links are in markdown format."""
    # Convert plain URLs to markdown links
    url_pattern = r'(https?://[^\s]+)'
    content = re.sub(url_pattern, r'[\1](\1)', content)
    return content

def format_emphasis_bold_italic(content: str) -> str:
    """Format emphasis with bold and italic."""
    # Convert *text* to **text** for bold
    content = re.sub(r'\*([^*]+)\*', r'**\1**', content)
    return content

def break_long_paragraphs(content: str, max_sentences: int = 4) -> str:
    """Break up long paragraphs for better readability."""
    paragraphs = content.split('\n\n')
    improved_paragraphs = []
    
    for paragraph in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        if len(sentences) > max_sentences:
            # Split into smaller paragraphs
            for i in range(0, len(sentences), max_sentences):
                chunk = ' '.join(sentences[i:i+max_sentences])
                improved_paragraphs.append(chunk)
        else:
            improved_paragraphs.append(paragraph)
    
    return '\n\n'.join(improved_paragraphs)

def add_subheadings_for_sections(content: str) -> str:
    """Add subheadings for long sections."""
    # This is a simplified implementation
    # In practice, you'd use more sophisticated content analysis
    return content

def improve_sentence_structure(content: str) -> str:
    """Improve sentence structure for better readability."""
    # This is a simplified implementation
    # In practice, you'd use NLP libraries for better sentence improvement
    return content

def add_transition_words(content: str) -> str:
    """Add transition words to improve flow."""
    # Add transition words at the beginning of paragraphs
    transition_words = ['Additionally', 'Furthermore', 'Moreover', 'However', 'Therefore', 'Consequently']
    return content

def format_lists_for_readability(content: str) -> str:
    """Format lists for better readability."""
    # Ensure consistent list formatting
    content = re.sub(r'^[-*]\s+', '- ', content, flags=re.MULTILINE)
    return content

def add_visual_breathing_room(content: str) -> str:
    """Add white space for visual breathing room."""
    # Add extra spacing around headings
    content = re.sub(r'^(#{1,6} .+)$', r'\n\1\n', content, flags=re.MULTILINE)
    return content

def add_image_placeholders(content: str) -> str:
    """Add image placeholders to content."""
    # Add image placeholders after headings
    content = re.sub(r'^(#{1,6} .+)$', r'\1\n\n![Image placeholder](placeholder.jpg)\n', content, flags=re.MULTILINE)
    return content

def add_callout_boxes(content: str) -> str:
    """Add callout boxes for important information."""
    # Add callout boxes for important information
    important_pattern = r'(Important: [^.!?]+[.!?])'
    content = re.sub(important_pattern, r'> **Important:** \1', content)
    return content

def add_quote_blocks(content: str) -> str:
    """Add quote blocks for highlighted text."""
    # Convert quoted text to blockquotes
    quote_pattern = r'"([^"]+)"'
    content = re.sub(quote_pattern, r'> \1', content)
    return content

def add_code_blocks(content: str) -> str:
    """Add code blocks for technical content."""
    # Add code blocks for technical terms
    code_terms = ['function', 'variable', 'class', 'method', 'API', 'endpoint']
    for term in code_terms:
        content = re.sub(rf'\b{term}\b', f'`{term}`', content)
    return content

def add_tables(content: str) -> str:
    """Add tables for structured data."""
    # This is a simplified implementation
    # In practice, you'd detect tabular data and format it properly
    return content

def add_icons(content: str) -> str:
    """Add icons to enhance visual appeal."""
    # Add icons for different content types
    content = re.sub(r'^(#{1,6} .+)$', r'📝 \1', content, flags=re.MULTILINE)
    return content

def generate_table_of_contents(content: str) -> str:
    """Generate table of contents from headings."""
    headings = re.findall(r'^(#{1,6}) (.+)$', content, re.MULTILINE)
    if not headings:
        return ""
    
    toc = "## Table of Contents\n\n"
    for level, heading in headings:
        indent = "  " * (len(level) - 1)
        link = heading.lower().replace(' ', '-').replace(':', '')
        toc += f"{indent}- [{heading}](#{link})\n"
    
    return toc

def generate_metadata_header(article: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate metadata header for the article."""
    metadata = "---\n"
    metadata += f"title: {article.get('title', 'Untitled')}\n"
    metadata += f"description: {article.get('meta_description', '')}\n"
    
    if config.get('add_author_info'):
        metadata += f"author: {article.get('author', 'Marketing Team')}\n"
    
    if config.get('add_publication_date'):
        metadata += f"date: {datetime.now().strftime('%Y-%m-%d')}\n"
    
    if config.get('add_tags'):
        metadata += f"tags: {', '.join(article.get('tags', []))}\n"
    
    metadata += "---\n"
    return metadata

def generate_footer(article: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate footer for the article."""
    footer = "---\n\n"
    footer += "## About This Article\n\n"
    footer += f"This article was generated as part of our content marketing strategy.\n\n"
    footer += "**Related Resources:**\n"
    footer += "- [Blog Home](/blog)\n"
    footer += "- [Resources](/resources)\n"
    footer += "- [Contact Us](/contact)\n"
    return footer

def clean_up_formatting(content: str) -> str:
    """Clean up formatting issues."""
    # Remove extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    # Remove trailing whitespace
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)
    return content

def validate_final_content(content: str) -> Dict[str, Any]:
    """Validate final content quality."""
    return {
        'word_count': len(content.split()),
        'character_count': len(content),
        'paragraph_count': len(content.split('\n\n')),
        'heading_count': len(re.findall(r'^#{1,6} ', content, re.MULTILINE)),
        'link_count': len(re.findall(r'\[.*?\]\(.*?\)', content)),
        'image_count': len(re.findall(r'!\[.*?\]\(.*?\)', content))
    }

def calculate_readability_metrics(content: str) -> Dict[str, Any]:
    """Calculate readability metrics."""
    words = content.split()
    sentences = re.split(r'[.!?]+', content)
    words = [w for w in words if w.strip()]
    sentences = [s for s in sentences if s.strip()]
    
    if not sentences:
        return {'score': 0, 'level': 'unknown'}
    
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables = sum(estimate_syllables(word) for word in words) / len(words)
    
    # Simplified Flesch Reading Ease
    score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
    
    if score >= 90:
        level = 'very_easy'
    elif score >= 80:
        level = 'easy'
    elif score >= 70:
        level = 'fairly_easy'
    elif score >= 60:
        level = 'standard'
    elif score >= 50:
        level = 'fairly_difficult'
    elif score >= 30:
        level = 'difficult'
    else:
        level = 'very_difficult'
    
    return {
        'score': max(0, min(100, score)),
        'level': level,
        'avg_sentence_length': avg_sentence_length,
        'avg_syllables_per_word': avg_syllables
    }

def calculate_reading_time(content: str) -> str:
    """Calculate estimated reading time."""
    word_count = len(content.split())
    reading_time = max(1, word_count // 200)  # 200 words per minute
    return f"{reading_time} minute{'s' if reading_time != 1 else ''}"

def estimate_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower().strip('.,!?')
    if not word:
        return 0
    
    vowels = 'aeiouy'
    syllable_count = 0
    prev_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel
    
    # Handle silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)

def check_heading_hierarchy(content: str) -> bool:
    """Check if heading hierarchy is proper."""
    headings = re.findall(r'^(#{1,6}) ', content, re.MULTILINE)
    if not headings:
        return False
    
    # Check for proper hierarchy (H1 -> H2 -> H3, etc.)
    prev_level = 0
    for heading in headings:
        level = len(heading)
        if level > prev_level + 1:
            return False
        prev_level = level
    
    return True

def check_paragraph_lengths(content: str) -> bool:
    """Check if paragraph lengths are appropriate."""
    paragraphs = content.split('\n\n')
    for paragraph in paragraphs:
        if len(paragraph.split()) > 200:  # Too long
            return False
    return True

def check_sentence_lengths(content: str) -> bool:
    """Check if sentence lengths are appropriate."""
    sentences = re.split(r'[.!?]+', content)
    for sentence in sentences:
        if len(sentence.split()) > 30:  # Too long
            return False
    return True

def check_proper_spacing(content: str) -> bool:
    """Check if content has proper spacing."""
    # Check for proper spacing around headings
    if re.search(r'^#{1,6} .+[^\\n]', content, re.MULTILINE):
        return False
    return True

def check_call_to_action(content: str) -> bool:
    """Check if content has call-to-action elements."""
    cta_indicators = ['learn more', 'get started', 'read more', 'contact us', 'subscribe']
    content_lower = content.lower()
    return any(cta in content_lower for cta in cta_indicators)
