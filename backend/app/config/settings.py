"""
Configuration Settings for Healthcare Web Application

This module handles all configuration settings including API keys,
environment variables, and application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings using Pydantic for validation and type checking.
    Settings can be overridden using environment variables.
    """
    
    # Application settings
    app_name: str = "Healthcare Web Application"
    debug: bool = False
    environment: str = "development"
    
    # Server configuration
    host: str = "127.0.0.1"
    port: int = 8000
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000"]
    
    # Deepgram API configuration
    deepgram_api_key: Optional[str] = None
    
    # Google Gemini API configuration  
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    
    # Deepgram STT configuration
    deepgram_model: str = "nova-2"  # Latest Deepgram model
    deepgram_language: str = "en-US"
    deepgram_punctuation: bool = True
    deepgram_diarization: bool = False  # Speaker separation
    
    # Deepgram TTS configuration
    deepgram_tts_model: str = "aura-asteria-en"  # High-quality voice
    deepgram_tts_encoding: str = "linear16"
    
    # Audio processing settings
    max_audio_file_size: int = 25 * 1024 * 1024  # 25MB limit
    supported_audio_formats: list = ["wav", "mp3", "m4a", "ogg", "webm", "flac"]
    
    # Real-time audio settings for Deepgram
    sample_rate: int = 16000  # 16kHz for optimal STT quality
    channels: int = 1  # Mono audio
    encoding: str = "linear16"
    
    # Multilingual support (Deepgram supported languages)
    supported_languages: dict = {
        "en-US": "English (US)",
        "en-GB": "English (UK)", 
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian", 
        "pt": "Portuguese",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "nl": "Dutch",
        "hi": "Hindi",
        "ru": "Russian"
    }
    
    class Config:
        """
        Pydantic configuration class
        Allows loading settings from environment variables
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create a global settings instance
settings = Settings()

def get_settings() -> Settings:
    """
    Dependency function to get settings instance.
    Can be used with FastAPI's dependency injection system.
    """
    return settings
