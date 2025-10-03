"""
Tests for the transcripts plugin.

This module tests all functions in the transcripts plugin tasks.
"""

from unittest.mock import Mock, patch

import pytest

from marketing_project.core.models import AppContext, TranscriptContext
from marketing_project.plugins.transcripts.tasks import (
    analyze_transcript_type,
    enhance_transcript_with_ocr,
    extract_transcript_metadata,
    route_transcript_processing,
    validate_transcript_structure,
)


class TestAnalyzeTranscriptType:
    """Test the analyze_transcript_type function."""

    def test_analyze_podcast_transcript(self, sample_transcript):
        """Test analyzing podcast transcript type."""
        sample_transcript.transcript_type = "podcast"
        result = analyze_transcript_type(sample_transcript)
        assert result == "podcast"

    def test_analyze_video_transcript(self, sample_transcript):
        """Test analyzing video transcript type."""
        sample_transcript.transcript_type = "video"
        result = analyze_transcript_type(sample_transcript)
        assert result == "video"

    def test_analyze_youtube_transcript(self, sample_transcript):
        """Test analyzing YouTube transcript type."""
        sample_transcript.transcript_type = "youtube"
        result = analyze_transcript_type(sample_transcript)
        assert result == "video"

    def test_analyze_meeting_transcript(self, sample_transcript):
        """Test analyzing meeting transcript type."""
        sample_transcript.transcript_type = "meeting"
        result = analyze_transcript_type(sample_transcript)
        assert result == "meeting"

    def test_analyze_call_transcript(self, sample_transcript):
        """Test analyzing call transcript type."""
        sample_transcript.transcript_type = "call"
        result = analyze_transcript_type(sample_transcript)
        assert result == "meeting"

    def test_analyze_interview_transcript(self, sample_transcript):
        """Test analyzing interview transcript type."""
        sample_transcript.transcript_type = "interview"
        result = analyze_transcript_type(sample_transcript)
        assert result == "interview"

    def test_analyze_general_transcript(self, sample_transcript):
        """Test analyzing general transcript type."""
        sample_transcript.transcript_type = "general"
        result = analyze_transcript_type(sample_transcript)
        assert result == "general"

    def test_analyze_transcript_type_case_insensitive(self, sample_transcript):
        """Test that transcript type analysis is case insensitive."""
        sample_transcript.transcript_type = "PODCAST"
        result = analyze_transcript_type(sample_transcript)
        assert result == "podcast"


class TestExtractTranscriptMetadata:
    """Test the extract_transcript_metadata function."""

    @patch("marketing_project.plugins.transcripts.tasks.parse_transcript")
    def test_extract_transcript_metadata(self, mock_parse, sample_transcript):
        """Test extracting metadata from transcript."""
        mock_parse.return_value = {
            "speakers": ["Speaker A", "Speaker B"],
            "estimated_duration": "45:30",
            "timestamps": {"00:00": "Introduction", "20:00": "Main topic"},
            "cleaned_content": "Cleaned transcript content",
        }

        result = extract_transcript_metadata(sample_transcript)

        assert isinstance(result, dict)
        assert result["content_type"] == "transcript"
        assert result["id"] == sample_transcript.id
        assert result["title"] == sample_transcript.title
        assert result["speakers"] == sample_transcript.speakers
        assert result["duration"] == sample_transcript.duration
        assert result["transcript_type"] == sample_transcript.transcript_type
        assert result["has_timestamps"] is True
        assert result["speaker_count"] == len(sample_transcript.speakers)
        assert result["word_count"] > 0
        assert "parsed_speakers" in result
        assert "parsed_timestamps" in result
        assert "cleaned_content" in result
        assert "timestamp_count" in result

    @patch("marketing_project.plugins.transcripts.tasks.parse_transcript")
    def test_extract_transcript_metadata_with_parsed_data(
        self, mock_parse, sample_transcript
    ):
        """Test extracting metadata with parsed data overriding original."""
        mock_parse.return_value = {
            "speakers": ["Parsed Speaker 1", "Parsed Speaker 2"],
            "estimated_duration": "60:00",
            "timestamps": {"00:00": "Start", "30:00": "Middle"},
            "cleaned_content": "Parsed cleaned content",
        }

        # Set original values to None to test fallback
        sample_transcript.speakers = None
        sample_transcript.duration = None
        sample_transcript.timestamps = None

        result = extract_transcript_metadata(sample_transcript)

        assert result["speakers"] == ["Parsed Speaker 1", "Parsed Speaker 2"]
        assert result["duration"] == "60:00"
        assert result["has_timestamps"] is True
        assert result["speaker_count"] == 2
        assert result["timestamp_count"] == 2

    @patch("marketing_project.plugins.transcripts.tasks.parse_transcript")
    def test_extract_transcript_metadata_no_timestamps(
        self, mock_parse, sample_transcript
    ):
        """Test extracting metadata when no timestamps are present."""
        mock_parse.return_value = {
            "speakers": ["Speaker 1"],
            "estimated_duration": "30:00",
            "timestamps": {},
            "cleaned_content": "Content without timestamps",
        }

        sample_transcript.timestamps = None

        result = extract_transcript_metadata(sample_transcript)

        assert result["has_timestamps"] is False
        assert "timestamp_count" not in result


