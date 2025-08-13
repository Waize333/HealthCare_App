"""
Real-time WebSocket API Routes

This module handles real-time audio streaming and transcription using WebSockets.
Supports live audio streaming from the frontend for real-time transcription.
- Client may send audio either as base64 in JSON (legacy) or as raw PCM16 binary frames.
"""

import asyncio
import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from ..services import DeepgramSTTService
from ..config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/realtime", tags=["Real-time Audio"])

# Keep track of active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Helper: wrap raw PCM16LE bytes into a minimal WAV file (mono)
def _pcm16le_to_wav(pcm: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    import struct
    bits_per_sample = 16
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm)
    riff_chunk_size = 36 + data_size

    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', riff_chunk_size, b'WAVE',
        b'fmt ', 16, 1, channels, sample_rate, byte_rate, block_align, bits_per_sample,
        b'data', data_size
    )
    return header + pcm

@router.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    Real-time audio transcription via WebSocket.
    
    Protocol:
    - Client sends TEXT JSON frames for control/config:
        {"type": "config", "language": "en-US", "sample_rate": 16000, "encoding": "linear16"}
        {"type": "ping"}
    - Client sends AUDIO as EITHER:
        a) TEXT JSON frames (legacy): {"type": "audio", "data": base64_audio_chunk}
        b) BINARY frames: raw PCM16 little-endian bytes at the configured sample_rate
    - Server sends TEXT JSON frames:
        {"type": "connected" | "config_updated" | "transcript" | "error", ...}
    """
    await websocket.accept()
    connection_id = f"conn_{id(websocket)}"
    active_connections[connection_id] = websocket

    logger.info(f"WebSocket connection established: {connection_id}")

    # Configuration for this connection
    config: Dict[str, Any] = {
        "language": "en-US",
        "sample_rate": 16000,
        "encoding": "linear16",
        "model": get_settings().deepgram_model,
    }

    try:
        # Send welcome message
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({
                "type": "connected",
                "message": "Real-time transcription ready",
                "config": config,
            })

        # Audio buffer for accumulating chunks
        audio_buffer = b""
        buffer_duration_ms = 2000  # Process every 2 seconds of audio
        bytes_per_second = config["sample_rate"] * 2  # 16-bit audio = 2 bytes per sample
        buffer_size = int(bytes_per_second * buffer_duration_ms / 1000)

        while websocket.client_state == WebSocketState.CONNECTED:
            try:
                # Receive either TEXT (json) or BINARY (bytes)
                message = await asyncio.wait_for(websocket.receive(), timeout=30.0)

                # WebSocket close event from client
                if message.get("type") == "websocket.disconnect":
                    logger.info(f"Client requested disconnect: {connection_id}")
                    break

                # Handle TEXT frames
                if message.get("text") is not None:
                    try:
                        data = json.loads(message["text"]) if isinstance(message["text"], str) else {}
                    except json.JSONDecodeError:
                        logger.warning("Received non-JSON text frame")
                        if websocket.client_state == WebSocketState.CONNECTED:
                            await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                        continue

                    message_type = data.get("type")

                    if message_type == "config":
                        # Update configuration (allow encoding override)
                        config.update({
                            "language": data.get("language", config["language"]),
                            "sample_rate": data.get("sample_rate", config["sample_rate"]),
                            "encoding": data.get("encoding", config.get("encoding", "linear16")),
                        })
                        logger.info(f"Updated config for {connection_id}: {config}")

                        # Recalculate buffer_size if sample_rate changed
                        bytes_per_second = config["sample_rate"] * 2
                        buffer_size = int(bytes_per_second * buffer_duration_ms / 1000)

                        if websocket.client_state == WebSocketState.CONNECTED:
                            await websocket.send_json({"type": "config_updated", "config": config})

                    elif message_type == "audio":
                        # Legacy base64 audio in JSON
                        import base64
                        try:
                            audio_chunk = base64.b64decode(data.get("data", ""))
                            audio_buffer += audio_chunk
                            logger.debug(f"{connection_id}: received base64 audio chunk, buffer={len(audio_buffer)} bytes")
                        except Exception as e:
                            logger.error(f"Error decoding base64 audio data: {str(e)}")
                            if websocket.client_state == WebSocketState.CONNECTED:
                                await websocket.send_json({"type": "error", "message": "Invalid audio data format"})
                            continue

                    elif message_type == "ping":
                        if websocket.client_state == WebSocketState.CONNECTED:
                            await websocket.send_json({"type": "pong"})

                    else:
                        logger.warning(f"Unknown message type: {message_type}")
                        if websocket.client_state == WebSocketState.CONNECTED:
                            await websocket.send_json({"type": "error", "message": f"Unknown message type: {message_type}"})

                # Handle BINARY frames (raw PCM16)
                elif message.get("bytes") is not None:
                    audio_chunk_bytes: bytes = message["bytes"] or b""
                    if not audio_chunk_bytes:
                        continue
                    audio_buffer += audio_chunk_bytes
                    logger.debug(f"{connection_id}: received binary audio chunk, buffer={len(audio_buffer)} bytes")

                # Process when buffer is full enough
                if len(audio_buffer) >= buffer_size:
                    chunk_to_process = audio_buffer[:buffer_size]
                    audio_buffer = audio_buffer[buffer_size:]

                    try:
                        stt_service = DeepgramSTTService()
                        # If client sends raw PCM16 (binary frames), wrap as WAV for Deepgram prerecorded API
                        wav_bytes = _pcm16le_to_wav(
                            chunk_to_process,
                            sample_rate=config.get("sample_rate", 16000),
                            channels=1,
                        )
                        result = await stt_service.transcribe_audio_file(
                            audio_data=wav_bytes,
                            language=config["language"],
                            include_punctuation=True,
                            include_diarization=False,
                        )

                        if result.get("success") and result.get("transcript") and websocket.client_state == WebSocketState.CONNECTED:
                            await websocket.send_json({
                                "type": "transcript",
                                "text": result["transcript"],
                                "confidence": result.get("confidence", 0.0),
                                "is_final": True,
                                "timestamp": result.get("metadata", {}).get("timestamp"),
                            })
                        else:
                            logger.warning(f"{connection_id}: transcription unsuccessful or empty transcript: {result}")

                    except Exception as e:
                        logger.error(f"Error processing audio chunk: {str(e)}")
                        if websocket.client_state == WebSocketState.CONNECTED:
                            await websocket.send_json({"type": "error", "message": f"Transcription error: {str(e)}"})
                        # continue loop

            except asyncio.TimeoutError:
                logger.info(f"WebSocket timeout for {connection_id}")
                break
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected during receive: {connection_id}")
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({"type": "error", "message": f"Processing error: {str(e)}"})
                # continue loop on non-fatal errors
                continue

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Clean up connection
        if connection_id in active_connections:
            del active_connections[connection_id]
        logger.info(f"WebSocket connection closed: {connection_id}")

@router.get("/connections")
async def get_active_connections():
    """
    Get information about active WebSocket connections.
    """
    return {
        "active_connections": len(active_connections),
        "connection_ids": list(active_connections.keys()),
        "server_status": "operational",
    }

@router.get("/health")
async def realtime_health_check():
    """
    Health check for the real-time transcription service.
    """
    try:
        return {
            "service": "realtime_transcription",
            "status": "healthy",
            "active_connections": len(active_connections),
            "websocket_endpoint": "/api/realtime/transcribe",
            "supported_audio_formats": ["linear16", "wav", "webm"],
            "recommended_sample_rate": 16000,
        }
    except Exception as e:
        logger.error(f"Real-time health check failed: {str(e)}")
        return {"service": "realtime_transcription", "status": "unhealthy", "error": str(e)}
