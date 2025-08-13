"""
Medical Text Enhancement API Routes

This module handles medical text enhancement using Google Gemini,
including correction, explanation, and rephrasing of medical transcriptions.
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..services import GeminiMedicalService
from ..models.schemas import (
    EnhancementRequest,
    EnhancementResponse,
    EnhancementModesResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/enhance", tags=["Medical Enhancement"])


def get_medical_service():
    """Get medical enhancement service instance with proper error handling."""
    try:
        return GeminiMedicalService()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"Medical enhancement service unavailable: {str(e)}")


@router.post("/medical", response_model=EnhancementResponse)
async def enhance_medical_text(request: EnhancementRequest):
    """
    Enhance medical transcription text using AI.
    
    This endpoint takes transcribed medical text and enhances it by:
    - Correcting medical terminology and expanding abbreviations
    - Providing detailed explanations of medical terms and procedures
    - Rephrasing text using professional medical language
    
    The enhancement mode determines the type of processing applied.
    """
    try:
        medical_service = get_medical_service()

        # Basic validation
        if len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        result = await medical_service.enhance_medical_text(
            transcribed_text=request.text,
            enhancement_mode=request.mode,
            language=request.language
        )

        # Do NOT raise 500 for model safety blocks or content issues.
        # Return a normal response with success=false and an error message instead.
        if not result.get("success", False):
            logger.warning(f"Enhancement not successful: {result.get('error')}")
            return EnhancementResponse(**result)

        return EnhancementResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in enhance_medical_text: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "original_text": request.text,
                "enhanced_text": request.text,
                "enhancement_mode": request.mode,
                "language": request.language,
                "success": False,
                "error": "Internal server error during text enhancement"
            }
        )


@router.get("/modes", response_model=EnhancementModesResponse)
async def get_enhancement_modes():
    """
    Get the list of available enhancement modes.
    
    Returns information about the different types of medical text enhancement
    that can be performed on transcriptions.
    """
    try:
        medical_service = get_medical_service()
        modes = await medical_service.get_supported_modes()
        return EnhancementModesResponse(
            modes=modes,
            count=len(modes)
        )
    except Exception as e:
        logger.error(f"Error getting enhancement modes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving enhancement modes")


@router.get("/health")
async def enhancement_health_check():
    """
    Health check specifically for the medical enhancement service.
    
    Verifies that the Google Gemini service is properly configured and accessible.
    """
    try:
        medical_service = get_medical_service()
        test_result = await medical_service.enhance_medical_text(
            transcribed_text="Patient has elevated BP",
            enhancement_mode="correction",
            language="en"
        )
        return {
            "service": "gemini_medical",
            "status": "healthy" if test_result.get("success") else "degraded",
            "model": "gemini-pro",
            "test_enhancement_successful": test_result.get("success", False)
        }
    except Exception as e:
        logger.error(f"Medical enhancement health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "gemini_medical",
                "status": "unhealthy",
                "error": str(e)
            }
        )
