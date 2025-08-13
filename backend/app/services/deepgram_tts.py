"""
Deepgram Text-to-Speech Service

This service handles text-to-speech conversion using Deepgram's Aura models.
It provides high-quality voice synthesis with multiple voice options.
"""

import logging
from typing import Optional, Dict, Any, List
from io import BytesIO

from deepgram import (
    DeepgramClient,
    SpeakOptions
)

from ..config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DeepgramTTSService:
    """
    Service for converting text to speech using Deepgram's Aura TTS models.
    
    Features:
    - High-quality voice synthesis
    - Multiple voice models and languages
    - Customizable audio encoding
    - Real-time streaming capability
    """
    
    def __init__(self):
        """Initialize the Deepgram client with API key from settings."""
        if not settings.deepgram_api_key:
            raise ValueError("Deepgram API key is required. Set DEEPGRAM_API_KEY in environment.")
        
        self.client = DeepgramClient(settings.deepgram_api_key)
        
        # Available voice models with their characteristics
        self.available_voices = {
            "aura-asteria-en": {"language": "en", "gender": "female", "description": "Warm, conversational"},
            "aura-luna-en": {"language": "en", "gender": "female", "description": "Polite, younger"},
            "aura-stella-en": {"language": "en", "gender": "female", "description": "Friendly, customer service"},
            "aura-athena-en": {"language": "en", "gender": "female", "description": "Professional, confident"},
            "aura-hera-en": {"language": "en", "gender": "female", "description": "Business, authoritative"},
            "aura-orion-en": {"language": "en", "gender": "male", "description": "Conversational, approachable"},
            "aura-arcas-en": {"language": "en", "gender": "male", "description": "Calm, natural"},
            "aura-perseus-en": {"language": "en", "gender": "male", "description": "Professional, confident"},
            "aura-angus-en": {"language": "en", "gender": "male", "description": "Narrative, storytelling"},
            "aura-orpheus-en": {"language": "en", "gender": "male", "description": "Confident, booming"},
            "aura-helios-en": {"language": "en", "gender": "male", "description": "Upbeat, energetic"}
        }
        
        logger.info("Deepgram TTS service initialized")
    
    async def synthesize_speech(
        self,
        text: str,
        voice_model: str = None,
        encoding: str = None,
        sample_rate: int = None
    ) -> Dict[str, Any]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            voice_model: Voice model to use (defaults to settings default)
            encoding: Audio encoding format (linear16, mp3, etc.)
            sample_rate: Audio sample rate in Hz
            
        Returns:
            Dictionary containing audio data and metadata
        """
        try:
            # Use default values if not specified
            if voice_model is None:
                voice_model = settings.deepgram_tts_model
            if encoding is None:
                encoding = settings.deepgram_tts_encoding
            if sample_rate is None:
                sample_rate = settings.sample_rate
            
            # Validate voice model
            if voice_model not in self.available_voices:
                logger.warning(f"Voice model {voice_model} not in available list, using anyway")
            
            # Validate text length (Deepgram has limits)
            if len(text) > 2000:  # Conservative limit
                logger.warning(f"Text length ({len(text)}) may exceed TTS limits")
            
            # Configure TTS options
            options = SpeakOptions(
                model=voice_model,
                encoding=encoding,
                sample_rate=sample_rate
            )
            
            logger.info(f"Starting TTS synthesis with model: {voice_model}")
            
            # Generate speech
            response = self.client.speak.v("1").stream_raw(
                {"text": text},
                options
            )
            
            # Read the audio data
            audio_data = b""
            for chunk in response.iter_content():
                audio_data += chunk
            
            # Create result with metadata
            result = {
                "audio_data": audio_data,
                "audio_length": len(audio_data),
                "voice_model": voice_model,
                "encoding": encoding,
                "sample_rate": sample_rate,
                "text_length": len(text),
                "success": True,
                "metadata": {
                    "voice_info": self.available_voices.get(voice_model, {}),
                    "content_type": self._get_content_type(encoding)
                }
            }
            
            logger.info("TTS synthesis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during TTS synthesis: {str(e)}")
            return {
                "audio_data": None,
                "audio_length": 0,
                "voice_model": voice_model,
                "encoding": encoding,
                "sample_rate": sample_rate,
                "text_length": len(text),
                "success": False,
                "error": str(e)
            }
    
    def _get_content_type(self, encoding: str) -> str:
        """
        Get the appropriate MIME type for the audio encoding.
        
        Args:
            encoding: Audio encoding format
            
        Returns:
            MIME type string
        """
        encoding_types = {
            "linear16": "audio/wav",
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac"
        }
        return encoding_types.get(encoding, "audio/wav")
    
    async def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the list of available voice models with their characteristics.
        
        Returns:
            Dictionary of voice models and their metadata
        """
        return self.available_voices
    
    def get_recommended_voice(self, language: str = "en", gender: str = None) -> str:
        """
        Get a recommended voice model based on language and gender preferences.
        
        Args:
            language: Language code (e.g., 'en', 'es')
            gender: Preferred gender ('male', 'female', or None for any)
            
        Returns:
            Recommended voice model name
        """
        # Filter voices by language
        language_voices = {
            k: v for k, v in self.available_voices.items() 
            if v.get("language") == language
        }
        
        if not language_voices:
            # Fallback to default if language not found
            return settings.deepgram_tts_model
        
        # Filter by gender if specified
        if gender:
            gender_voices = {
                k: v for k, v in language_voices.items()
                if v.get("gender") == gender
            }
            if gender_voices:
                language_voices = gender_voices
        
        # Return first available voice or default
        return next(iter(language_voices.keys())) if language_voices else settings.deepgram_tts_model
    
    def validate_text_length(self, text: str) -> bool:
        """
        Check if text length is within TTS limits.
        
        Args:
            text: Text to validate
            
        Returns:
            True if text length is acceptable, False otherwise
        """
        # Deepgram TTS typically has a limit around 2000 characters
        return len(text) <= 2000
