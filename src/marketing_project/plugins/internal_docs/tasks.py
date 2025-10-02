"""
Internal Documents processing plugin tasks for Marketing Project.

This module provides functions to suggest internal documents
and cross-references to enhance content and improve internal linking.

Functions:
    analyze_content_gaps: Analyzes content for missing information
    suggest_related_docs: Suggests related internal documents
    identify_cross_references: Identifies opportunities for cross-references
    generate_doc_suggestions: Generates specific document suggestions
    create_content_relationships: Creates relationships between content pieces
    optimize_internal_linking: Optimizes internal linking strategy
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

logger = logging.getLogger("marketing_project.plugins.internal_docs")

def analyze_content_gaps(article: Union[Dict[str, Any], ContentContext], existing_docs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes content for gaps that could be filled with internal documents.
    
    Args:
        article: Article dictionary with content or ContentContext
        existing_docs: List of existing internal documents
        
    Returns:
        Dict[str, Any]: Standardized task result with content gap analysis
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
        
        gap_analysis = {
            'content_gaps': [],
            'missing_topics': [],
            'unexplained_concepts': [],
            'suggested_docs': [],
            'priority_level': 'medium'
        }
        
        content = article_data.get('content', '')
        title = article_data.get('title', '')
        
        # Identify technical terms that might need explanation
        technical_terms = [
            'API', 'SDK', 'framework', 'architecture', 'algorithm', 'database',
            'authentication', 'authorization', 'encryption', 'scalability',
            'performance', 'optimization', 'integration', 'deployment'
        ]
        
        unexplained_concepts = []
        for term in technical_terms:
            if term.lower() in content.lower() and not is_term_explained(content, term):
                unexplained_concepts.append(term)
        
        gap_analysis['unexplained_concepts'] = unexplained_concepts
        
        # Identify topics that could benefit from deeper coverage
        topic_indicators = [
            'for more information', 'see also', 'related to', 'similar to',
            'in addition', 'furthermore', 'additionally', 'moreover'
        ]
        
        missing_topics = []
        for indicator in topic_indicators:
            if indicator in content.lower():
                # Extract the topic that needs more information
                pattern = rf'{re.escape(indicator)}[^.]*\.'
                matches = re.findall(pattern, content, re.IGNORECASE)
                missing_topics.extend(matches)
        
        gap_analysis['missing_topics'] = missing_topics
        
        # Identify content gaps based on article structure
        content_gaps = []
        
        # Check for missing sections that are common in comprehensive articles
        expected_sections = [
            'introduction', 'overview', 'getting started', 'prerequisites',
            'implementation', 'examples', 'best practices', 'troubleshooting',
            'conclusion', 'next steps', 'resources'
        ]
        
        content_lower = content.lower()
        for section in expected_sections:
            if section not in content_lower:
                content_gaps.append(f"Missing {section} section")
        
        gap_analysis['content_gaps'] = content_gaps
        
        # Generate document suggestions based on gaps
        doc_suggestions = []
        
        if unexplained_concepts:
            doc_suggestions.append({
                'type': 'glossary',
                'title': f"{title} - Technical Glossary",
                'description': f"Definitions and explanations for technical terms: {', '.join(unexplained_concepts[:5])}",
                'priority': 'high',
                'target_audience': 'beginners'
            })
        
        if 'troubleshooting' in content_gaps:
            doc_suggestions.append({
                'type': 'troubleshooting',
                'title': f"{title} - Troubleshooting Guide",
                'description': "Common issues and solutions related to the main topic",
                'priority': 'medium',
                'target_audience': 'all'
            })
        
        if 'examples' in content_gaps:
            doc_suggestions.append({
                'type': 'examples',
                'title': f"{title} - Code Examples",
                'description': "Practical examples and code snippets",
                'priority': 'high',
                'target_audience': 'developers'
            })
        
        gap_analysis['suggested_docs'] = doc_suggestions
        
        # Determine priority level
        if len(unexplained_concepts) > 3 or len(content_gaps) > 5:
            gap_analysis['priority_level'] = 'high'
        elif len(unexplained_concepts) > 1 or len(content_gaps) > 2:
            gap_analysis['priority_level'] = 'medium'
        else:
            gap_analysis['priority_level'] = 'low'
        
        return create_standard_task_result(
            success=True,
            data=gap_analysis,
            task_name='analyze_content_gaps',
            metadata={
                'content_gaps_count': len(gap_analysis['content_gaps']),
                'unexplained_concepts_count': len(gap_analysis['unexplained_concepts']),
                'suggested_docs_count': len(gap_analysis['suggested_docs']),
                'priority_level': gap_analysis['priority_level']
            }
        )
        
    except Exception as e:
        logger.error(f"Error in analyze_content_gaps: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Content gap analysis failed: {str(e)}",
            task_name='analyze_content_gaps'
        )

def suggest_related_docs(article: Dict[str, Any], doc_database: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Suggests related internal documents based on content analysis.
    
    Args:
        article: Article dictionary with content
        doc_database: Database of existing internal documents
        
    Returns:
        Dict[str, Any]: Related document suggestions
    """
    suggestions = {
        'related_docs': [],
        'prerequisite_docs': [],
        'follow_up_docs': [],
        'complementary_docs': [],
        'cross_references': []
    }
    
    if not doc_database:
        # Default document database structure
        doc_database = [
            {
                'id': 'getting-started',
                'title': 'Getting Started Guide',
                'keywords': ['getting started', 'beginner', 'introduction', 'setup'],
                'type': 'guide',
                'audience': 'beginners'
            },
            {
                'id': 'best-practices',
                'title': 'Best Practices',
                'keywords': ['best practices', 'recommendations', 'guidelines', 'standards'],
                'type': 'guide',
                'audience': 'intermediate'
            },
            {
                'id': 'troubleshooting',
                'title': 'Troubleshooting Guide',
                'keywords': ['troubleshooting', 'issues', 'problems', 'solutions', 'debug'],
                'type': 'reference',
                'audience': 'all'
            },
            {
                'id': 'api-reference',
                'title': 'API Reference',
                'keywords': ['api', 'reference', 'endpoints', 'methods', 'parameters'],
                'type': 'reference',
                'audience': 'developers'
            },
            {
                'id': 'case-studies',
                'title': 'Case Studies',
                'keywords': ['case study', 'example', 'use case', 'implementation', 'success'],
                'type': 'example',
                'audience': 'all'
            }
        ]
    
    content = article.get('content', '').lower()
    title = article.get('title', '').lower()
    
    # Find related documents based on keyword matching
    for doc in doc_database:
        relevance_score = 0
        matched_keywords = []
        
        for keyword in doc['keywords']:
            if keyword.lower() in content or keyword.lower() in title:
                relevance_score += 1
                matched_keywords.append(keyword)
        
        if relevance_score > 0:
            doc_suggestion = {
                'doc_id': doc['id'],
                'title': doc['title'],
                'type': doc['type'],
                'audience': doc['audience'],
                'relevance_score': relevance_score,
                'matched_keywords': matched_keywords,
                'suggestion_reason': f"Matches {len(matched_keywords)} keywords"
            }
            
            # Categorize suggestions
            if doc['type'] == 'guide' and 'getting started' in doc['title'].lower():
                suggestions['prerequisite_docs'].append(doc_suggestion)
            elif doc['type'] == 'reference':
                suggestions['complementary_docs'].append(doc_suggestion)
            elif doc['type'] == 'example':
                suggestions['follow_up_docs'].append(doc_suggestion)
            else:
                suggestions['related_docs'].append(doc_suggestion)
    
    # Sort by relevance score
    for category in ['related_docs', 'prerequisite_docs', 'follow_up_docs', 'complementary_docs']:
        suggestions[category].sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return suggestions

