"""
Article Generation processing plugin tasks for Marketing Project.

This module provides functions to generate high-quality articles
based on marketing briefs, SEO keywords, and content strategy.

Functions:
    generate_article_structure: Creates article structure and outline
    write_article_content: Writes the main article content
    add_supporting_elements: Adds images, quotes, and other supporting elements
    review_article_quality: Reviews and improves article quality
    optimize_article_flow: Optimizes article flow and readability
    add_call_to_actions: Adds strategic call-to-action elements
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

logger = logging.getLogger("marketing_project.plugins.article_generation")

def generate_article_structure(marketing_brief: Union[Dict[str, Any], ContentContext], seo_keywords: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generates article structure and outline based on marketing brief.
    
    Args:
        marketing_brief: Marketing brief dictionary or ContentContext
        seo_keywords: List of SEO keywords for optimization
        
    Returns:
        Dict[str, Any]: Standardized task result with article structure
    """
    try:
        # Handle both dict and ContentContext inputs
        if isinstance(marketing_brief, ContentContext):
            brief_data = {
                'title': marketing_brief.title,
                'executive_summary': marketing_brief.snippet,
                'content_pillars': [],
                'target_audience': {}
            }
        else:
            brief_data = marketing_brief
        
        structure = {
            'title': '',
            'meta_description': '',
            'introduction': {},
            'main_sections': [],
            'conclusion': {},
            'word_count_target': 1500,
            'reading_time_estimate': '5-7 minutes',
            'seo_optimization': {},
            'content_pillars': [],
            'target_audience': {}
        }
        
        # Generate title based on brief and keywords
        title = brief_data.get('title', 'Untitled Article')
        primary_keyword = ''
        if seo_keywords and len(seo_keywords) > 0:
            primary_keyword = seo_keywords[0]['keyword']
            if primary_keyword.lower() not in title.lower():
                title = f"{title}: {primary_keyword.title()}"
        
        structure['title'] = title
        
        # Generate meta description
        executive_summary = brief_data.get('executive_summary', '')
        if executive_summary:
            meta_desc = executive_summary[:150] + '...' if len(executive_summary) > 150 else executive_summary
        else:
            meta_desc = f"Learn about {primary_keyword if primary_keyword else 'this topic'} with our comprehensive guide."
        
        structure['meta_description'] = meta_desc
        
        # Generate introduction structure
        structure['introduction'] = {
            'hook': 'Compelling opening statement',
            'problem_statement': 'What problem does this solve?',
            'solution_preview': 'What will readers learn?',
            'value_proposition': 'Why should they read this?',
            'word_count': 150
        }
        
        # Generate main sections based on content pillars
        content_pillars = brief_data.get('content_pillars', ['Main Topic'])
        for i, pillar in enumerate(content_pillars[:4]):  # Limit to 4 main sections
            section = {
                'heading': f"H2: {pillar}",
                'subheadings': [],
                'key_points': [],
                'word_count': 300,
                'seo_keywords': []
            }
            
            # Add subheadings
            if i == 0:
                section['subheadings'] = ['H3: Getting Started', 'H3: Key Concepts']
            elif i == 1:
                section['subheadings'] = ['H3: Best Practices', 'H3: Common Mistakes']
            elif i == 2:
                section['subheadings'] = ['H3: Advanced Techniques', 'H3: Tools and Resources']
            else:
                section['subheadings'] = ['H3: Implementation', 'H3: Next Steps']
            
            # Add relevant keywords to each section
            if seo_keywords:
                section['seo_keywords'] = [kw['keyword'] for kw in seo_keywords[i*2:(i+1)*2]]
            
            structure['main_sections'].append(section)
        
        # Generate conclusion structure
        structure['conclusion'] = {
            'summary': 'Key takeaways summary',
            'call_to_action': 'What should readers do next?',
            'related_topics': 'Suggestions for further reading',
            'word_count': 100
        }
        
        # Set SEO optimization targets
        if seo_keywords and len(seo_keywords) > 0:
            structure['seo_optimization'] = {
                'primary_keyword': seo_keywords[0]['keyword'],
                'secondary_keywords': [kw['keyword'] for kw in seo_keywords[1:4]] if len(seo_keywords) > 1 else [],
                'keyword_density_target': '1-3%',
                'title_optimization': 'Include primary keyword in title',
                'heading_optimization': 'Include keywords in H2 and H3 tags'
            }
        else:
            structure['seo_optimization'] = {
                'primary_keyword': '',
                'secondary_keywords': [],
                'keyword_density_target': '1-3%',
                'title_optimization': 'Include primary keyword in title',
                'heading_optimization': 'Include keywords in H2 and H3 tags'
            }
        
        # Set content pillars and target audience
        structure['content_pillars'] = content_pillars
        structure['target_audience'] = brief_data.get('target_audience', {})
        
        return create_standard_task_result(
            success=True,
            data=structure,
            task_name='generate_article_structure',
            metadata={
                'content_pillars_count': len(content_pillars),
                'main_sections_count': len(structure['main_sections']),
                'seo_keywords_count': len(seo_keywords) if seo_keywords else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Error in generate_article_structure: {str(e)}")
        # Return a simple dict instead of calling create_standard_task_result
        # to avoid potential issues if that function is also failing
        return {
            'success': False,
            'error': f"Article structure generation failed: {str(e)}",
            'task_name': 'generate_article_structure'
        }

def write_article_content(structure: Dict[str, Any], source_content: ContentContext = None) -> Dict[str, Any]:
    """
    Writes the main article content based on structure.
    
    Args:
        structure: Article structure dictionary
        source_content: Source content for reference
        
    Returns:
        Dict[str, Any]: Generated article content
    """
    article = {
        'title': structure['title'],
        'meta_description': structure['meta_description'],
        'content': '',
        'word_count': 0,
        'reading_time': '',
        'sections': [],
        'quality_score': 0,
        'seo_score': 0
    }
    
    # Write introduction
    intro = write_introduction(structure['introduction'], structure.get('target_audience', {}))
    article['sections'].append({
        'type': 'introduction',
        'heading': 'Introduction',
        'content': intro,
        'word_count': len(intro.split())
    })
    
    # Write main sections
    for section_structure in structure['main_sections']:
        section_content = write_main_section(section_structure, source_content)
        article['sections'].append({
            'type': 'main_section',
            'heading': section_structure['heading'],
            'content': section_content,
            'word_count': len(section_content.split()),
            'subheadings': section_structure['subheadings']
        })
    
    # Write conclusion
    conclusion = write_conclusion(structure['conclusion'], structure.get('target_audience', {}))
    article['sections'].append({
        'type': 'conclusion',
        'heading': 'Conclusion',
        'content': conclusion,
        'word_count': len(conclusion.split())
    })
    
    # Combine all content
    full_content = f"# {article['title']}\n\n"
    for section in article['sections']:
        full_content += f"## {section['heading']}\n\n{section['content']}\n\n"
    
    article['content'] = full_content
    article['word_count'] = len(full_content.split())
    article['reading_time'] = f"{article['word_count'] // 200 + 1} minutes"
    
    return article

def add_supporting_elements(article: Dict[str, Any], content_type: str = 'article') -> Dict[str, Any]:
    """
    Adds supporting elements like images, quotes, and callouts.
    
    Args:
        article: Article dictionary
        content_type: Type of content being generated
        
    Returns:
        Dict[str, Any]: Article with supporting elements
    """
    enhanced_article = article.copy()
    enhanced_article['supporting_elements'] = {
        'images': [],
        'quotes': [],
        'callouts': [],
        'lists': [],
        'tables': [],
        'code_blocks': []
    }
    
    # Add images based on content
    content = article['content']
    
    # Suggest images for each main section
    for i, section in enumerate(article['sections']):
        if section['type'] == 'main_section':
            image_suggestion = {
                'type': 'infographic' if 'best practices' in section['heading'].lower() else 'illustration',
                'alt_text': f"Visual representation of {section['heading']}",
                'placement': 'after_heading',
                'description': f"Image to illustrate concepts in {section['heading']}"
            }
            enhanced_article['supporting_elements']['images'].append(image_suggestion)
    
    # Add quotes based on content type
    if content_type in ['tutorial', 'guide']:
        enhanced_article['supporting_elements']['quotes'].append({
            'text': '"The best way to learn is by doing."',
            'author': 'Industry Expert',
            'placement': 'introduction'
        })
    elif content_type in ['review', 'analysis']:
        enhanced_article['supporting_elements']['quotes'].append({
            'text': '"Data-driven insights lead to better decisions."',
            'author': 'Analytics Professional',
            'placement': 'main_content'
        })
    
    # Add callouts for key information
    callout_keywords = ['important', 'note', 'tip', 'warning', 'remember']
    for section in article['sections']:
        content_lower = section['content'].lower()
        for keyword in callout_keywords:
            if keyword in content_lower:
                enhanced_article['supporting_elements']['callouts'].append({
                    'type': 'info' if keyword in ['note', 'tip'] else 'warning' if keyword == 'warning' else 'highlight',
                    'content': f"Key {keyword.title()} from {section['heading']}",
                    'placement': section['heading']
                })
                break
    
    # Add lists for better readability
    list_indicators = ['first', 'second', 'third', 'steps', 'benefits', 'features']
    for section in article['sections']:
        content_lower = section['content'].lower()
        for indicator in list_indicators:
            if indicator in content_lower:
                enhanced_article['supporting_elements']['lists'].append({
                    'type': 'bulleted' if 'benefits' in indicator or 'features' in indicator else 'numbered',
                    'content': f"List of {indicator} from {section['heading']}",
                    'placement': section['heading']
                })
                break
    
    return enhanced_article

def review_article_quality(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reviews article quality and provides improvement suggestions.
    
    Args:
        article: Article dictionary to review
        
    Returns:
        Dict[str, Any]: Quality review results
    """
    review = {
        'overall_score': 0,
        'readability_score': 0,
        'seo_score': 0,
        'engagement_score': 0,
        'issues': [],
        'suggestions': [],
        'strengths': []
    }
    
    content = article['content']
    word_count = article['word_count']
    
    # Calculate readability score (simplified Flesch Reading Ease)
    sentences = content.count('.') + content.count('!') + content.count('?')
    words = len(content.split())
    syllables = estimate_syllables(content)
    
    if sentences > 0 and words > 0:
        readability_score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        review['readability_score'] = max(0, min(100, readability_score))
    
    # Calculate SEO score
    seo_score = 0
    seo_checks = {
        'has_title': bool(article.get('title')),
        'has_meta_description': bool(article.get('meta_description')),
        'title_length_ok': 30 <= len(article.get('title', '')) <= 60,
        'meta_length_ok': 120 <= len(article.get('meta_description', '')) <= 160,
        'has_headings': '##' in content,
        'word_count_ok': 1000 <= word_count <= 3000
    }
    
    seo_score = sum(seo_checks.values()) / len(seo_checks) * 100
    review['seo_score'] = seo_score
    
    # Calculate engagement score
    engagement_indicators = {
        'has_questions': '?' in content,
        'has_lists': any(marker in content for marker in ['- ', '* ', '1. ', '2. ']),
        'has_callouts': any(marker in content.lower() for marker in ['important:', 'note:', 'tip:']),
        'good_paragraph_length': check_paragraph_lengths(content),
        'has_transitions': check_transitions(content)
    }
    
    engagement_score = sum(engagement_indicators.values()) / len(engagement_indicators) * 100
    review['engagement_score'] = engagement_score
    
    # Calculate overall score
    review['overall_score'] = (review['readability_score'] + seo_score + engagement_score) / 3
    
    # Identify issues
    if review['readability_score'] < 60:
        review['issues'].append('Content may be difficult to read')
    if seo_score < 70:
        review['issues'].append('SEO optimization needs improvement')
    if engagement_score < 60:
        review['issues'].append('Content engagement could be improved')
    if word_count < 1000:
        review['issues'].append('Content may be too short')
    if word_count > 3000:
        review['issues'].append('Content may be too long')
    
    # Generate suggestions
    if not seo_checks['title_length_ok']:
        review['suggestions'].append('Optimize title length (30-60 characters)')
    if not seo_checks['meta_length_ok']:
        review['suggestions'].append('Optimize meta description length (120-160 characters)')
    if not seo_checks['has_headings']:
        review['suggestions'].append('Add more subheadings for better structure')
    if not engagement_indicators['has_questions']:
        review['suggestions'].append('Add questions to engage readers')
    if not engagement_indicators['has_lists']:
        review['suggestions'].append('Use lists to improve readability')
    
    # Identify strengths
    if review['readability_score'] > 80:
        review['strengths'].append('Excellent readability')
    if seo_score > 80:
        review['strengths'].append('Strong SEO optimization')
    if engagement_score > 80:
        review['strengths'].append('High engagement potential')
    if 1500 <= word_count <= 2500:
        review['strengths'].append('Optimal content length')
    
    return review

def optimize_article_flow(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimizes article flow and transitions between sections.
    
    Args:
        article: Article dictionary to optimize
        
    Returns:
        Dict[str, Any]: Optimized article with improved flow
    """
    optimized_article = article.copy()
    
    # Add transitions between sections
    transitions = [
        "Now that we've covered the basics, let's dive deeper into...",
        "Building on what we've learned, the next important aspect is...",
        "With this foundation in place, we can now explore...",
        "Having understood the key concepts, let's look at...",
        "Now that you have a solid understanding, let's move on to..."
    ]
    
    # Add transitions to main sections
    for i, section in enumerate(optimized_article['sections']):
        if section['type'] == 'main_section' and i > 0:
            transition = transitions[i % len(transitions)]
            section['content'] = f"{transition}\n\n{section['content']}"
    
    # Improve paragraph flow
    for section in optimized_article['sections']:
        if section['type'] in ['main_section', 'conclusion']:
            section['content'] = improve_paragraph_flow(section['content'])
    
    return optimized_article

def add_call_to_actions(article: Dict[str, Any], cta_strategy: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Adds strategic call-to-action elements throughout the article.
    
    Args:
        article: Article dictionary
        cta_strategy: CTA strategy configuration
        
    Returns:
        Dict[str, Any]: Article with CTAs added
    """
    enhanced_article = article.copy()
    
    if not cta_strategy:
        cta_strategy = {
            'primary_cta': 'Learn more about our solutions',
            'secondary_cta': 'Subscribe to our newsletter',
            'cta_placement': ['introduction', 'middle', 'conclusion']
        }
    
    enhanced_article['ctas'] = []
    
    # Add CTAs based on strategy
    for placement in cta_strategy['cta_placement']:
        if placement == 'introduction':
            cta = {
                'text': cta_strategy['primary_cta'],
                'type': 'primary',
                'placement': 'introduction',
                'action': 'Learn More'
            }
        elif placement == 'middle':
            cta = {
                'text': cta_strategy['secondary_cta'],
                'type': 'secondary',
                'placement': 'middle',
                'action': 'Subscribe'
            }
        else:  # conclusion
            cta = {
                'text': cta_strategy['primary_cta'],
                'type': 'primary',
                'placement': 'conclusion',
                'action': 'Get Started'
            }
        
        enhanced_article['ctas'].append(cta)
    
    return enhanced_article

# Helper functions

def write_introduction(intro_structure: Dict[str, Any], target_audience: Dict[str, Any]) -> str:
    """Write introduction content based on structure."""
    hook = intro_structure.get('hook', 'In today\'s fast-paced world')
    problem = intro_structure.get('problem_statement', 'many face challenges')
    solution = intro_structure.get('solution_preview', 'This guide will help you')
    value = intro_structure.get('value_proposition', 'achieve your goals')
    
    return f"{hook}, {problem}. {solution} {value}."

def write_main_section(section_structure: Dict[str, Any], source_content: ContentContext = None) -> str:
    """Write main section content based on structure."""
    heading = section_structure['heading']
    subheadings = section_structure.get('subheadings', [])
    keywords = section_structure.get('seo_keywords', [])
    
    content = f"This section covers {heading.lower()}.\n\n"
    
    for subheading in subheadings:
        content += f"### {subheading}\n\n"
        content += f"Here we explore the key aspects of {subheading.lower()}.\n\n"
    
    if keywords:
        content += f"Key terms to focus on: {', '.join(keywords)}.\n\n"
    
    return content

def write_conclusion(conclusion_structure: Dict[str, Any], target_audience: Dict[str, Any]) -> str:
    """Write conclusion content based on structure."""
    summary = conclusion_structure.get('summary', 'In summary')
    cta = conclusion_structure.get('call_to_action', 'Take action today')
    related = conclusion_structure.get('related_topics', 'Explore more topics')
    
    return f"{summary}, we've covered the essential points. {cta} and {related}."

def estimate_syllables(text: str) -> int:
    """Estimate syllable count for readability calculation."""
    words = text.split()
    syllables = 0
    for word in words:
        word = word.lower().strip('.,!?')
        if word:
            syllables += max(1, len(re.findall(r'[aeiouy]', word)))
    return syllables

def check_paragraph_lengths(content: str) -> bool:
    """Check if paragraphs are appropriate length."""
    paragraphs = content.split('\n\n')
    avg_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    return 50 <= avg_length <= 200

def check_transitions(content: str) -> bool:
    """Check if content has good transitions."""
    transition_words = ['however', 'moreover', 'furthermore', 'additionally', 'consequently', 'therefore']
    return any(word in content.lower() for word in transition_words)

def improve_paragraph_flow(content: str) -> str:
    """Improve paragraph flow by adding transitions."""
    paragraphs = content.split('\n\n')
    improved_paragraphs = []
    
    for i, paragraph in enumerate(paragraphs):
        if i > 0 and not any(word in paragraph.lower() for word in ['however', 'moreover', 'additionally', 'furthermore']):
            paragraph = f"Additionally, {paragraph.lower()}"
        improved_paragraphs.append(paragraph)
    
    return '\n\n'.join(improved_paragraphs)
