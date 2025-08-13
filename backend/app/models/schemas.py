"""
Pydantic Models for Healthcare Web Application

This module defines the data models used for API requests and responses.
All models use Pydantic for automatic validation and serialization.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class TranscriptionRequest(BaseModel):
    """Request model for audio transcription."""
    language: Optional[str] = Field(default="en-US", description="Language code for transcription")
    include_punctuation: bool = Field(default=True, description="Include punctuation in transcript")
    include_diarization: bool = Field(default=False, description="Separate different speakers")
    
    @validator('language')
    def validate_language(cls, v):
        # Basic validation - more thorough validation happens in the service
        if v and len(v) < 2:
            raise ValueError('Language code must be at least 2 characters')
        return v

class TranscriptionResponse(BaseModel):
    """Response model for audio transcription results."""
    transcript: str = Field(description="The transcribed text")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0-1)")
    language: str = Field(description="Detected/used language")
    duration: float = Field(ge=0.0, description="Audio duration in seconds")
    words: List[Dict[str, Any]] = Field(default=[], description="Word-level timing and confidence")
    summary: str = Field(default="", description="AI-generated summary")
    success: bool = Field(description="Whether transcription was successful")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class EnhancementRequest(BaseModel):
    """Request model for medical text enhancement."""
    text: str = Field(min_length=1, max_length=5000, description="Text to enhance")
    mode: str = Field(default="correction", description="Enhancement mode")
    language: str = Field(default="en", description="Target language")
    
    @validator('mode')
    def validate_mode(cls, v):
        allowed_modes = ['correction', 'explanation', 'rephrase']
        if v not in allowed_modes:
            raise ValueError(f'Mode must be one of: {", ".join(allowed_modes)}')
        return v

class EnhancementResponse(BaseModel):
    """Response model for medical text enhancement results."""
    original_text: str = Field(description="Original input text")
    enhanced_text: str = Field(description="Enhanced/processed text")
    enhancement_mode: str = Field(description="Mode used for enhancement")
    language: str = Field(description="Language used")
    success: bool = Field(description="Whether enhancement was successful")
    analysis: Dict[str, Any] = Field(default={}, description="Enhancement analysis")
    metadata: Dict[str, Any] = Field(default={}, description="Processing metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class TTSRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    text: str = Field(min_length=1, max_length=2000, description="Text to convert to speech")
    voice_model: Optional[str] = Field(default=None, description="Voice model to use")
    encoding: Optional[str] = Field(default=None, description="Audio encoding format")
    sample_rate: Optional[int] = Field(default=None, ge=8000, le=48000, description="Audio sample rate")
    
    @validator('text')
    def validate_text_length(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Text cannot be empty')
        return v

class TTSResponse(BaseModel):
    """Response model for text-to-speech results."""
    audio_length: int = Field(description="Audio data length in bytes")
    voice_model: str = Field(description="Voice model used")
    encoding: str = Field(description="Audio encoding format")
    sample_rate: int = Field(description="Audio sample rate")
    text_length: int = Field(description="Original text length")
    success: bool = Field(description="Whether TTS was successful")
    metadata: Dict[str, Any] = Field(default={}, description="Voice and processing metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(description="Overall API status")
    timestamp: str = Field(description="Current timestamp")
    services: Dict[str, str] = Field(description="Status of individual services")

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(description="Error type or category")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages endpoint."""
    languages: Dict[str, str] = Field(description="Mapping of language codes to names")
    count: int = Field(description="Number of supported languages")

class SupportedVoicesResponse(BaseModel):
    """Response model for supported voices endpoint."""
    voices: Dict[str, Dict[str, Any]] = Field(description="Available voice models with metadata")
    count: int = Field(description="Number of available voices")

class EnhancementModesResponse(BaseModel):
    """Response model for enhancement modes endpoint."""
    modes: List[Dict[str, str]] = Field(description="Available enhancement modes")
    count: int = Field(description="Number of available modes")