class TestValidateTranscriptStructure:
    """Test the validate_transcript_structure function."""

    def test_validate_valid_transcript(self, sample_transcript):
        """Test validating valid transcript."""
        result = validate_transcript_structure(sample_transcript)
        assert result is True

    def test_validate_transcript_missing_id(self, sample_transcript):
        """Test validating transcript with missing ID."""
        sample_transcript.id = None
        result = validate_transcript_structure(sample_transcript)
        assert result is False

    def test_validate_transcript_missing_title(self, sample_transcript):
        """Test validating transcript with missing title."""
        sample_transcript.title = None
        result = validate_transcript_structure(sample_transcript)
        assert result is False

    def test_validate_transcript_missing_content(self, sample_transcript):
        """Test validating transcript with missing content."""
        sample_transcript.content = None
        result = validate_transcript_structure(sample_transcript)
        assert result is False

    def test_validate_transcript_missing_snippet(self, sample_transcript):
        """Test validating transcript with missing snippet."""
        sample_transcript.snippet = None
        result = validate_transcript_structure(sample_transcript)
        assert result is False

    def test_validate_transcript_missing_transcript_type(self, sample_transcript):
        """Test validating transcript with missing transcript type."""
        sample_transcript.transcript_type = None
        result = validate_transcript_structure(sample_transcript)
        assert result is False

    def test_validate_transcript_no_speakers_warning(self, sample_transcript):
        """Test validating transcript with no speakers (should warn but not fail)."""
        sample_transcript.speakers = []
        result = validate_transcript_structure(sample_transcript)
        assert result is True  # Should still be valid, just with warning


