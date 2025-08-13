"""
Deepgram Speech-to-Text Service

This service handles audio transcription using Deepgram's Nova-2 model.
It supports both real-time streaming and file-based transcription.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from io import BytesIO

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
    LiveTranscriptionEvents,
    LiveOptions
)

from ..config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DeepgramSTTService:
    """
    Service for handling speech-to-text transcription using Deepgram API.
    
    Features:
    - File-based transcription for uploaded audio files
    - Real-time streaming transcription (for future implementation)
    - Multiple language support
    - Punctuation and formatting
    """
    
    def __init__(self):
        """Initialize the Deepgram client with API key from settings."""
        if not settings.deepgram_api_key:
            raise ValueError("Deepgram API key is required. Set DEEPGRAM_API_KEY in environment.")
        
        self.client = DeepgramClient(settings.deepgram_api_key)
        logger.info("Deepgram STT service initialized")
    
    async def transcribe_audio_file(
        self, 
        audio_data: bytes, 
        language: str = None,
        include_punctuation: bool = True,
        include_diarization: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_data: Raw audio file bytes
            language: Language code (e.g., 'en-US', 'es', 'fr'). Defaults to settings default.
            include_punctuation: Whether to include punctuation in transcription
            include_diarization: Whether to separate different speakers
            
        Returns:
            Dictionary containing transcription results with metadata
        """
        try:
            # Use default language if not specified
            if language is None:
                language = settings.deepgram_language
            
            # Validate language is supported
            if language not in settings.supported_languages:
                logger.warning(f"Language {language} not in supported list, using anyway")
            
            # Create file source from audio bytes
            buffer_data = {"buffer": audio_data}
            
            # Configure transcription options
            options = PrerecordedOptions(
                model=settings.deepgram_model,
                language=language,
                punctuate=include_punctuation,
                diarize=include_diarization,
                smart_format=True,  # Automatically format numbers, dates, etc.
                utterances=True,    # Include timing information
                paragraphs=True,    # Break into paragraphs
                summarize="v2"      # Include AI summary
            )
            
            # Perform transcription
            logger.info(f"Starting transcription with model: {settings.deepgram_model}, language: {language}")
            response = self.client.listen.prerecorded.v("1").transcribe_file(
                buffer_data, options
            )
            
            # Extract and format results
            result = self._format_transcription_result(response)
            
            logger.info("Transcription completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _format_transcription_result(self, response) -> Dict[str, Any]:
        """
        Format the Deepgram response into a standardized result structure.
        
        Args:
            response: Raw Deepgram API response
            
        Returns:
            Formatted transcription result
        """
        try:
            # Extract the main transcript
            transcript = ""
            confidence = 0.0
            words = []
            
            if response.results and response.results.channels:
                channel = response.results.channels[0]
                if channel.alternatives:
                    alternative = channel.alternatives[0]
                    transcript = alternative.transcript
                    confidence = alternative.confidence
                    
                    # Extract word-level timing and confidence if available
                    if hasattr(alternative, 'words') and alternative.words:
                        words = [
                            {
                                "word": word.word,
                                "start": word.start,
                                "end": word.end,
                                "confidence": word.confidence
                            }
                            for word in alternative.words
                        ]
            
            # Extract summary if available
            summary = ""
            if hasattr(response.results, 'summary') and response.results.summary:
                summary = response.results.summary.short
            
            # Calculate duration
            duration = 0.0
            if response.metadata:
                duration = response.metadata.duration
            
            # Get language from metadata safely
            language = "unknown"
            timestamp = None
            if hasattr(response, 'metadata') and response.metadata:
                # Try different possible metadata structures
                if hasattr(response.metadata, 'model_info') and response.metadata.model_info:
                    if hasattr(response.metadata.model_info, 'language'):
                        language = response.metadata.model_info.language
                # Get timestamp if available
                if hasattr(response.metadata, 'created'):
                    timestamp = response.metadata.created
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "language": language,
                "duration": duration,
                "words": words,
                "summary": summary,
                "success": True,
                "metadata": {
                    "model": settings.deepgram_model,
                    "timestamp": timestamp
                }
            }
            
        except Exception as e:
            logger.error(f"Error formatting transcription result: {str(e)}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": "unknown",
                "duration": 0.0,
                "words": [],
                "summary": "",
                "success": False,
                "error": str(e)
            }
    
    async def get_supported_languages(self) -> Dict[str, str]:
        """
        Get the list of supported languages for transcription.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return settings.supported_languages
    
    def validate_audio_format(self, filename: str) -> bool:
        """
        Check if the audio file format is supported.
        
        Args:
            filename: Name of the audio file
            
        Returns:
            True if format is supported, False otherwise
        """
        extension = filename.lower().split('.')[-1]
        return extension in settings.supported_audio_formats
