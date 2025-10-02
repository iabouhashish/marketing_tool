"""
SEO Optimization processing plugin tasks for Marketing Project.

This module provides functions to optimize content for search engines
including title tags, meta descriptions, headings, and content structure.

Functions:
    optimize_title_tags: Optimizes title tags for SEO
    optimize_meta_descriptions: Optimizes meta descriptions
    optimize_headings: Optimizes heading structure and content
    optimize_content_structure: Optimizes overall content structure
    add_internal_links: Adds strategic internal links
    analyze_seo_performance: Analyzes SEO performance metrics
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from marketing_project.core.models import ContentContext, AppContext
from marketing_project.core.utils import (
    ensure_content_context, create_standard_task_result,
    validate_content_for_processing, extract_content_metadata_for_pipeline
)

logger = logging.getLogger("marketing_project.plugins.seo_optimization")

def optimize_title_tags(article: Union[Dict[str, Any], ContentContext], keywords: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimizes title tags for better SEO performance.
    
    Args:
        article: Article dictionary with content or ContentContext
        keywords: List of SEO keywords for optimization
        
    Returns:
        Dict[str, Any]: Standardized task result with optimized title tags
    """
    try:
        # Handle both dict and ContentContext inputs
        if isinstance(article, ContentContext):
            article_data = {
                'title': article.title,
                'content': article.content,
                'meta_description': ''
            }
        else:
            article_data = article
        
        optimization = {
            'current_title': article_data.get('title', ''),
            'optimized_titles': [],
            'recommendations': [],
            'seo_score': 0,
            'character_count': 0
        }
        
        current_title = article_data.get('title', '')
        optimization['character_count'] = len(current_title)
        
        # Check title length
        if len(current_title) < 30:
            optimization['recommendations'].append('Title is too short (aim for 30-60 characters)')
        elif len(current_title) > 60:
            optimization['recommendations'].append('Title is too long (aim for 30-60 characters)')
        else:
            optimization['recommendations'].append('Title length is optimal')
        
        # Generate optimized titles
        if keywords and len(keywords) > 0:
            primary_keyword = keywords[0]['keyword']
            secondary_keywords = [kw['keyword'] for kw in keywords[1:3]]
            
            # Title variations
            title_variations = [
                f"{primary_keyword.title()}: Complete Guide",
                f"How to {primary_keyword.title()}: Expert Tips",
                f"{primary_keyword.title()} Best Practices for 2024",
                f"Ultimate {primary_keyword.title()} Guide",
                f"{primary_keyword.title()} - Everything You Need to Know"
            ]
            
            # Add secondary keywords if space allows
            for variation in title_variations:
                if len(variation) <= 60:
                    if secondary_keywords and len(variation) + len(secondary_keywords[0]) + 3 <= 60:
                        variation += f" & {secondary_keywords[0]}"
                    optimization['optimized_titles'].append(variation)
        
        # Check for power words
        power_words = ['ultimate', 'complete', 'guide', 'best', 'expert', 'proven', 'essential', 'comprehensive']
        has_power_words = any(word in current_title.lower() for word in power_words)
        if not has_power_words:
            optimization['recommendations'].append('Consider adding power words to increase click-through rate')
        
        # Check for emotional triggers
        emotional_words = ['amazing', 'incredible', 'shocking', 'secret', 'revealed', 'discovered']
        has_emotional_words = any(word in current_title.lower() for word in emotional_words)
        if not has_emotional_words:
            optimization['recommendations'].append('Consider adding emotional triggers to improve engagement')
        
        # Calculate SEO score
        seo_factors = {
            'length_ok': 30 <= len(current_title) <= 60,
            'has_keywords': any(kw['keyword'].lower() in current_title.lower() for kw in keywords) if keywords else False,
            'has_power_words': has_power_words,
            'has_emotional_words': has_emotional_words,
            'starts_with_keyword': current_title.lower().startswith(primary_keyword.lower()) if keywords and keywords else False
        }
        
        optimization['seo_score'] = sum(seo_factors.values()) / len(seo_factors) * 100
        
        return create_standard_task_result(
            success=True,
            data=optimization,
            task_name='optimize_title_tags',
            metadata={
                'current_title_length': len(current_title),
                'optimized_titles_count': len(optimization['optimized_titles']),
                'seo_score': optimization['seo_score']
            }
        )
        
    except Exception as e:
        logger.error(f"Error in optimize_title_tags: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Title optimization failed: {str(e)}",
            task_name='optimize_title_tags'
        )

