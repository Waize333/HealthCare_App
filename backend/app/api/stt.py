"""
Speech-to-Text API Routes

This module handles all STT-related endpoints including file upload transcription
and real-time streaming transcription.
"""

import logging
from typing import List
from io import BytesIO

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..services import DeepgramSTTService
from ..models.schemas import (
    TranscriptionRequest,
    TranscriptionResponse,
    SupportedLanguagesResponse,
    ErrorResponse
)
from ..config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stt", tags=["Speech-to-Text"])

def get_stt_service():
    """Get STT service instance with proper error handling."""
    try:
        return DeepgramSTTService()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"STT service unavailable: {str(e)}")

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio_file(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = "en-US",
    include_punctuation: bool = True,
    include_diarization: bool = False
):
    """
    Transcribe an uploaded audio file to text.
    
    This endpoint accepts audio files and returns the transcribed text along with
    confidence scores, timing information, and other metadata.
    
    Supported formats: WAV, MP3, M4A, OGG, WebM, FLAC
    """
    try:
        # Get STT service instance
        stt_service = get_stt_service()
        
        # Validate file format
        if not stt_service.validate_audio_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Supported formats: {', '.join(get_settings().supported_audio_formats)}"
            )
        
        # Check file size
        if file.size and file.size > get_settings().max_audio_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {get_settings().max_audio_file_size / (1024*1024):.1f}MB"
            )
        
        # Read audio data
        audio_data = await file.read()
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing audio file: {file.filename}, size: {len(audio_data)} bytes")
        
        # Transcribe audio
        result = await stt_service.transcribe_audio_file(
            audio_data=audio_data,
            language=language,
            include_punctuation=include_punctuation,
            include_diarization=include_diarization
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {result.get('error', 'Unknown error')}"
            )
        
        return TranscriptionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in transcribe_audio_file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during transcription")

@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """
    Get the list of supported languages for speech-to-text transcription.
    
    Returns a mapping of language codes to human-readable language names.
    """
    try:
        stt_service = get_stt_service()
        languages = await stt_service.get_supported_languages()
        return SupportedLanguagesResponse(
            languages=languages,
            count=len(languages)
        )
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving supported languages")

@router.get("/health")
async def stt_health_check():
    """
    Health check specifically for the STT service.
    
    Verifies that the Deepgram STT service is properly configured and accessible.
    """
    try:
        # Get STT service instance  
        stt_service = get_stt_service()
        
        # Basic service validation
        languages = await stt_service.get_supported_languages()
        
        return {
            "service": "deepgram_stt",
            "status": "healthy",
            "model": get_settings().deepgram_model,
            "supported_languages_count": len(languages),
            "max_file_size_mb": get_settings().max_audio_file_size / (1024*1024)
        }
    except Exception as e:
        logger.error(f"STT health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "deepgram_stt",
                "status": "unhealthy",
                "error": str(e)
            }
        )
