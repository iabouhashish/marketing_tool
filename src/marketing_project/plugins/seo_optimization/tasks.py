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
    calculate_seo_score: Calculates overall SEO score for content
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from marketing_project.core.models import AppContext, ContentContext
from marketing_project.core.utils import (
    create_standard_task_result,
    ensure_content_context,
    extract_content_metadata_for_pipeline,
    validate_content_for_processing,
)

logger = logging.getLogger("marketing_project.plugins.seo_optimization")


def optimize_title_tags(
    article: Union[Dict[str, Any], ContentContext],
    keywords: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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
                "title": article.title,
                "content": article.content,
                "meta_description": "",
            }
        else:
            article_data = article

        optimization = {
            "current_title": article_data.get("title", ""),
            "optimized_titles": [],
            "recommendations": [],
            "seo_score": 0,
            "character_count": 0,
        }

        current_title = article_data.get("title", "")
        optimization["character_count"] = len(current_title)

        # Check title length
        if len(current_title) < 30:
            optimization["recommendations"].append(
                "Title is too short (aim for 30-60 characters)"
            )
        elif len(current_title) > 60:
            optimization["recommendations"].append(
                "Title is too long (aim for 30-60 characters)"
            )
        else:
            optimization["recommendations"].append("Title length is optimal")

        # Generate optimized titles
        if keywords and len(keywords) > 0:
            primary_keyword = keywords[0]["keyword"]
            secondary_keywords = [kw["keyword"] for kw in keywords[1:3]]

            # Title variations
            title_variations = [
                f"{primary_keyword.title()}: Complete Guide",
                f"How to {primary_keyword.title()}: Expert Tips",
                f"{primary_keyword.title()} Best Practices for 2024",
                f"Ultimate {primary_keyword.title()} Guide",
                f"{primary_keyword.title()} - Everything You Need to Know",
            ]

            # Add secondary keywords if space allows
            for variation in title_variations:
                if len(variation) <= 60:
                    if (
                        secondary_keywords
                        and len(variation) + len(secondary_keywords[0]) + 3 <= 60
                    ):
                        variation += f" & {secondary_keywords[0]}"
                    optimization["optimized_titles"].append(variation)

        # Check for power words
        power_words = [
            "ultimate",
            "complete",
            "guide",
            "best",
            "expert",
            "proven",
            "essential",
            "comprehensive",
        ]
        has_power_words = any(word in current_title.lower() for word in power_words)
        if not has_power_words:
            optimization["recommendations"].append(
                "Consider adding power words to increase click-through rate"
            )

        # Check for emotional triggers
        emotional_words = [
            "amazing",
            "incredible",
            "shocking",
            "secret",
            "revealed",
            "discovered",
        ]
        has_emotional_words = any(
            word in current_title.lower() for word in emotional_words
        )
        if not has_emotional_words:
            optimization["recommendations"].append(
                "Consider adding emotional triggers to improve engagement"
            )

        # Calculate SEO score
        seo_factors = {
            "length_ok": 30 <= len(current_title) <= 60,
            "has_keywords": (
                any(kw["keyword"].lower() in current_title.lower() for kw in keywords)
                if keywords
                else False
            ),
            "has_power_words": has_power_words,
            "has_emotional_words": has_emotional_words,
            "starts_with_keyword": (
                current_title.lower().startswith(primary_keyword.lower())
                if keywords and keywords
                else False
            ),
        }

        optimization["seo_score"] = sum(seo_factors.values()) / len(seo_factors) * 100

        return create_standard_task_result(
            success=True,
            data=optimization,
            task_name="optimize_title_tags",
            metadata={
                "current_title_length": len(current_title),
                "optimized_titles_count": len(optimization["optimized_titles"]),
                "seo_score": optimization["seo_score"],
            },
        )

    except Exception as e:
        logger.error(f"Error in optimize_title_tags: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"Title optimization failed: {str(e)}",
            task_name="optimize_title_tags",
        )


