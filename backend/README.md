# 🏥 Healthcare Translation Web App — Backend (FastAPI)

FastAPI backend that powers speech-to-text transcription, medical text enhancement, and text-to-speech for the Healthcare Translation Web App.

## Features

- REST API with FastAPI
- Speech-to-Text via Deepgram Nova-2 (prerecorded/file uploads)
- Medical Text Enhancement via Google Gemini 2.5 Flash
- Optional Text-to-Speech via Deepgram Aura
- Multilingual support
- CORS enabled for the React frontend

## Setup

1. Install Python dependencies

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Configure environment variables

   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and settings
   ```

3. Run the development server

   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application entry point
│   ├── api/              # API route definitions
│   ├── services/         # Business logic (STT, LLM, TTS)
│   ├── models/           # Pydantic data models
│   └── config/           # Configuration and settings
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## Environment Variables

- DEEPGRAM_API_KEY: Deepgram API key
- GEMINI_API_KEY: Google Gemini API key
- DEEPGRAM_MODEL: STT model (e.g., nova-2)
- DEEPGRAM_TTS_MODEL: TTS voice model (optional)
- GEMINI_MODEL: Model for text enhancement
- DEBUG: Enable debug mode

## Notes

- Auto-reload is enabled in development
- CORS is configured for the Vite React frontend
- Endpoints include error handling and logging
- Follows RESTful conventions
