"""
Text-to-Speech API Routes

This module handles text-to-speech conversion using Deepgram Aura models.
Supports multiple voice models and audio formats.
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse

from ..services import DeepgramTTSService
from ..models.schemas import (
    TTSRequest,
    TTSResponse,
    SupportedVoicesResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tts", tags=["Text-to-Speech"])

def get_tts_service():
    """Get TTS service instance with proper error handling."""
    try:
        return DeepgramTTSService()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"TTS service unavailable: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech audio.
    
    This endpoint takes text input and converts it to high-quality speech audio
    using Deepgram's Aura TTS models. The audio is returned as binary data
    with appropriate content headers.
    
    Supports multiple voice models and audio encoding formats.
    """
    try:
        # Get TTS service instance
        tts_service = get_tts_service()
        
        logger.info(f"Processing TTS request: text_length={len(request.text)}, voice={request.voice_model}")
        
        # Validate text length
        if not tts_service.validate_text_length(request.text):
            raise HTTPException(
                status_code=400,
                detail="Text too long. Maximum length is 2000 characters."
            )
        
        # Synthesize speech
        result = await tts_service.synthesize_speech(
            text=request.text,
            voice_model=request.voice_model,
            encoding=request.encoding,
            sample_rate=request.sample_rate
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"TTS synthesis failed: {result.get('error', 'Unknown error')}"
            )
        
        # Return audio data as binary response
        audio_data = result["audio_data"]
        content_type = result["metadata"]["content_type"]
        
        return Response(
            content=audio_data,
            media_type=content_type,
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
                "X-Audio-Length": str(result["audio_length"]),
                "X-Voice-Model": result["voice_model"],
                "X-Sample-Rate": str(result["sample_rate"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in synthesize_speech: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during speech synthesis")

@router.post("/synthesize-info", response_model=TTSResponse)
async def synthesize_speech_info(request: TTSRequest):
    """
    Get information about speech synthesis without returning audio data.
    
    This endpoint performs the same TTS processing but returns metadata
    about the synthesis instead of the actual audio data. Useful for
    testing and getting synthesis information.
    """
    try:
        # Get TTS service instance
        tts_service = get_tts_service()
        
        # Validate text length
        if not tts_service.validate_text_length(request.text):
            raise HTTPException(
                status_code=400,
                detail="Text too long. Maximum length is 2000 characters."
            )
        
        # Synthesize speech
        result = await tts_service.synthesize_speech(
            text=request.text,
            voice_model=request.voice_model,
            encoding=request.encoding,
            sample_rate=request.sample_rate
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"TTS synthesis failed: {result.get('error', 'Unknown error')}"
            )
        
        # Return metadata without audio data
        response_data = {k: v for k, v in result.items() if k != "audio_data"}
        return TTSResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in synthesize_speech_info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during speech synthesis")

@router.get("/voices", response_model=SupportedVoicesResponse)
async def get_supported_voices():
    """
    Get the list of available voice models for text-to-speech.
    
    Returns detailed information about each voice including language,
    gender, and characteristics.
    """
    try:
        tts_service = get_tts_service()
        voices = await tts_service.get_available_voices()
        return SupportedVoicesResponse(
            voices=voices,
            count=len(voices)
        )
    except Exception as e:
        logger.error(f"Error getting supported voices: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving supported voices")

@router.get("/voices/recommend/{language}")
async def get_recommended_voice(language: str, gender: str = None):
    """
    Get a recommended voice model for a specific language and optional gender.
    
    This endpoint helps clients choose an appropriate voice model based on
    language preferences and gender requirements.
    """
    try:
        tts_service = get_tts_service()
        recommended_voice = tts_service.get_recommended_voice(language, gender)
        voice_info = await tts_service.get_available_voices()
        
        return {
            "recommended_voice": recommended_voice,
            "voice_info": voice_info.get(recommended_voice, {}),
            "language": language,
            "gender_preference": gender
        }
    except Exception as e:
        logger.error(f"Error getting recommended voice: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting voice recommendation")

@router.get("/health")
async def tts_health_check():
    """
    Health check specifically for the TTS service.
    
    Verifies that the Deepgram TTS service is properly configured and accessible.
    """
    try:
        # Get TTS service instance
        tts_service = get_tts_service()
        
        # Test with simple text synthesis (info only, no audio)
        test_result = await tts_service.synthesize_speech(
            text="Test synthesis",
            voice_model=None,  # Use default
            encoding=None,
            sample_rate=None
        )
        
        voices = await tts_service.get_available_voices()
        
        return {
            "service": "deepgram_tts",
            "status": "healthy" if test_result.get("success") else "degraded",
            "available_voices_count": len(voices),
            "test_synthesis_successful": test_result.get("success", False)
        }
    except Exception as e:
        logger.error(f"TTS health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "deepgram_tts",
                "status": "unhealthy",
                "error": str(e)
            }
        )
