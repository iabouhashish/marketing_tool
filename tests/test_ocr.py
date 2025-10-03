"""
Tests for the OCR service.
"""

from unittest.mock import Mock, patch

import pytest

from marketing_project.services.ocr import (
    enhance_content_with_ocr,
    extract_images_from_content,
    extract_text_from_image,
    extract_text_from_url,
    process_content_images,
    validate_image_url,
)


def test_extract_images_from_content():
    """Test image URL extraction from content."""
    content = """
    Check out this image: https://example.com/image.jpg
    And this one: https://test.com/photo.png?size=large
    Not an image: https://example.com/document.pdf
    """

    urls = extract_images_from_content(content)
    assert len(urls) == 2
    assert "https://example.com/image.jpg" in urls
    assert "https://test.com/photo.png?size=large" in urls
    assert "https://example.com/document.pdf" not in urls


def test_validate_image_url():
    """Test image URL validation."""
    # Valid image URLs
    assert validate_image_url("https://example.com/image.jpg") == True
    assert validate_image_url("https://test.com/photo.png") == True
    assert validate_image_url("https://site.com/pic.gif") == True

    # Invalid URLs
    assert validate_image_url("not-a-url") == False
    assert validate_image_url("https://example.com/doc.pdf") == False
    assert validate_image_url("") == False


@patch("marketing_project.services.ocr.pytesseract.image_to_string")
@patch("marketing_project.services.ocr.Image.open")
def test_extract_text_from_image(mock_image_open, mock_ocr):
    """Test OCR text extraction from image bytes."""
    # Mock the OCR response
    mock_ocr.return_value = "Extracted text from image"

    # Mock image opening
    mock_image = Mock()
    mock_image.mode = "RGB"
    mock_image.convert.return_value = mock_image
    mock_image_open.return_value = mock_image

    # Test with image bytes
    image_bytes = b"fake_image_data"
    result = extract_text_from_image(image_bytes)

    assert result == "Extracted text from image"
    mock_image_open.assert_called_once()
    mock_ocr.assert_called_once()


@patch("marketing_project.services.ocr.requests.get")
@patch("marketing_project.services.ocr.extract_text_from_image")
def test_extract_text_from_url(mock_extract, mock_get):
    """Test OCR text extraction from image URL."""
    # Mock the HTTP response
    mock_response = Mock()
    mock_response.content = b"image_data"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Mock the OCR extraction
    mock_extract.return_value = "Text from URL image"

    # Test
    result = extract_text_from_url("https://example.com/image.jpg")

    assert result == "Text from URL image"
    mock_get.assert_called_once_with("https://example.com/image.jpg", timeout=30)
    mock_extract.assert_called_once_with(b"image_data", "eng")


def test_process_content_images():
    """Test processing images in content."""
    content = "This is some content with images."
    image_urls = ["https://example.com/image1.jpg", "https://example.com/image2.png"]

    with patch("marketing_project.services.ocr.extract_text_from_url") as mock_extract:
        mock_extract.side_effect = ["Text from image 1", "Text from image 2"]

        result = process_content_images(content, image_urls)

        assert "extracted_texts" in result
        assert "image_count" in result
        assert "total_ocr_text" in result
        assert "enhanced_content" in result
        assert result["image_count"] == 2
        assert len(result["extracted_texts"]) == 2
        assert "Text from image 1" in result["total_ocr_text"]
        assert "Text from image 2" in result["total_ocr_text"]


def test_enhance_content_with_ocr():
    """Test content enhancement with OCR."""
    content = "This is content with images."
    image_urls = ["https://example.com/screenshot.jpg"]

    with patch("marketing_project.services.ocr.process_content_images") as mock_process:
        mock_process.return_value = {
            "enhanced_content": "Enhanced content with OCR text",
            "total_ocr_text": "OCR text from images",
            "image_count": 1,
        }

        result = enhance_content_with_ocr(content, "blog_post", image_urls)

        assert "original_content" in result
        assert "enhanced_content" in result
        assert "ocr_text" in result
        assert "image_count" in result
        assert result["content_type"] == "blog_post"
        assert result["has_images"] == True


def test_enhance_content_with_ocr_transcript():
    """Test content enhancement for transcript type."""
    content = "Speaker 1: Hello world!"

    with patch("marketing_project.services.ocr.process_content_images") as mock_process:
        mock_process.return_value = {
            "enhanced_content": "Enhanced transcript with OCR",
            "total_ocr_text": "Visual transcript text",
            "image_count": 1,
        }

        result = enhance_content_with_ocr(content, "transcript")

        assert result["content_type"] == "transcript"
        assert "has_visual_content" in result
        assert "visual_transcript" in result


def test_enhance_content_with_ocr_release_notes():
    """Test content enhancement for release notes type."""
    content = "Version 2.0.0 is here!"

    with patch("marketing_project.services.ocr.process_content_images") as mock_process:
        mock_process.return_value = {
            "enhanced_content": "Enhanced release notes with OCR",
            "total_ocr_text": "Screenshot text",
            "image_count": 1,
        }

        result = enhance_content_with_ocr(content, "release_notes")

        assert result["content_type"] == "release_notes"
        assert "has_screenshots" in result
        assert "screenshot_text" in result