class TestEnhanceTranscriptWithOCR:
    """Test the enhance_transcript_with_ocr function."""

    @patch("marketing_project.plugins.transcripts.tasks.extract_images_from_content")
    @patch("marketing_project.plugins.transcripts.tasks.enhance_content_with_ocr")
    def test_enhance_transcript_with_ocr_no_images(
        self, mock_enhance, mock_extract, sample_transcript
    ):
        """Test enhancing transcript with OCR when no images provided."""
        mock_extract.return_value = []
        mock_enhance.return_value = {
            "enhanced_content": "Enhanced transcript content",
            "ocr_text": "OCR text from images",
            "has_visual_content": False,
            "image_count": 0,
            "visual_transcript": "Visual transcript content",
        }

        result = enhance_transcript_with_ocr(sample_transcript)

        assert isinstance(result, dict)
        assert "original_transcript" in result
        assert "enhanced_content" in result
        assert "ocr_text" in result
        assert "has_visual_content" in result
        assert "image_count" in result
        assert "visual_transcript" in result

        assert result["original_transcript"] == sample_transcript
        assert result["has_visual_content"] is False
        assert result["image_count"] == 0

    @patch("marketing_project.plugins.transcripts.tasks.enhance_content_with_ocr")
    def test_enhance_transcript_with_ocr_with_images(
        self, mock_enhance, sample_transcript
    ):
        """Test enhancing transcript with OCR when images are provided."""
        image_urls = [
            "https://example.com/slide1.jpg",
            "https://example.com/slide2.jpg",
        ]
        mock_enhance.return_value = {
            "enhanced_content": "Enhanced transcript with visual content",
            "ocr_text": "OCR text from slides",
            "has_visual_content": True,
            "image_count": 2,
            "visual_transcript": "Visual transcript with slides",
        }

        result = enhance_transcript_with_ocr(sample_transcript, image_urls)

        assert result["has_visual_content"] is True
        assert result["image_count"] == 2

        # Verify OCR service was called with correct parameters
        mock_enhance.assert_called_once_with(
            sample_transcript.content, "transcript", image_urls=image_urls
        )


class TestRouteTranscriptProcessing:
    """Test the route_transcript_processing function."""

    def test_route_podcast_transcript(
        self, sample_app_context_transcript, sample_available_agents
    ):
        """Test routing podcast transcript to appropriate agent."""
        sample_app_context_transcript.content.transcript_type = "podcast"

        result = route_transcript_processing(
            sample_app_context_transcript, sample_available_agents
        )

        assert "Successfully routed podcast transcript to transcripts_agent" in result

    def test_route_video_transcript(
        self, sample_app_context_transcript, sample_available_agents
    ):
        """Test routing video transcript to appropriate agent."""
        sample_app_context_transcript.content.transcript_type = "video"

        result = route_transcript_processing(
            sample_app_context_transcript, sample_available_agents
        )

        assert "Successfully routed video transcript to transcripts_agent" in result

    def test_route_meeting_transcript(
        self, sample_app_context_transcript, sample_available_agents
    ):
        """Test routing meeting transcript to appropriate agent."""
        sample_app_context_transcript.content.transcript_type = "meeting"

        result = route_transcript_processing(
            sample_app_context_transcript, sample_available_agents
        )

        assert "Successfully routed meeting transcript to transcripts_agent" in result

    def test_route_interview_transcript(
        self, sample_app_context_transcript, sample_available_agents
    ):
        """Test routing interview transcript to appropriate agent."""
        sample_app_context_transcript.content.transcript_type = "interview"

        result = route_transcript_processing(
            sample_app_context_transcript, sample_available_agents
        )

        assert "Successfully routed interview transcript to transcripts_agent" in result

    def test_route_general_transcript(
        self, sample_app_context_transcript, sample_available_agents
    ):
        """Test routing general transcript to general agent."""
        sample_app_context_transcript.content.transcript_type = "general"

        result = route_transcript_processing(
            sample_app_context_transcript, sample_available_agents
        )

        assert "Successfully routed general transcript to transcripts_agent" in result

    def test_route_transcript_no_agent_available(self, sample_app_context_transcript):
        """Test routing when no agent is available."""
        available_agents = {}  # Empty agents dictionary

        result = route_transcript_processing(
            sample_app_context_transcript, available_agents
        )

        assert (
            "No specialized agent for podcast transcript, using general processing"
            in result
        )

    def test_route_transcript_wrong_content_type(
        self, sample_app_context_blog, sample_available_agents
    ):
        """Test routing with wrong content type."""
        result = route_transcript_processing(
            sample_app_context_blog, sample_available_agents
        )

        assert result == "Error: Content is not a transcript"