def identify_cross_references(article: Dict[str, Any], content_library: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Identifies opportunities for cross-references between content pieces.
    
    Args:
        article: Article dictionary with content
        content_library: Library of existing content for cross-referencing
        
    Returns:
        Dict[str, Any]: Cross-reference opportunities
    """
    cross_refs = {
        'internal_links': [],
        'topic_connections': [],
        'concept_relationships': [],
        'series_opportunities': [],
        'update_opportunities': []
    }
    
    if not content_library:
        # Default content library structure
        content_library = [
            {
                'id': 'content-1',
                'title': 'Introduction to Web Development',
                'topics': ['html', 'css', 'javascript', 'web development'],
                'type': 'tutorial',
                'status': 'published'
            },
            {
                'id': 'content-2',
                'title': 'Advanced JavaScript Techniques',
                'topics': ['javascript', 'advanced', 'performance', 'optimization'],
                'type': 'tutorial',
                'status': 'published'
            },
            {
                'id': 'content-3',
                'title': 'CSS Best Practices',
                'topics': ['css', 'best practices', 'styling', 'responsive'],
                'type': 'guide',
                'status': 'published'
            }
        ]
    
    content = article.get('content', '').lower()
    title = article.get('title', '').lower()
    
    # Find topic connections
    for content_item in content_library:
        topic_matches = []
        for topic in content_item['topics']:
            if topic.lower() in content or topic.lower() in title:
                topic_matches.append(topic)
        
        if topic_matches:
            cross_ref = {
                'content_id': content_item['id'],
                'title': content_item['title'],
                'type': content_item['type'],
                'matched_topics': topic_matches,
                'relevance_score': len(topic_matches),
                'link_text': f"See also: {content_item['title']}",
                'suggestion': f"Link to {content_item['title']} when discussing {', '.join(topic_matches[:2])}"
            }
            
            cross_refs['topic_connections'].append(cross_ref)
    
    # Identify concept relationships
    concept_relationships = [
        ('authentication', 'authorization'),
        ('frontend', 'backend'),
        ('database', 'api'),
        ('testing', 'deployment'),
        ('performance', 'optimization')
    ]
    
    for concept1, concept2 in concept_relationships:
        if concept1 in content and concept2 in content:
            cross_refs['concept_relationships'].append({
                'concepts': [concept1, concept2],
                'suggestion': f"Create a comprehensive guide covering both {concept1} and {concept2}",
                'priority': 'medium'
            })
    
    # Identify series opportunities
    series_keywords = ['part 1', 'part 2', 'introduction', 'advanced', 'beginner', 'intermediate']
    series_matches = [kw for kw in series_keywords if kw in title]
    
    if series_matches:
        cross_refs['series_opportunities'].append({
            'keywords': series_matches,
            'suggestion': f"Consider creating a series: {title} could be part of a larger series",
            'priority': 'high'
        })
    
    # Sort by relevance
    cross_refs['topic_connections'].sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return cross_refs

def generate_doc_suggestions(article: Dict[str, Any], gap_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generates specific document suggestions based on content analysis.
    
    Args:
        article: Article dictionary with content
        gap_analysis: Content gap analysis results
        
    Returns:
        Dict[str, Any]: Specific document suggestions
    """
    suggestions = {
        'immediate_docs': [],
        'future_docs': [],
        'update_suggestions': [],
        'content_expansions': [],
        'resource_creations': []
    }
    
    if not gap_analysis:
        gap_analysis = analyze_content_gaps(article)
    
    content = article.get('content', '')
    title = article.get('title', '')
    
    # Immediate document suggestions based on gaps
    if gap_analysis.get('unexplained_concepts'):
        suggestions['immediate_docs'].append({
            'type': 'glossary',
            'title': f"{title} - Technical Terms Glossary",
            'description': "Define and explain technical terms used in the main article",
            'priority': 'high',
            'estimated_effort': '2-3 hours',
            'target_audience': 'beginners',
            'content_outline': [
                'Introduction to technical terms',
                'Alphabetical list of terms with definitions',
                'Cross-references to related concepts',
                'Examples and use cases'
            ]
        })
    
    if gap_analysis.get('content_gaps'):
        for gap in gap_analysis['content_gaps']:
            if 'troubleshooting' in gap.lower():
                suggestions['immediate_docs'].append({
                    'type': 'troubleshooting',
                    'title': f"{title} - Common Issues and Solutions",
                    'description': "Troubleshooting guide for common problems",
                    'priority': 'high',
                    'estimated_effort': '4-6 hours',
                    'target_audience': 'all',
                    'content_outline': [
                        'Common error messages and solutions',
                        'Step-by-step troubleshooting process',
                        'Prevention tips',
                        'Getting additional help'
                    ]
                })
    
    # Future document suggestions
    content_lower = content.lower()
    
    if 'tutorial' in content_lower or 'guide' in content_lower:
        suggestions['future_docs'].append({
            'type': 'video',
            'title': f"{title} - Video Tutorial",
            'description': "Video version of the tutorial for visual learners",
            'priority': 'medium',
            'estimated_effort': '8-12 hours',
            'target_audience': 'visual learners'
        })
    
    if 'api' in content_lower or 'integration' in content_lower:
        suggestions['future_docs'].append({
            'type': 'code_examples',
            'title': f"{title} - Code Examples Repository",
            'description': "GitHub repository with working code examples",
            'priority': 'medium',
            'estimated_effort': '6-8 hours',
            'target_audience': 'developers'
        })
    
    # Update suggestions for existing content
    suggestions['update_suggestions'].append({
        'type': 'content_update',
        'title': f"Update {title} with latest information",
        'description': "Review and update content with current best practices",
        'priority': 'low',
        'estimated_effort': '2-4 hours',
        'frequency': 'quarterly'
    })
    
    # Content expansion suggestions
    if len(content.split()) < 2000:
        suggestions['content_expansions'].append({
            'type': 'content_expansion',
            'title': f"Expand {title} with additional sections",
            'description': "Add more detailed sections to make content more comprehensive",
            'priority': 'medium',
            'estimated_effort': '4-6 hours',
            'suggested_sections': [
                'More detailed examples',
                'Advanced use cases',
                'Performance considerations',
                'Security best practices'
            ]
        })
    
    # Resource creation suggestions
    suggestions['resource_creations'].append({
        'type': 'cheat_sheet',
        'title': f"{title} - Quick Reference Cheat Sheet",
        'description': "One-page reference for quick lookup",
        'priority': 'low',
        'estimated_effort': '2-3 hours',
        'target_audience': 'all'
    })
    
    return suggestions

def create_content_relationships(article: Dict[str, Any], content_library: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Creates relationships between content pieces for better organization.
    
    Args:
        article: Article dictionary with content
        content_library: Library of existing content
        
    Returns:
        Dict[str, Any]: Content relationship mapping
    """
    relationships = {
        'content_map': {},
        'learning_paths': [],
        'topic_clusters': [],
        'content_hierarchy': {},
        'cross_references': []
    }
    
    if not content_library:
        content_library = []
    
    content_id = article.get('id', 'current-article')
    title = article.get('title', '')
    content = article.get('content', '').lower()
    
    # Create content map
    relationships['content_map'] = {
        'id': content_id,
        'title': title,
        'type': 'article',
        'topics': extract_topics_from_content(content),
        'difficulty': assess_content_difficulty(content),
        'audience': determine_target_audience(content),
        'prerequisites': [],
        'follow_ups': [],
        'related_content': []
    }
    
    # Identify learning paths
    if 'beginner' in content or 'introduction' in content:
        relationships['learning_paths'].append({
            'path_name': f"{title} Learning Path",
            'level': 'beginner',
            'steps': [
                {'content_id': content_id, 'title': title, 'order': 1},
                {'content_id': 'intermediate-topic', 'title': 'Intermediate Topic', 'order': 2},
                {'content_id': 'advanced-topic', 'title': 'Advanced Topic', 'order': 3}
            ]
        })
    
    # Create topic clusters
    topics = extract_topics_from_content(content)
    for topic in topics:
        relationships['topic_clusters'].append({
            'topic': topic,
            'content_items': [content_id],
            'cluster_leader': content_id,
            'related_topics': [t for t in topics if t != topic]
        })
    
    # Create content hierarchy
    relationships['content_hierarchy'] = {
        'parent_content': None,
        'child_content': [],
        'sibling_content': [],
        'level': 1
    }
    
    return relationships

def optimize_internal_linking(article: Dict[str, Any], content_library: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimizes internal linking strategy for better SEO and user experience.
    
    Args:
        article: Article dictionary with content
        content_library: Library of existing content for linking
        
    Returns:
        Dict[str, Any]: Internal linking optimization results
    """
    optimization = {
        'current_links': [],
        'suggested_links': [],
        'link_opportunities': [],
        'anchor_text_suggestions': [],
        'link_distribution': {},
        'seo_impact': {}
    }
    
    content = article.get('content', '')
    
    # Extract current internal links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    current_links = re.findall(link_pattern, content)
    
    optimization['current_links'] = [
        {'anchor_text': match[0], 'url': match[1]} for match in current_links
    ]
    
    # Suggest new internal links based on content analysis
    if content_library:
        for content_item in content_library:
            relevance_score = calculate_content_relevance(content, content_item)
            
            if relevance_score > 0.3:  # Threshold for relevance
                optimization['suggested_links'].append({
                    'content_id': content_item['id'],
                    'title': content_item['title'],
                    'url': f"/{content_item['id']}",
                    'relevance_score': relevance_score,
                    'suggested_anchor_text': generate_anchor_text(content_item['title']),
                    'placement_suggestion': suggest_link_placement(content, content_item)
                })
    
    # Identify link opportunities
    link_opportunities = [
        'learn more', 'read more', 'see also', 'related to', 'for more information',
        'additional resources', 'further reading', 'next steps', 'get started'
    ]
    
    for opportunity in link_opportunities:
        if opportunity in content.lower():
            optimization['link_opportunities'].append({
                'text': opportunity,
                'suggestion': f"Add internal link to '{opportunity}'",
                'priority': 'medium'
            })
    
    # Generate anchor text suggestions
    optimization['anchor_text_suggestions'] = [
        'Learn more about this topic',
        'Read our comprehensive guide',
        'See related documentation',
        'Explore additional resources',
        'Check out our best practices'
    ]
    
    # Analyze link distribution
    optimization['link_distribution'] = {
        'total_links': len(optimization['current_links']),
        'suggested_links': len(optimization['suggested_links']),
        'link_density': len(optimization['current_links']) / max(1, len(content.split()) / 100),
        'recommendation': 'Add more internal links' if len(optimization['current_links']) < 3 else 'Good internal linking'
    }
    
    # Calculate SEO impact
    optimization['seo_impact'] = {
        'link_juice_distribution': 'Good' if len(optimization['current_links']) >= 3 else 'Needs improvement',
        'user_experience': 'Enhanced' if len(optimization['suggested_links']) > 0 else 'Could be better',
        'content_discoverability': 'High' if len(optimization['suggested_links']) >= 5 else 'Medium'
    }
    
    return optimization

# Helper functions

def is_term_explained(content: str, term: str) -> bool:
    """Check if a technical term is explained in the content."""
    # Look for explanation patterns around the term
    explanation_patterns = [
        rf'{re.escape(term)}[^.]*is[^.]*\.',
        rf'{re.escape(term)}[^.]*refers to[^.]*\.',
        rf'{re.escape(term)}[^.]*means[^.]*\.',
        rf'{re.escape(term)}[^.]*defined as[^.]*\.'
    ]
    
    for pattern in explanation_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def extract_topics_from_content(content: str) -> List[str]:
    """Extract main topics from content."""
    # Simple topic extraction based on common technical terms
    topics = []
    technical_terms = [
        'javascript', 'python', 'react', 'vue', 'angular', 'node', 'api',
        'database', 'sql', 'mongodb', 'css', 'html', 'git', 'docker',
        'kubernetes', 'aws', 'azure', 'testing', 'deployment', 'security'
    ]
    
    content_lower = content.lower()
    for term in technical_terms:
        if term in content_lower:
            topics.append(term)
    
    return topics[:5]  # Limit to top 5 topics

def assess_content_difficulty(content: str) -> str:
    """Assess content difficulty level."""
    advanced_indicators = ['advanced', 'expert', 'complex', 'sophisticated', 'enterprise']
    beginner_indicators = ['beginner', 'introduction', 'basic', 'simple', 'getting started']
    
    content_lower = content.lower()
    
    if any(indicator in content_lower for indicator in advanced_indicators):
        return 'advanced'
    elif any(indicator in content_lower for indicator in beginner_indicators):
        return 'beginner'
    else:
        return 'intermediate'

def determine_target_audience(content: str) -> str:
    """Determine target audience based on content."""
    developer_indicators = ['code', 'programming', 'development', 'api', 'sdk']
    business_indicators = ['strategy', 'management', 'business', 'roi', 'metrics']
    
    content_lower = content.lower()
    
    if any(indicator in content_lower for indicator in developer_indicators):
        return 'developers'
    elif any(indicator in content_lower for indicator in business_indicators):
        return 'business'
    else:
        return 'general'

def calculate_content_relevance(content: str, content_item: Dict[str, Any]) -> float:
    """Calculate relevance score between content and content item."""
    content_lower = content.lower()
    item_title = content_item.get('title', '').lower()
    item_topics = content_item.get('topics', [])
    
    relevance_score = 0
    
    # Check title similarity
    if item_title in content_lower:
        relevance_score += 0.5
    
    # Check topic matches
    topic_matches = sum(1 for topic in item_topics if topic.lower() in content_lower)
    relevance_score += topic_matches * 0.1
    
    return min(relevance_score, 1.0)

def generate_anchor_text(title: str) -> str:
    """Generate appropriate anchor text for a title."""
    # Remove common words and create concise anchor text
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = title.lower().split()
    anchor_words = [word for word in words if word not in stop_words]
    
    return ' '.join(anchor_words[:4])  # Limit to 4 words

def suggest_link_placement(content: str, content_item: Dict[str, Any]) -> str:
    """Suggest where to place a link in the content."""
    content_lower = content.lower()
    item_title = content_item.get('title', '').lower()
    
    # Find the best placement based on content structure
    if 'introduction' in content_lower or 'overview' in content_lower:
        return 'introduction'
    elif 'conclusion' in content_lower or 'summary' in content_lower:
        return 'conclusion'
    else:
        return 'middle'
