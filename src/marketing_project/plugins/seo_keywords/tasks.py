"""
SEO Keywords processing plugin tasks for Marketing Project.

This module provides functions to extract, analyze, and optimize SEO keywords
from content for better search engine visibility and content strategy.

Functions:
    extract_primary_keywords: Extracts main SEO keywords from content
    extract_secondary_keywords: Extracts supporting keywords and LSI terms
    analyze_keyword_density: Analyzes keyword density and distribution
    generate_keyword_suggestions: Generates additional keyword suggestions
    optimize_keyword_placement: Optimizes keyword placement in content
    calculate_keyword_scores: Calculates keyword relevance and difficulty scores
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Union
from collections import Counter
from marketing_project.core.models import ContentContext, AppContext
from marketing_project.core.utils import (
    ensure_content_context, create_standard_task_result,
    validate_content_for_processing, extract_content_metadata_for_pipeline
)

logger = logging.getLogger("marketing_project.plugins.seo_keywords")

def extract_primary_keywords(content: Union[ContentContext, Dict[str, Any]], max_keywords: int = 5) -> Dict[str, Any]:
    """
    Extracts primary SEO keywords from content based on frequency and relevance.
    
    Args:
        content: Content context object or dictionary
        max_keywords: Maximum number of primary keywords to extract
        
    Returns:
        Dict[str, Any]: Standardized task result with primary keywords
    """
    try:
        # Ensure content is a ContentContext object
        content_obj = ensure_content_context(content)
        
        # Validate content
        validation = validate_content_for_processing(content_obj)
        if not validation['is_valid']:
            return create_standard_task_result(
                success=False,
                error=f"Content validation failed: {', '.join(validation['issues'])}",
                task_name='extract_primary_keywords'
            )
        
        text = f"{content_obj.title} {content_obj.content}".lower()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Calculate keyword scores based on frequency and position
        keywords = []
        for word, count in word_counts.most_common(max_keywords * 2):
            # Calculate position score (words in title get higher score)
            title_words = content_obj.title.lower().split() if content_obj.title else []
            position_score = 2.0 if word in title_words else 1.0
            
            # Calculate final score
            score = count * position_score
            
            keywords.append({
                'keyword': word,
                'frequency': count,
                'score': score,
                'in_title': word in title_words,
                'density': count / len(filtered_words) * 100
            })
        
        # Sort by score and return top keywords
        keywords.sort(key=lambda x: x['score'], reverse=True)
        result_keywords = keywords[:max_keywords]
        
        return create_standard_task_result(
            success=True,
            data={
                'primary_keywords': result_keywords,
                'total_keywords_found': len(keywords),
                'filtered_words_count': len(filtered_words)
            },
            task_name='extract_primary_keywords',
            metadata=extract_content_metadata_for_pipeline(content_obj)
        )
        
    except Exception as e:
        logger.error(f"Error in extract_primary_keywords: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Keyword extraction failed: {str(e)}",
            task_name='extract_primary_keywords'
        )

def extract_secondary_keywords(content: Union[ContentContext, Dict[str, Any]], primary_keywords: List[str], max_keywords: int = 10) -> Dict[str, Any]:
    """
    Extracts secondary keywords and LSI (Latent Semantic Indexing) terms.
    
    Args:
        content: Content context object or dictionary
        primary_keywords: List of primary keywords to find related terms for
        max_keywords: Maximum number of secondary keywords to extract
        
    Returns:
        Dict[str, Any]: Standardized task result with secondary keywords
    """
    try:
        # Ensure content is a ContentContext object
        content_obj = ensure_content_context(content)
        
        # Validate content
        validation = validate_content_for_processing(content_obj)
        if not validation['is_valid']:
            return create_standard_task_result(
                success=False,
                error=f"Content validation failed: {', '.join(validation['issues'])}",
                task_name='extract_secondary_keywords'
            )
        
        text = content_obj.content.lower()
        
        # Find 2-3 word phrases that contain primary keywords
        secondary_keywords = []
        
        for primary in primary_keywords:
            # Find phrases containing the primary keyword
            pattern = rf'\b\w*\s*{re.escape(primary)}\s*\w*\b'
            phrases = re.findall(pattern, text)
            
            for phrase in phrases:
                if len(phrase.split()) <= 3 and phrase != primary:
                    secondary_keywords.append({
                        'keyword': phrase.strip(),
                        'related_to': primary,
                        'type': 'phrase',
                        'frequency': text.count(phrase)
                    })
        
        # Find synonyms and related terms (simplified approach)
        synonym_patterns = {
            'best': ['top', 'greatest', 'excellent', 'superior'],
            'guide': ['tutorial', 'how-to', 'instructions', 'manual'],
            'review': ['analysis', 'evaluation', 'assessment', 'critique'],
            'tips': ['advice', 'recommendations', 'suggestions', 'hints'],
            'learn': ['understand', 'discover', 'explore', 'study']
        }
        
        for word in text.split():
            if word in synonym_patterns:
                for synonym in synonym_patterns[word]:
                    if synonym in text:
                        secondary_keywords.append({
                            'keyword': synonym,
                            'related_to': word,
                            'type': 'synonym',
                            'frequency': text.count(synonym)
                        })
        
        # Remove duplicates and sort by frequency
        seen = set()
        unique_keywords = []
        for kw in secondary_keywords:
            if kw['keyword'] not in seen:
                seen.add(kw['keyword'])
                unique_keywords.append(kw)
        
        unique_keywords.sort(key=lambda x: x['frequency'], reverse=True)
        result_keywords = unique_keywords[:max_keywords]
        
        return create_standard_task_result(
            success=True,
            data={
                'secondary_keywords': result_keywords,
                'total_secondary_found': len(unique_keywords),
                'primary_keywords_used': primary_keywords
            },
            task_name='extract_secondary_keywords',
            metadata=extract_content_metadata_for_pipeline(content_obj)
        )
        
    except Exception as e:
        logger.error(f"Error in extract_secondary_keywords: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Secondary keyword extraction failed: {str(e)}",
            task_name='extract_secondary_keywords'
        )

def analyze_keyword_density(content: Union[ContentContext, Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
    """
    Analyzes keyword density and distribution in content.
    
    Args:
        content: Content context object or dictionary
        keywords: List of keywords to analyze
        
    Returns:
        Dict[str, Any]: Standardized task result with density analysis
    """
    try:
        # Ensure content is a ContentContext object
        content_obj = ensure_content_context(content)
        
        # Validate content
        validation = validate_content_for_processing(content_obj)
        if not validation['is_valid']:
            return create_standard_task_result(
                success=False,
                error=f"Content validation failed: {', '.join(validation['issues'])}",
                task_name='analyze_keyword_density'
            )
        
        text = content_obj.content.lower()
        word_count = len(text.split())
        
        density_analysis = {
            'total_words': word_count,
            'keyword_densities': {},
            'keyword_positions': {},
            'recommendations': []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            frequency = text.count(keyword_lower)
            density = (frequency / word_count) * 100 if word_count > 0 else 0
            
            density_analysis['keyword_densities'][keyword] = {
                'frequency': frequency,
                'density': density,
                'status': 'optimal' if 1 <= density <= 3 else 'needs_optimization'
            }
            
            # Find keyword positions
            positions = []
            start = 0
            while True:
                pos = text.find(keyword_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            density_analysis['keyword_positions'][keyword] = positions
            
            # Generate recommendations
            if density < 1:
                density_analysis['recommendations'].append(f"Increase '{keyword}' density (currently {density:.2f}%)")
            elif density > 3:
                density_analysis['recommendations'].append(f"Reduce '{keyword}' density (currently {density:.2f}%)")
        
        return create_standard_task_result(
            success=True,
            data=density_analysis,
            task_name='analyze_keyword_density',
            metadata=extract_content_metadata_for_pipeline(content_obj)
        )
        
    except Exception as e:
        logger.error(f"Error in analyze_keyword_density: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Keyword density analysis failed: {str(e)}",
            task_name='analyze_keyword_density'
        )

def generate_keyword_suggestions(content: Union[ContentContext, Dict[str, Any]], industry: str = None, target_audience: str = None) -> Dict[str, Any]:
    """
    Generates additional keyword suggestions based on content analysis.
    
    Args:
        content: Content context object or dictionary
        industry: Industry context for keyword suggestions
        target_audience: Target audience for keyword suggestions
        
    Returns:
        Dict[str, Any]: Standardized task result with keyword suggestions
    """
    try:
        # Ensure content is a ContentContext object
        content_obj = ensure_content_context(content)
        
        # Validate content
        validation = validate_content_for_processing(content_obj)
        if not validation['is_valid']:
            return create_standard_task_result(
                success=False,
                error=f"Content validation failed: {', '.join(validation['issues'])}",
                task_name='generate_keyword_suggestions'
            )
        
        suggestions = []
        
        # Extract key topics from content
        text = content_obj.content.lower()
        title = content_obj.title.lower() if content_obj.title else ""
        
        # Industry-specific keyword suggestions
        industry_keywords = {
            'technology': ['innovation', 'digital', 'automation', 'software', 'platform'],
            'marketing': ['strategy', 'campaign', 'brand', 'engagement', 'conversion'],
            'finance': ['investment', 'portfolio', 'revenue', 'profit', 'growth'],
            'healthcare': ['treatment', 'patient', 'medical', 'health', 'wellness'],
            'education': ['learning', 'training', 'course', 'skill', 'knowledge']
        }
        
        if industry and industry.lower() in industry_keywords:
            for keyword in industry_keywords[industry.lower()]:
                if keyword not in text:
                    suggestions.append({
                        'keyword': keyword,
                        'type': 'industry',
                        'relevance_score': 0.8,
                        'suggestion_reason': f'Industry-specific keyword for {industry}'
                    })
        
        # Audience-specific keyword suggestions
        audience_keywords = {
            'beginners': ['introduction', 'basics', 'getting started', 'tutorial', 'guide'],
            'professionals': ['advanced', 'expert', 'enterprise', 'optimization', 'strategy'],
            'developers': ['code', 'implementation', 'technical', 'api', 'integration'],
            'managers': ['management', 'leadership', 'strategy', 'planning', 'decision']
        }
        
        if target_audience and target_audience.lower() in audience_keywords:
            for keyword in audience_keywords[target_audience.lower()]:
                if keyword not in text:
                    suggestions.append({
                        'keyword': keyword,
                        'type': 'audience',
                        'relevance_score': 0.7,
                        'suggestion_reason': f'Audience-specific keyword for {target_audience}'
                    })
        
        # Long-tail keyword suggestions based on content
        words = text.split()
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        # Find common phrases that could be keywords
        phrase_counts = Counter(bigrams + trigrams)
        for phrase, count in phrase_counts.most_common(5):
            if count > 1 and len(phrase.split()) >= 2:
                suggestions.append({
                    'keyword': phrase,
                    'type': 'long_tail',
                    'relevance_score': min(count / 10, 1.0),
                    'suggestion_reason': 'Frequently used phrase in content'
                })
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        result_suggestions = suggestions[:10]
        
        return create_standard_task_result(
            success=True,
            data={
                'suggestions': result_suggestions,
                'total_suggestions': len(suggestions),
                'industry': industry,
                'target_audience': target_audience
            },
            task_name='generate_keyword_suggestions',
            metadata=extract_content_metadata_for_pipeline(content_obj)
        )
        
    except Exception as e:
        logger.error(f"Error in generate_keyword_suggestions: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Keyword suggestion generation failed: {str(e)}",
            task_name='generate_keyword_suggestions'
        )

def optimize_keyword_placement(content: Union[ContentContext, Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
    """
    Provides recommendations for optimizing keyword placement in content.
    
    Args:
        content: Content context object or dictionary
        keywords: List of keywords to optimize placement for
        
    Returns:
        Dict[str, Any]: Standardized task result with placement optimization
    """
    try:
        # Ensure content is a ContentContext object
        content_obj = ensure_content_context(content)
        
        # Validate content
        validation = validate_content_for_processing(content_obj)
        if not validation['is_valid']:
            return create_standard_task_result(
                success=False,
                error=f"Content validation failed: {', '.join(validation['issues'])}",
                task_name='optimize_keyword_placement'
            )
        
        text = content_obj.content
        title = content_obj.title or ""
        
        optimization = {
            'title_optimization': {},
            'heading_optimization': {},
            'content_optimization': {},
            'meta_optimization': {},
            'recommendations': []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Title optimization
            title_contains = keyword_lower in title.lower()
            optimization['title_optimization'][keyword] = {
                'in_title': title_contains,
                'recommendation': 'Add to title' if not title_contains else 'Already in title'
            }
            
            # Heading optimization (simplified - would need proper heading detection)
            headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
            heading_contains = any(keyword_lower in heading.lower() for heading in headings)
            optimization['heading_optimization'][keyword] = {
                'in_headings': heading_contains,
                'recommendation': 'Add to headings' if not heading_contains else 'Already in headings'
            }
            
            # Content optimization
            first_paragraph = text.split('\n')[0] if text else ""
            first_100_words = ' '.join(text.split()[:100])
            
            optimization['content_optimization'][keyword] = {
                'in_first_paragraph': keyword_lower in first_paragraph.lower(),
                'in_first_100_words': keyword_lower in first_100_words.lower(),
                'recommendation': 'Add to first paragraph' if keyword_lower not in first_100_words.lower() else 'Good placement'
            }
            
            # Generate overall recommendations
            if not title_contains:
                optimization['recommendations'].append(f"Consider adding '{keyword}' to the title")
            if not heading_contains:
                optimization['recommendations'].append(f"Consider adding '{keyword}' to a heading")
            if keyword_lower not in first_100_words.lower():
                optimization['recommendations'].append(f"Consider adding '{keyword}' to the first paragraph")
        
        return create_standard_task_result(
            success=True,
            data=optimization,
            task_name='optimize_keyword_placement',
            metadata=extract_content_metadata_for_pipeline(content_obj)
        )
        
    except Exception as e:
        logger.error(f"Error in optimize_keyword_placement: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Keyword placement optimization failed: {str(e)}",
            task_name='optimize_keyword_placement'
        )

def calculate_keyword_scores(keywords: List[Dict[str, Any]], content: Union[ContentContext, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates comprehensive keyword scores including relevance and difficulty.
    
    Args:
        keywords: List of keyword dictionaries
        content: Content context object or dictionary
        
    Returns:
        Dict[str, Any]: Standardized task result with scored keywords
    """
    try:
        # Ensure content is a ContentContext object
        content_obj = ensure_content_context(content)
        
        # Validate content
        validation = validate_content_for_processing(content_obj)
        if not validation['is_valid']:
            return create_standard_task_result(
                success=False,
                error=f"Content validation failed: {', '.join(validation['issues'])}",
                task_name='calculate_keyword_scores'
            )
        
        scored_keywords = []
        
        for keyword_data in keywords:
            keyword = keyword_data['keyword']
            
            # Calculate relevance score (0-1)
            frequency = keyword_data.get('frequency', 0)
            in_title = keyword_data.get('in_title', False)
            density = keyword_data.get('density', 0)
            
            relevance_score = min(frequency / 10, 1.0)  # Normalize frequency
            if in_title:
                relevance_score += 0.2
            if 1 <= density <= 3:
                relevance_score += 0.1
            
            # Calculate difficulty score (0-1, where 1 is most difficult)
            word_length = len(keyword.split())
            difficulty_score = min(word_length / 5, 1.0)  # Longer phrases are harder
            
            # Calculate overall score
            overall_score = (relevance_score * 0.7) + ((1 - difficulty_score) * 0.3)
            
            scored_keyword = keyword_data.copy()
            scored_keyword.update({
                'relevance_score': relevance_score,
                'difficulty_score': difficulty_score,
                'overall_score': overall_score,
                'priority': 'high' if overall_score > 0.7 else 'medium' if overall_score > 0.4 else 'low'
            })
            
            scored_keywords.append(scored_keyword)
        
        # Sort by overall score
        scored_keywords.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return create_standard_task_result(
            success=True,
            data={
                'scored_keywords': scored_keywords,
                'high_priority_count': sum(1 for kw in scored_keywords if kw['priority'] == 'high'),
                'medium_priority_count': sum(1 for kw in scored_keywords if kw['priority'] == 'medium'),
                'low_priority_count': sum(1 for kw in scored_keywords if kw['priority'] == 'low')
            },
            task_name='calculate_keyword_scores',
            metadata=extract_content_metadata_for_pipeline(content_obj)
        )
        
    except Exception as e:
        logger.error(f"Error in calculate_keyword_scores: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Keyword scoring failed: {str(e)}",
            task_name='calculate_keyword_scores'
        )