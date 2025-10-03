"""
OCR (Optical Character Recognition) service for Marketing Project.

This module provides OCR functionality for extracting text from images
that may be embedded in content like blog posts, release notes, or transcripts.

Functions:
    extract_text_from_image: Extract text from image bytes using OCR
    extract_text_from_url: Download and extract text from image URL
    process_content_images: Process all images in content and extract text
    enhance_content_with_ocr: Enhance content with OCR text from images
"""

import base64
import io
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import pytesseract
import requests
from PIL import Image

logger = logging.getLogger("marketing_project.services.ocr")


def extract_text_from_image(image_bytes: bytes, language: str = "eng") -> str:
    """
    Extract text from image bytes using OCR.

    Args:
        image_bytes: Image data as bytes
        language: OCR language code (default: 'eng')

    Returns:
        Extracted text string
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Extract text using pytesseract
        text = pytesseract.image_to_string(image, lang=language)

        # Clean up the text
        text = text.strip()
        text = re.sub(r"\s+", " ", text)  # Normalize whitespace

        logger.info(f"Extracted {len(text)} characters from image using OCR")
        return text

    except Exception as e:
        logger.error(f"OCR failed for image: {e}")
        return ""


def extract_text_from_url(image_url: str, language: str = "eng") -> str:
    """
    Download image from URL and extract text using OCR.

    Args:
        image_url: URL of the image
        language: OCR language code (default: 'eng')

    Returns:
        Extracted text string
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # Extract text
        return extract_text_from_image(response.content, language)

    except Exception as e:
        logger.error(f"Failed to download and OCR image from {image_url}: {e}")
        return ""


def process_content_images(
    content: str, image_urls: List[str] = None, image_data: List[bytes] = None
) -> Dict[str, Any]:
    """
    Process all images in content and extract text using OCR.

    Args:
        content: Content text that may reference images
        image_urls: List of image URLs to process
        image_data: List of image data as bytes

    Returns:
        Dictionary with OCR results and enhanced content
    """
    ocr_results = {
        "extracted_texts": [],
        "image_count": 0,
        "total_ocr_text": "",
        "enhanced_content": content,
    }

    # Process image URLs
    if image_urls:
        for url in image_urls:
            try:
                text = extract_text_from_url(url)
                if text:
                    ocr_results["extracted_texts"].append(
                        {"source": url, "text": text, "type": "url"}
                    )
                    ocr_results["total_ocr_text"] += f"\n\n[Image from {url}]:\n{text}"
                    ocr_results["image_count"] += 1
            except Exception as e:
                logger.warning(f"Failed to process image URL {url}: {e}")

    # Process image data
    if image_data:
        for i, img_bytes in enumerate(image_data):
            try:
                text = extract_text_from_image(img_bytes)
                if text:
                    ocr_results["extracted_texts"].append(
                        {"source": f"image_data_{i}", "text": text, "type": "data"}
                    )
                    ocr_results["total_ocr_text"] += f"\n\n[Image {i+1}]:\n{text}"
                    ocr_results["image_count"] += 1
            except Exception as e:
                logger.warning(f"Failed to process image data {i}: {e}")

    # Enhance content with OCR text
    if ocr_results["total_ocr_text"]:
        ocr_results["enhanced_content"] = (
            content + "\n\n--- OCR Extracted Text ---" + ocr_results["total_ocr_text"]
        )

    return ocr_results


def enhance_content_with_ocr(
    content: str,
    content_type: str,
    image_urls: List[str] = None,
    image_data: List[bytes] = None,
) -> Dict[str, Any]:
    """
    Enhance content with OCR text from images based on content type.

    Args:
        content: Original content text
        content_type: Type of content (transcript, blog_post, release_notes)
        image_urls: List of image URLs to process
        image_data: List of image data as bytes

    Returns:
        Enhanced content with OCR text
    """
    # Process images
    ocr_results = process_content_images(content, image_urls, image_data)

    # Enhance based on content type
    enhanced_content = {
        "original_content": content,
        "enhanced_content": ocr_results["enhanced_content"],
        "ocr_text": ocr_results["total_ocr_text"],
        "image_count": ocr_results["image_count"],
        "content_type": content_type,
    }

    # Add type-specific enhancements
    if content_type == "transcript":
        enhanced_content["has_visual_content"] = ocr_results["image_count"] > 0
        enhanced_content["visual_transcript"] = ocr_results["total_ocr_text"]
    elif content_type == "blog_post":
        enhanced_content["has_images"] = ocr_results["image_count"] > 0
        enhanced_content["image_alt_text"] = ocr_results["total_ocr_text"]
    elif content_type == "release_notes":
        enhanced_content["has_screenshots"] = ocr_results["image_count"] > 0
        enhanced_content["screenshot_text"] = ocr_results["total_ocr_text"]

    return enhanced_content


def extract_images_from_content(content: str) -> List[str]:
    """
    Extract image URLs from content text.

    Args:
        content: Content text that may contain image URLs

    Returns:
        List of image URLs found in content
    """
    # Pattern to match various image URL formats
    image_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:jpg|jpeg|png|gif|bmp|webp|svg)(?:\?[^\s<>"{}|\\^`\[\]]*)?'

    urls = re.findall(image_pattern, content, re.IGNORECASE)

    # Filter out non-image URLs that might match the pattern
    image_urls = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.path.lower().endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg")
            ):
                image_urls.append(url)
        except Exception:
            continue

    return image_urls


def validate_image_url(url: str) -> bool:
    """
    Validate if a URL points to a valid image.

    Args:
        url: URL to validate

    Returns:
        True if URL appears to be a valid image
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check if URL ends with image extension
        image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg")
        return parsed.path.lower().endswith(image_extensions)

    except Exception:
        return False