class TestIntegration:
    """Test integration between functions."""

    @patch("marketing_project.plugins.transcripts.tasks.parse_transcript")
    @patch("marketing_project.plugins.transcripts.tasks.extract_images_from_content")
    @patch("marketing_project.plugins.transcripts.tasks.enhance_content_with_ocr")
    def test_full_transcript_processing_workflow(
        self,
        mock_enhance,
        mock_extract,
        mock_parse,
        sample_transcript,
        sample_available_agents,
    ):
        """Test the full transcript processing workflow."""
        # Setup mocks
        mock_parse.return_value = {
            "speakers": ["Speaker A", "Speaker B"],
            "estimated_duration": "45:30",
            "timestamps": {"00:00": "Introduction", "20:00": "Main topic"},
            "cleaned_content": "Cleaned transcript content",
        }
        mock_extract.return_value = ["https://example.com/slide.jpg"]
        mock_enhance.return_value = {
            "enhanced_content": "Enhanced transcript",
            "ocr_text": "OCR text",
            "has_visual_content": True,
            "image_count": 1,
            "visual_transcript": "Visual transcript",
        }

        # Step 1: Analyze transcript type
        transcript_type = analyze_transcript_type(sample_transcript)
        assert transcript_type in [
            "podcast",
            "video",
            "meeting",
            "interview",
            "general",
        ]

        # Step 2: Extract metadata
        metadata = extract_transcript_metadata(sample_transcript)
        assert metadata["content_type"] == "transcript"
        assert "speakers" in metadata
        assert "duration" in metadata

        # Step 3: Validate structure
        is_valid = validate_transcript_structure(sample_transcript)
        assert is_valid is True

        # Step 4: Enhance with OCR
        enhanced_data = enhance_transcript_with_ocr(sample_transcript)
        assert "enhanced_content" in enhanced_data
        assert "ocr_text" in enhanced_data

        # Step 5: Route to appropriate agent
        app_context = AppContext(
            content=sample_transcript,
            labels={"category": "technology"},
            content_type="transcript",
        )
        routing_result = route_transcript_processing(
            app_context, sample_available_agents
        )
        assert (
            "Successfully routed" in routing_result
            or "No specialized agent" in routing_result
        )


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_analyze_transcript_type_empty_type(self):
        """Test analyzing transcript with empty type."""
        transcript = TranscriptContext(
            id="test-1",
            title="Test Transcript",
            content="Some content",
            snippet="Some snippet",
            transcript_type="",
        )

        result = analyze_transcript_type(transcript)
        assert result == "general"

    def test_analyze_transcript_type_none_type(self):
        """Test analyzing transcript with empty type."""
        transcript = TranscriptContext(
            id="test-1",
            title="Test Transcript",
            content="Some content",
            snippet="Some snippet",
            transcript_type="",
        )

        result = analyze_transcript_type(transcript)
        assert result == "general"

    def test_extract_metadata_with_minimal_transcript(self):
        """Test extracting metadata from minimal transcript."""
        transcript = TranscriptContext(
            id="test-1",
            title="Minimal Transcript",
            content="Minimal content",
            snippet="Minimal snippet",
            transcript_type="podcast",
        )

        with patch(
            "marketing_project.plugins.transcripts.tasks.parse_transcript"
        ) as mock_parse:
            mock_parse.return_value = {
                "speakers": [],
                "estimated_duration": None,
                "timestamps": {},
                "cleaned_content": "Minimal content",
            }

            result = extract_transcript_metadata(transcript)

            assert result["content_type"] == "transcript"
            assert result["id"] == "test-1"
            assert result["title"] == "Minimal Transcript"
            assert result["speaker_count"] == 0
            assert result["has_timestamps"] is False
            assert "timestamp_count" not in result

    def test_validate_transcript_structure_minimal_valid(self):
        """Test validating minimal but valid transcript structure."""
        transcript = TranscriptContext(
            id="test-1",
            title="Test",
            content="Content",
            snippet="Snippet",
            transcript_type="podcast",
        )

        result = validate_transcript_structure(transcript)
        assert result is True