def optimize_meta_descriptions(article: Union[Dict[str, Any], ContentContext], keywords: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimizes meta descriptions for better SEO performance.
    
    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for optimization
        
    Returns:
        Dict[str, Any]: Optimized meta descriptions and recommendations
    """
    optimization = {
        'current_meta': article.get('meta_description', ''),
        'optimized_meta': [],
        'recommendations': [],
        'seo_score': 0,
        'character_count': 0
    }
    
    current_meta = article.get('meta_description', '')
    optimization['character_count'] = len(current_meta)
    
    # Check meta description length
    if len(current_meta) < 120:
        optimization['recommendations'].append('Meta description is too short (aim for 120-160 characters)')
    elif len(current_meta) > 160:
        optimization['recommendations'].append('Meta description is too long (aim for 120-160 characters)')
    else:
        optimization['recommendations'].append('Meta description length is optimal')
    
    # Generate optimized meta descriptions
    if keywords and len(keywords) > 0:
        primary_keyword = keywords[0]['keyword']
        secondary_keywords = [kw['keyword'] for kw in keywords[1:3]]
        
        # Get content summary
        content_summary = article.get('content', '')[:200] + '...' if len(article.get('content', '')) > 200 else article.get('content', '')
        
        # Meta description variations
        meta_variations = [
            f"Learn {primary_keyword} with our comprehensive guide. {content_summary[:100]}",
            f"Discover the best {primary_keyword} strategies and tips. {content_summary[:100]}",
            f"Master {primary_keyword} with expert insights and practical advice. {content_summary[:100]}",
            f"Everything you need to know about {primary_keyword}. {content_summary[:100]}",
            f"Complete {primary_keyword} guide with step-by-step instructions. {content_summary[:100]}"
        ]
        
        for variation in meta_variations:
            if 120 <= len(variation) <= 160:
                optimization['optimized_meta'].append(variation)
    
    # Check for call-to-action
    cta_words = ['learn', 'discover', 'find out', 'get started', 'explore', 'read more']
    has_cta = any(word in current_meta.lower() for word in cta_words)
    if not has_cta:
        optimization['recommendations'].append('Add a call-to-action to encourage clicks')
    
    # Check for keyword inclusion
    if keywords:
        has_primary_keyword = primary_keyword.lower() in current_meta.lower()
        if not has_primary_keyword:
            optimization['recommendations'].append('Include primary keyword in meta description')
    
    # Calculate SEO score
    seo_factors = {
        'length_ok': 120 <= len(current_meta) <= 160,
        'has_keywords': any(kw['keyword'].lower() in current_meta.lower() for kw in keywords) if keywords else False,
        'has_cta': has_cta,
        'unique_content': current_meta != article.get('title', ''),
        'compelling': any(word in current_meta.lower() for word in ['best', 'ultimate', 'complete', 'guide', 'tips', 'strategies'])
    }
    
    optimization['seo_score'] = sum(seo_factors.values()) / len(seo_factors) * 100
    
    return optimization

def optimize_headings(article: Dict[str, Any], keywords: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimizes heading structure and content for SEO.
    
    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for optimization
        
    Returns:
        Dict[str, Any]: Optimized headings and recommendations
    """
    optimization = {
        'current_headings': [],
        'optimized_headings': [],
        'recommendations': [],
        'seo_score': 0,
        'heading_structure': {}
    }
    
    content = article.get('content', '')
    
    # Extract current headings
    h1_pattern = r'^# (.+)$'
    h2_pattern = r'^## (.+)$'
    h3_pattern = r'^### (.+)$'
    
    h1_headings = re.findall(h1_pattern, content, re.MULTILINE)
    h2_headings = re.findall(h2_pattern, content, re.MULTILINE)
    h3_headings = re.findall(h3_pattern, content, re.MULTILINE)
    
    optimization['current_headings'] = {
        'h1': h1_headings,
        'h2': h2_headings,
        'h3': h3_headings
    }
    
    optimization['heading_structure'] = {
        'h1_count': len(h1_headings),
        'h2_count': len(h2_headings),
        'h3_count': len(h3_headings),
        'total_headings': len(h1_headings) + len(h2_headings) + len(h3_headings)
    }
    
    # Check heading structure
    if len(h1_headings) == 0:
        optimization['recommendations'].append('Add an H1 heading for better SEO structure')
    elif len(h1_headings) > 1:
        optimization['recommendations'].append('Use only one H1 heading per page')
    
    if len(h2_headings) < 3:
        optimization['recommendations'].append('Add more H2 headings to improve content structure')
    
    # Optimize headings with keywords
    if keywords and len(keywords) > 0:
        primary_keyword = keywords[0]['keyword']
        secondary_keywords = [kw['keyword'] for kw in keywords[1:4]]
        
        # Generate optimized H2 headings
        optimized_h2 = []
        for i, h2 in enumerate(h2_headings):
            if primary_keyword.lower() not in h2.lower():
                optimized_h2.append(f"{h2} - {primary_keyword.title()}")
            else:
                optimized_h2.append(h2)
        
        # Generate optimized H3 headings
        optimized_h3 = []
        for i, h3 in enumerate(h3_headings):
            if i < len(secondary_keywords) and secondary_keywords[i].lower() not in h3.lower():
                optimized_h3.append(f"{h3} - {secondary_keywords[i].title()}")
            else:
                optimized_h3.append(h3)
        
        optimization['optimized_headings'] = {
            'h1': h1_headings,
            'h2': optimized_h2,
            'h3': optimized_h3
        }
    
    # Check heading length
    for heading_list in [h1_headings, h2_headings, h3_headings]:
        for heading in heading_list:
            if len(heading) > 60:
                optimization['recommendations'].append(f'Heading too long: "{heading[:50]}..." (aim for 60 characters or less)')
    
    # Calculate SEO score
    seo_factors = {
        'has_h1': len(h1_headings) == 1,
        'has_h2': len(h2_headings) >= 3,
        'has_h3': len(h3_headings) > 0,
        'keyword_in_headings': any(kw['keyword'].lower() in ' '.join(h2_headings + h3_headings).lower() for kw in keywords) if keywords else False,
        'proper_hierarchy': len(h1_headings) <= 1 and len(h2_headings) >= len(h3_headings)
    }
    
    optimization['seo_score'] = sum(seo_factors.values()) / len(seo_factors) * 100
    
    return optimization

def optimize_content_structure(article: Dict[str, Any], keywords: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimizes overall content structure for SEO.
    
    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for optimization
        
    Returns:
        Dict[str, Any]: Content structure optimization results
    """
    optimization = {
        'word_count': 0,
        'paragraph_count': 0,
        'sentence_count': 0,
        'readability_score': 0,
        'keyword_density': {},
        'recommendations': [],
        'seo_score': 0
    }
    
    content = article.get('content', '')
    words = content.split()
    optimization['word_count'] = len(words)
    
    # Count paragraphs and sentences
    paragraphs = content.split('\n\n')
    optimization['paragraph_count'] = len(paragraphs)
    
    sentences = re.split(r'[.!?]+', content)
    optimization['sentence_count'] = len([s for s in sentences if s.strip()])
    
    # Calculate readability score (simplified)
    avg_sentence_length = optimization['word_count'] / optimization['sentence_count'] if optimization['sentence_count'] > 0 else 0
    optimization['readability_score'] = max(0, 100 - (avg_sentence_length * 1.5))
    
    # Analyze keyword density
    if keywords:
        content_lower = content.lower()
        for keyword_data in keywords:
            keyword = keyword_data['keyword'].lower()
            frequency = content_lower.count(keyword)
            density = (frequency / optimization['word_count']) * 100 if optimization['word_count'] > 0 else 0
            
            optimization['keyword_density'][keyword] = {
                'frequency': frequency,
                'density': density,
                'status': 'optimal' if 1 <= density <= 3 else 'needs_optimization'
            }
    
    # Generate recommendations
    if optimization['word_count'] < 1000:
        optimization['recommendations'].append('Content is too short (aim for 1000+ words)')
    elif optimization['word_count'] > 3000:
        optimization['recommendations'].append('Content may be too long (consider breaking into series)')
    
    if optimization['paragraph_count'] < 5:
        optimization['recommendations'].append('Add more paragraphs for better structure')
    
    if optimization['readability_score'] < 60:
        optimization['recommendations'].append('Improve readability with shorter sentences')
    
    # Check for keyword optimization
    if keywords:
        for keyword, data in optimization['keyword_density'].items():
            if data['density'] < 1:
                optimization['recommendations'].append(f'Increase "{keyword}" keyword density')
            elif data['density'] > 3:
                optimization['recommendations'].append(f'Reduce "{keyword}" keyword density')
    
    # Calculate SEO score
    seo_factors = {
        'word_count_ok': 1000 <= optimization['word_count'] <= 3000,
        'paragraph_count_ok': optimization['paragraph_count'] >= 5,
        'readability_ok': optimization['readability_score'] >= 60,
        'keyword_density_ok': all(data['status'] == 'optimal' for data in optimization['keyword_density'].values()) if optimization['keyword_density'] else True
    }
    
    optimization['seo_score'] = sum(seo_factors.values()) / len(seo_factors) * 100
    
    return optimization

def add_internal_links(article: Dict[str, Any], internal_pages: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Adds strategic internal links to improve SEO and user experience.
    
    Args:
        article: Article dictionary with content
        internal_pages: List of internal pages for linking
        
    Returns:
        Dict[str, Any]: Article with internal links added
    """
    enhanced_article = article.copy()
    
    if not internal_pages:
        internal_pages = [
            {'url': '/blog', 'title': 'Blog', 'keywords': ['blog', 'articles', 'content']},
            {'url': '/resources', 'title': 'Resources', 'keywords': ['resources', 'guides', 'tools']},
            {'url': '/about', 'title': 'About Us', 'keywords': ['about', 'company', 'team']},
            {'url': '/contact', 'title': 'Contact', 'keywords': ['contact', 'get in touch', 'reach out']}
        ]
    
    enhanced_article['internal_links'] = []
    content = article.get('content', '')
    
    # Find opportunities for internal links
    for page in internal_pages:
        for keyword in page['keywords']:
            if keyword.lower() in content.lower():
                # Find the first occurrence and add link
                pattern = rf'\b{re.escape(keyword)}\b'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    link_text = f"[{keyword}]({page['url']})"
                    enhanced_article['internal_links'].append({
                        'keyword': keyword,
                        'url': page['url'],
                        'title': page['title'],
                        'position': match.start(),
                        'link_text': link_text
                    })
                    break
    
    # Add contextual internal links
    contextual_links = [
        {'keyword': 'learn more', 'url': '/learn', 'title': 'Learning Center'},
        {'keyword': 'get started', 'url': '/getting-started', 'title': 'Getting Started'},
        {'keyword': 'best practices', 'url': '/best-practices', 'title': 'Best Practices'},
        {'keyword': 'case study', 'url': '/case-studies', 'title': 'Case Studies'}
    ]
    
    for link in contextual_links:
        if link['keyword'].lower() in content.lower():
            enhanced_article['internal_links'].append({
                'keyword': link['keyword'],
                'url': link['url'],
                'title': link['title'],
                'type': 'contextual'
            })
    
    return enhanced_article

def analyze_seo_performance(article: Dict[str, Any], keywords: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes overall SEO performance and provides comprehensive recommendations.
    
    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for analysis
        
    Returns:
        Dict[str, Any]: Comprehensive SEO performance analysis
    """
    analysis = {
        'overall_score': 0,
        'title_optimization': {},
        'meta_optimization': {},
        'heading_optimization': {},
        'content_optimization': {},
        'technical_seo': {},
        'recommendations': [],
        'priority_actions': []
    }
    
    # Analyze title
    title_analysis = optimize_title_tags(article, keywords)
    analysis['title_optimization'] = title_analysis
    
    # Analyze meta description
    meta_analysis = optimize_meta_descriptions(article, keywords)
    analysis['meta_optimization'] = meta_analysis
    
    # Analyze headings
    heading_analysis = optimize_headings(article, keywords)
    analysis['heading_optimization'] = heading_analysis
    
    # Analyze content structure
    content_analysis = optimize_content_structure(article, keywords)
    analysis['content_optimization'] = content_analysis
    
    # Technical SEO analysis
    technical_analysis = analyze_technical_seo(article)
    analysis['technical_seo'] = technical_analysis
    
    # Calculate overall score
    scores = [
        title_analysis['seo_score'],
        meta_analysis['seo_score'],
        heading_analysis['seo_score'],
        content_analysis['seo_score'],
        technical_analysis['seo_score']
    ]
    analysis['overall_score'] = sum(scores) / len(scores)
    
    # Compile recommendations
    all_recommendations = (
        title_analysis['recommendations'] +
        meta_analysis['recommendations'] +
        heading_analysis['recommendations'] +
        content_analysis['recommendations'] +
        technical_analysis['recommendations']
    )
    analysis['recommendations'] = list(set(all_recommendations))  # Remove duplicates
    
    # Identify priority actions
    if analysis['overall_score'] < 70:
        analysis['priority_actions'] = [
            'Fix critical SEO issues first',
            'Optimize title and meta description',
            'Improve content structure',
            'Add missing keywords'
        ]
    elif analysis['overall_score'] < 85:
        analysis['priority_actions'] = [
            'Fine-tune keyword optimization',
            'Improve content readability',
            'Add more internal links',
            'Enhance heading structure'
        ]
    else:
        analysis['priority_actions'] = [
            'Maintain current optimization',
            'Monitor performance metrics',
            'A/B test different approaches',
            'Focus on content quality'
        ]
    
    return analysis

def analyze_technical_seo(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes technical SEO aspects of the content.
    
    Args:
        article: Article dictionary with content
        
    Returns:
        Dict[str, Any]: Technical SEO analysis results
    """
    technical = {
        'seo_score': 0,
        'recommendations': [],
        'checks': {}
    }
    
    content = article.get('content', '')
    title = article.get('title', '')
    meta_description = article.get('meta_description', '')
    
    # Technical SEO checks
    checks = {
        'has_title': bool(title),
        'has_meta_description': bool(meta_description),
        'title_length_ok': 30 <= len(title) <= 60,
        'meta_length_ok': 120 <= len(meta_description) <= 160,
        'has_h1': '#' in content,
        'has_h2': '##' in content,
        'word_count_ok': 1000 <= len(content.split()) <= 3000,
        'has_images': '![' in content,
        'has_links': '](' in content,
        'has_lists': any(marker in content for marker in ['- ', '* ', '1. ', '2. '])
    }
    
    technical['checks'] = checks
    technical['seo_score'] = sum(checks.values()) / len(checks) * 100
    
    # Generate recommendations based on failed checks
    if not checks['has_title']:
        technical['recommendations'].append('Add a title tag')
    if not checks['has_meta_description']:
        technical['recommendations'].append('Add a meta description')
    if not checks['title_length_ok']:
        technical['recommendations'].append('Optimize title length (30-60 characters)')
    if not checks['meta_length_ok']:
        technical['recommendations'].append('Optimize meta description length (120-160 characters)')
    if not checks['has_h1']:
        technical['recommendations'].append('Add H1 heading')
    if not checks['has_h2']:
        technical['recommendations'].append('Add H2 headings')
    if not checks['word_count_ok']:
        technical['recommendations'].append('Optimize content length (1000-3000 words)')
    if not checks['has_images']:
        technical['recommendations'].append('Add relevant images')
    if not checks['has_links']:
        technical['recommendations'].append('Add internal and external links')
    if not checks['has_lists']:
        technical['recommendations'].append('Use lists for better readability')
    
    return technical