def optimize_meta_descriptions(
    article: Union[Dict[str, Any], ContentContext],
    keywords: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Optimizes meta descriptions for better SEO performance.

    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for optimization

    Returns:
        Dict[str, Any]: Optimized meta descriptions and recommendations
    """
    optimization = {
        "current_meta": article.get("meta_description", ""),
        "optimized_meta": [],
        "recommendations": [],
        "seo_score": 0,
        "character_count": 0,
    }

    current_meta = article.get("meta_description", "")
    optimization["character_count"] = len(current_meta)

    # Check meta description length
    if len(current_meta) < 120:
        optimization["recommendations"].append(
            "Meta description is too short (aim for 120-160 characters)"
        )
    elif len(current_meta) > 160:
        optimization["recommendations"].append(
            "Meta description is too long (aim for 120-160 characters)"
        )
    else:
        optimization["recommendations"].append("Meta description length is optimal")

    # Generate optimized meta descriptions
    if keywords and len(keywords) > 0:
        primary_keyword = keywords[0]["keyword"]
        secondary_keywords = [kw["keyword"] for kw in keywords[1:3]]

        # Get content summary
        content_summary = (
            article.get("content", "")[:200] + "..."
            if len(article.get("content", "")) > 200
            else article.get("content", "")
        )

        # Meta description variations
        meta_variations = [
            f"Learn {primary_keyword} with our comprehensive guide. {content_summary[:100]}",
            f"Discover the best {primary_keyword} strategies and tips. {content_summary[:100]}",
            f"Master {primary_keyword} with expert insights and practical advice. {content_summary[:100]}",
            f"Everything you need to know about {primary_keyword}. {content_summary[:100]}",
            f"Complete {primary_keyword} guide with step-by-step instructions. {content_summary[:100]}",
        ]

        for variation in meta_variations:
            if 120 <= len(variation) <= 160:
                optimization["optimized_meta"].append(variation)

    # Check for call-to-action
    cta_words = ["learn", "discover", "find out", "get started", "explore", "read more"]
    has_cta = any(word in current_meta.lower() for word in cta_words)
    if not has_cta:
        optimization["recommendations"].append(
            "Add a call-to-action to encourage clicks"
        )

    # Check for keyword inclusion
    if keywords:
        has_primary_keyword = primary_keyword.lower() in current_meta.lower()
        if not has_primary_keyword:
            optimization["recommendations"].append(
                "Include primary keyword in meta description"
            )

    # Calculate SEO score
    seo_factors = {
        "length_ok": 120 <= len(current_meta) <= 160,
        "has_keywords": (
            any(kw["keyword"].lower() in current_meta.lower() for kw in keywords)
            if keywords
            else False
        ),
        "has_cta": has_cta,
        "unique_content": current_meta != article.get("title", ""),
        "compelling": any(
            word in current_meta.lower()
            for word in ["best", "ultimate", "complete", "guide", "tips", "strategies"]
        ),
    }

    optimization["seo_score"] = sum(seo_factors.values()) / len(seo_factors) * 100

    return optimization


def optimize_headings(
    article: Dict[str, Any], keywords: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Optimizes heading structure and content for SEO.

    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for optimization

    Returns:
        Dict[str, Any]: Optimized headings and recommendations
    """
    optimization = {
        "current_headings": [],
        "optimized_headings": [],
        "recommendations": [],
        "seo_score": 0,
        "heading_structure": {},
    }

    content = article.get("content", "")

    # Extract current headings
    h1_pattern = r"^# (.+)$"
    h2_pattern = r"^## (.+)$"
    h3_pattern = r"^### (.+)$"

    h1_headings = re.findall(h1_pattern, content, re.MULTILINE)
    h2_headings = re.findall(h2_pattern, content, re.MULTILINE)
    h3_headings = re.findall(h3_pattern, content, re.MULTILINE)

    optimization["current_headings"] = {
        "h1": h1_headings,
        "h2": h2_headings,
        "h3": h3_headings,
    }

    optimization["heading_structure"] = {
        "h1_count": len(h1_headings),
        "h2_count": len(h2_headings),
        "h3_count": len(h3_headings),
        "total_headings": len(h1_headings) + len(h2_headings) + len(h3_headings),
    }

    # Check heading structure
    if len(h1_headings) == 0:
        optimization["recommendations"].append(
            "Add an H1 heading for better SEO structure"
        )
    elif len(h1_headings) > 1:
        optimization["recommendations"].append("Use only one H1 heading per page")

    if len(h2_headings) < 3:
        optimization["recommendations"].append(
            "Add more H2 headings to improve content structure"
        )

    # Optimize headings with keywords
    if keywords and len(keywords) > 0:
        primary_keyword = keywords[0]["keyword"]
        secondary_keywords = [kw["keyword"] for kw in keywords[1:4]]

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
            if (
                i < len(secondary_keywords)
                and secondary_keywords[i].lower() not in h3.lower()
            ):
                optimized_h3.append(f"{h3} - {secondary_keywords[i].title()}")
            else:
                optimized_h3.append(h3)

        optimization["optimized_headings"] = {
            "h1": h1_headings,
            "h2": optimized_h2,
            "h3": optimized_h3,
        }

    # Check heading length
    for heading_list in [h1_headings, h2_headings, h3_headings]:
        for heading in heading_list:
            if len(heading) > 60:
                optimization["recommendations"].append(
                    f'Heading too long: "{heading[:50]}..." (aim for 60 characters or less)'
                )

    # Calculate SEO score
    seo_factors = {
        "has_h1": len(h1_headings) == 1,
        "has_h2": len(h2_headings) >= 3,
        "has_h3": len(h3_headings) > 0,
        "keyword_in_headings": (
            any(
                kw["keyword"].lower() in " ".join(h2_headings + h3_headings).lower()
                for kw in keywords
            )
            if keywords
            else False
        ),
        "proper_hierarchy": len(h1_headings) <= 1
        and len(h2_headings) >= len(h3_headings),
    }

    optimization["seo_score"] = sum(seo_factors.values()) / len(seo_factors) * 100

    return optimization


def optimize_content_structure(
    article: Dict[str, Any], keywords: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Optimizes overall content structure for SEO.

    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for optimization

    Returns:
        Dict[str, Any]: Content structure optimization results
    """
    optimization = {
        "word_count": 0,
        "paragraph_count": 0,
        "sentence_count": 0,
        "readability_score": 0,
        "keyword_density": {},
        "recommendations": [],
        "seo_score": 0,
    }

    content = article.get("content", "")
    words = content.split()
    optimization["word_count"] = len(words)

    # Count paragraphs and sentences
    paragraphs = content.split("\n\n")
    optimization["paragraph_count"] = len(paragraphs)

    sentences = re.split(r"[.!?]+", content)
    optimization["sentence_count"] = len([s for s in sentences if s.strip()])

    # Calculate readability score (simplified)
    avg_sentence_length = (
        optimization["word_count"] / optimization["sentence_count"]
        if optimization["sentence_count"] > 0
        else 0
    )
    optimization["readability_score"] = max(0, 100 - (avg_sentence_length * 1.5))

    # Analyze keyword density
    if keywords:
        content_lower = content.lower()
        for keyword_data in keywords:
            keyword = keyword_data["keyword"].lower()
            frequency = content_lower.count(keyword)
            density = (
                (frequency / optimization["word_count"]) * 100
                if optimization["word_count"] > 0
                else 0
            )

            optimization["keyword_density"][keyword] = {
                "frequency": frequency,
                "density": density,
                "status": "optimal" if 1 <= density <= 3 else "needs_optimization",
            }

    # Generate recommendations
    if optimization["word_count"] < 1000:
        optimization["recommendations"].append(
            "Content is too short (aim for 1000+ words)"
        )
    elif optimization["word_count"] > 3000:
        optimization["recommendations"].append(
            "Content may be too long (consider breaking into series)"
        )

    if optimization["paragraph_count"] < 5:
        optimization["recommendations"].append(
            "Add more paragraphs for better structure"
        )

    if optimization["readability_score"] < 60:
        optimization["recommendations"].append(
            "Improve readability with shorter sentences"
        )

    # Check for keyword optimization
    if keywords:
        for keyword, data in optimization["keyword_density"].items():
            if data["density"] < 1:
                optimization["recommendations"].append(
                    f'Increase "{keyword}" keyword density'
                )
            elif data["density"] > 3:
                optimization["recommendations"].append(
                    f'Reduce "{keyword}" keyword density'
                )

    # Calculate SEO score
    seo_factors = {
        "word_count_ok": 1000 <= optimization["word_count"] <= 3000,
        "paragraph_count_ok": optimization["paragraph_count"] >= 5,
        "readability_ok": optimization["readability_score"] >= 60,
        "keyword_density_ok": (
            all(
                data["status"] == "optimal"
                for data in optimization["keyword_density"].values()
            )
            if optimization["keyword_density"]
            else True
        ),
    }

    optimization["seo_score"] = sum(seo_factors.values()) / len(seo_factors) * 100

    return optimization


def add_internal_links(
    article: Dict[str, Any], internal_pages: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
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
            {
                "url": "/blog",
                "title": "Blog",
                "keywords": ["blog", "articles", "content"],
            },
            {
                "url": "/resources",
                "title": "Resources",
                "keywords": ["resources", "guides", "tools"],
            },
            {
                "url": "/about",
                "title": "About Us",
                "keywords": ["about", "company", "team"],
            },
            {
                "url": "/contact",
                "title": "Contact",
                "keywords": ["contact", "get in touch", "reach out"],
            },
        ]

    enhanced_article["internal_links"] = []
    content = article.get("content", "")

    # Find opportunities for internal links
    for page in internal_pages:
        for keyword in page["keywords"]:
            if keyword.lower() in content.lower():
                # Find the first occurrence and add link
                pattern = rf"\b{re.escape(keyword)}\b"
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    link_text = f"[{keyword}]({page['url']})"
                    enhanced_article["internal_links"].append(
                        {
                            "keyword": keyword,
                            "url": page["url"],
                            "title": page["title"],
                            "position": match.start(),
                            "link_text": link_text,
                        }
                    )
                    break

    # Add contextual internal links
    contextual_links = [
        {"keyword": "learn more", "url": "/learn", "title": "Learning Center"},
        {
            "keyword": "get started",
            "url": "/getting-started",
            "title": "Getting Started",
        },
        {
            "keyword": "best practices",
            "url": "/best-practices",
            "title": "Best Practices",
        },
        {"keyword": "case study", "url": "/case-studies", "title": "Case Studies"},
    ]

    for link in contextual_links:
        if link["keyword"].lower() in content.lower():
            enhanced_article["internal_links"].append(
                {
                    "keyword": link["keyword"],
                    "url": link["url"],
                    "title": link["title"],
                    "type": "contextual",
                }
            )

    return enhanced_article


def analyze_seo_performance(
    article: Dict[str, Any], keywords: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes overall SEO performance and provides comprehensive recommendations.

    Args:
        article: Article dictionary with content
        keywords: List of SEO keywords for analysis

    Returns:
        Dict[str, Any]: Comprehensive SEO performance analysis
    """
    analysis = {
        "overall_score": 0,
        "title_optimization": {},
        "meta_optimization": {},
        "heading_optimization": {},
        "content_optimization": {},
        "technical_seo": {},
        "recommendations": [],
        "priority_actions": [],
    }

    # Analyze title
    title_analysis = optimize_title_tags(article, keywords)
    analysis["title_optimization"] = title_analysis

    # Analyze meta description
    meta_analysis = optimize_meta_descriptions(article, keywords)
    analysis["meta_optimization"] = meta_analysis

    # Analyze headings
    heading_analysis = optimize_headings(article, keywords)
    analysis["heading_optimization"] = heading_analysis

    # Analyze content structure
    content_analysis = optimize_content_structure(article, keywords)
    analysis["content_optimization"] = content_analysis

    # Technical SEO analysis
    technical_analysis = analyze_technical_seo(article)
    analysis["technical_seo"] = technical_analysis

    # Calculate overall score
    scores = [
        (
            title_analysis["data"]["seo_score"]
            if "data" in title_analysis
            else title_analysis["seo_score"]
        ),
        meta_analysis["seo_score"],
        heading_analysis["seo_score"],
        content_analysis["seo_score"],
        technical_analysis["seo_score"],
    ]
    analysis["overall_score"] = sum(scores) / len(scores)

    # Compile recommendations
    all_recommendations = (
        title_analysis["data"]["recommendations"]
        if "data" in title_analysis
        else title_analysis["recommendations"]
        + meta_analysis["recommendations"]
        + heading_analysis["recommendations"]
        + content_analysis["recommendations"]
        + technical_analysis["recommendations"]
    )
    analysis["recommendations"] = list(set(all_recommendations))  # Remove duplicates

    # Identify priority actions
    if analysis["overall_score"] < 70:
        analysis["priority_actions"] = [
            "Fix critical SEO issues first",
            "Optimize title and meta description",
            "Improve content structure",
            "Add missing keywords",
        ]
    elif analysis["overall_score"] < 85:
        analysis["priority_actions"] = [
            "Fine-tune keyword optimization",
            "Improve content readability",
            "Add more internal links",
            "Enhance heading structure",
        ]
    else:
        analysis["priority_actions"] = [
            "Maintain current optimization",
            "Monitor performance metrics",
            "A/B test different approaches",
            "Focus on content quality",
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
    technical = {"seo_score": 0, "recommendations": [], "checks": {}}

    content = article.get("content", "")
    title = article.get("title", "")
    meta_description = article.get("meta_description", "")

    # Technical SEO checks
    checks = {
        "has_title": bool(title),
        "has_meta_description": bool(meta_description),
        "title_length_ok": 30 <= len(title) <= 60,
        "meta_length_ok": 120 <= len(meta_description) <= 160,
        "has_h1": "#" in content,
        "has_h2": "##" in content,
        "word_count_ok": 1000 <= len(content.split()) <= 3000,
        "has_images": "![" in content,
        "has_links": "](" in content,
        "has_lists": any(marker in content for marker in ["- ", "* ", "1. ", "2. "]),
    }

    technical["checks"] = checks
    technical["seo_score"] = sum(checks.values()) / len(checks) * 100

    # Generate recommendations based on failed checks
    if not checks["has_title"]:
        technical["recommendations"].append("Add a title tag")
    if not checks["has_meta_description"]:
        technical["recommendations"].append("Add a meta description")
    if not checks["title_length_ok"]:
        technical["recommendations"].append("Optimize title length (30-60 characters)")
    if not checks["meta_length_ok"]:
        technical["recommendations"].append(
            "Optimize meta description length (120-160 characters)"
        )
    if not checks["has_h1"]:
        technical["recommendations"].append("Add H1 heading")
    if not checks["has_h2"]:
        technical["recommendations"].append("Add H2 headings")
    if not checks["word_count_ok"]:
        technical["recommendations"].append("Optimize content length (1000-3000 words)")
    if not checks["has_images"]:
        technical["recommendations"].append("Add relevant images")
    if not checks["has_links"]:
        technical["recommendations"].append("Add internal and external links")
    if not checks["has_lists"]:
        technical["recommendations"].append("Use lists for better readability")

    return technical


def calculate_seo_score(
    article: Union[Dict[str, Any], ContentContext],
    keywords: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculates an overall SEO score for the article based on multiple factors.

    Args:
        article: Article dictionary with content or ContentContext
        keywords: List of SEO keywords for scoring

    Returns:
        Dict[str, Any]: Standardized task result with SEO score and breakdown
    """
    try:
        # Handle both dict and ContentContext inputs
        if isinstance(article, ContentContext):
            article_data = {
                "title": article.title,
                "content": article.content,
                "meta_description": getattr(article, "snippet", ""),
                "url": getattr(article, "source_url", ""),
            }
        else:
            article_data = article

        # Initialize scoring components
        score_breakdown = {
            "title_optimization": 0,
            "meta_description": 0,
            "content_quality": 0,
            "keyword_optimization": 0,
            "technical_seo": 0,
            "content_structure": 0,
            "readability": 0,
            "internal_linking": 0,
        }

        total_score = 0
        max_possible_score = 0

        # 1. Title Optimization (20 points)
        title = article_data.get("title", "")
        title_score = 0
        title_issues = []

        if title:
            title_length = len(title)
            if 30 <= title_length <= 60:
                title_score += 15  # Optimal length
            elif 20 <= title_length <= 70:
                title_score += 10  # Acceptable length
            else:
                title_issues.append(
                    f"Title length ({title_length}) should be 30-60 characters"
                )

            # Check for keyword in title
            if keywords and any(
                kw["keyword"].lower() in title.lower() for kw in keywords[:3]
            ):
                title_score += 5
            elif keywords:
                title_issues.append("Primary keyword not found in title")
        else:
            title_issues.append("Missing title")

        score_breakdown["title_optimization"] = title_score
        total_score += title_score
        max_possible_score += 20

        # 2. Meta Description (15 points)
        meta_desc = article_data.get("meta_description", "")
        meta_score = 0
        meta_issues = []

        if meta_desc:
            meta_length = len(meta_desc)
            if 120 <= meta_length <= 160:
                meta_score += 15  # Optimal length
            elif 100 <= meta_length <= 180:
                meta_score += 10  # Acceptable length
            else:
                meta_issues.append(
                    f"Meta description length ({meta_length}) should be 120-160 characters"
                )

            # Check for keyword in meta description
            if keywords and any(
                kw["keyword"].lower() in meta_desc.lower() for kw in keywords[:3]
            ):
                meta_score += 0  # Already included in length score
            elif keywords:
                meta_issues.append("Primary keyword not found in meta description")
        else:
            meta_issues.append("Missing meta description")

        score_breakdown["meta_description"] = meta_score
        total_score += meta_score
        max_possible_score += 15

        # 3. Content Quality (25 points)
        content = article_data.get("content", "")
        content_score = 0
        content_issues = []

        if content:
            word_count = len(content.split())

            # Word count scoring
            if 1000 <= word_count <= 3000:
                content_score += 15  # Optimal length
            elif 500 <= word_count <= 5000:
                content_score += 10  # Acceptable length
            else:
                content_issues.append(
                    f"Content length ({word_count} words) should be 1000-3000 words"
                )

            # Check for headings
            heading_count = len(re.findall(r"<h[1-6]", content)) + len(
                re.findall(r"^#+", content, re.MULTILINE)
            )
            if heading_count >= 3:
                content_score += 5
            else:
                content_issues.append("Add more headings for better structure")

            # Check for images
            image_count = len(re.findall(r"<img", content)) + len(
                re.findall(r"!\[", content)
            )
            if image_count >= 1:
                content_score += 5
            else:
                content_issues.append("Add relevant images")
        else:
            content_issues.append("Missing content")

        score_breakdown["content_quality"] = content_score
        total_score += content_score
        max_possible_score += 25

        # 4. Keyword Optimization (20 points)
        keyword_score = 0
        keyword_issues = []

        if keywords and content:
            primary_keywords = [kw["keyword"] for kw in keywords[:3]]
            keyword_density = {}

            for keyword in primary_keywords:
                keyword_lower = keyword.lower()
                content_lower = content.lower()
                word_count = len(content.split())
                keyword_count = content_lower.count(keyword_lower)
                density = (keyword_count / word_count) * 100 if word_count > 0 else 0
                keyword_density[keyword] = density

                if 1 <= density <= 3:
                    keyword_score += 6  # Optimal density
                elif 0.5 <= density <= 5:
                    keyword_score += 4  # Acceptable density
                else:
                    keyword_issues.append(
                        f"Keyword '{keyword}' density ({density:.1f}%) should be 1-3%"
                    )
        else:
            keyword_issues.append("No keywords provided for optimization")

        score_breakdown["keyword_optimization"] = keyword_score
        total_score += keyword_score
        max_possible_score += 20

        # 5. Technical SEO (10 points)
        technical_score = 0
        technical_issues = []

        # Check for H1 tag
        if re.search(r"<h1[^>]*>", content) or re.search(r"^# ", content, re.MULTILINE):
            technical_score += 3
        else:
            technical_issues.append("Missing H1 heading")

        # Check for internal links
        internal_links = len(re.findall(r'href=["\'](?!https?://)', content))
        if internal_links >= 2:
            technical_score += 3
        elif internal_links >= 1:
            technical_score += 2
        else:
            technical_issues.append("Add internal links")

        # Check for external links
        external_links = len(re.findall(r'href=["\']https?://', content))
        if external_links >= 1:
            technical_score += 2
        else:
            technical_issues.append("Add external links for credibility")

        # Check for alt text on images
        images_with_alt = len(re.findall(r'<img[^>]*alt=["\'][^"\']+["\']', content))
        if images_with_alt >= 1:
            technical_score += 2
        else:
            technical_issues.append("Add alt text to images")

        score_breakdown["technical_seo"] = technical_score
        total_score += technical_score
        max_possible_score += 10

        # 6. Content Structure (5 points)
        structure_score = 0
        structure_issues = []

        # Check for lists
        list_count = len(re.findall(r"<[uo]l", content)) + len(
            re.findall(r"^\s*[-*+]\s", content, re.MULTILINE)
        )
        if list_count >= 1:
            structure_score += 3
        else:
            structure_issues.append("Add lists for better readability")

        # Check for paragraphs
        paragraph_count = len(re.findall(r"<p", content)) + len(
            re.findall(r"\n\s*\n", content)
        )
        if paragraph_count >= 3:
            structure_score += 2
        else:
            structure_issues.append("Add more paragraphs for better structure")

        score_breakdown["content_structure"] = structure_score
        total_score += structure_score
        max_possible_score += 5

        # 7. Readability (3 points)
        readability_score = 0
        readability_issues = []

        if content:
            sentences = re.split(r"[.!?]+", content)
            avg_sentence_length = (
                sum(len(s.split()) for s in sentences) / len(sentences)
                if sentences
                else 0
            )

            if avg_sentence_length <= 20:
                readability_score += 3
            elif avg_sentence_length <= 25:
                readability_score += 2
            else:
                readability_issues.append(
                    "Reduce average sentence length for better readability"
                )

        score_breakdown["readability"] = readability_score
        total_score += readability_score
        max_possible_score += 3

        # 8. Internal Linking (2 points)
        linking_score = 0
        linking_issues = []

        if internal_links >= 3:
            linking_score += 2
        elif internal_links >= 1:
            linking_score += 1
        else:
            linking_issues.append("Add more internal links")

        score_breakdown["internal_linking"] = linking_score
        total_score += linking_score
        max_possible_score += 2

        # Calculate overall score percentage
        overall_score = (
            (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        )

        # Determine SEO grade
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"

        # Compile all issues
        all_issues = []
        all_issues.extend(title_issues)
        all_issues.extend(meta_issues)
        all_issues.extend(content_issues)
        all_issues.extend(keyword_issues)
        all_issues.extend(technical_issues)
        all_issues.extend(structure_issues)
        all_issues.extend(readability_issues)
        all_issues.extend(linking_issues)

        # Generate recommendations
        recommendations = []
        if overall_score < 70:
            recommendations.append(
                "Focus on improving title and meta description optimization"
            )
        if score_breakdown["content_quality"] < 15:
            recommendations.append("Improve content quality and length")
        if score_breakdown["keyword_optimization"] < 15:
            recommendations.append(
                "Better integrate target keywords throughout content"
            )
        if score_breakdown["technical_seo"] < 7:
            recommendations.append("Address technical SEO issues")

        seo_analysis = {
            "overall_seo_score": round(overall_score, 1),
            "seo_grade": grade,
            "score_breakdown": score_breakdown,
            "total_possible_score": max_possible_score,
            "actual_score": total_score,
            "issues": all_issues,
            "recommendations": recommendations,
            "keyword_density": keyword_density if keywords else {},
            "content_metrics": {
                "word_count": len(content.split()) if content else 0,
                "heading_count": len(re.findall(r"<h[1-6]", content))
                + len(re.findall(r"^#+", content, re.MULTILINE)),
                "image_count": len(re.findall(r"<img", content))
                + len(re.findall(r"!\[", content)),
                "internal_links": internal_links,
                "external_links": external_links,
            },
        }

        return create_standard_task_result(
            success=True,
            data=seo_analysis,
            task_name="calculate_seo_score",
            metadata={
                "overall_score": overall_score,
                "grade": grade,
                "total_issues": len(all_issues),
                "recommendations_count": len(recommendations),
            },
        )

    except Exception as e:
        logger.error(f"Error in calculate_seo_score: {str(e)}")
        return create_standard_task_result(
            success=False,
            error=f"SEO score calculation failed: {str(e)}",
            task_name="calculate_seo_score",
        )
