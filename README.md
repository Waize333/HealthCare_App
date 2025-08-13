# 🏥 Healthcare Translation Web App — Production-Ready

A modern, mobile-first healthcare web application for fast speech-to-text transcription, medical terminology enhancement, and text-to-speech. Built with Deepgram for accurate transcription and Google Gemini for intelligent text enhancements, this app delivers lightning-fast performance with production-grade quality.

---

## Key Features

- 🎙 Speech-to-Text (STT)
  Fast, high-confidence transcription using Deepgram Nova-2 from browser-recorded or uploaded audio files.
- 🩺 Medical Terminology Enhancement
  AI-powered correction, explanation, and rephrasing of complex medical terms — ideal for healthcare settings.
- 🔊 Text-to-Speech (TTS)
  Optional audio playback of text via Deepgram Aura voices.
- 📱 Mobile-First Design
  Fully responsive UI optimized for mobile and desktop, with dual light and dark themes for better accessibility.
- 🖌 Modern UI & UX
  Clean, minimal design with subtle animations, including a recording pulse effect while capturing audio.
- ⚡ Ultra-Fast Performance
  Vite + React frontend and FastAPI backend, optimized for speed and production deployment.
- 🛠 Three Enhancement Modes

  1. Correction — Fix transcription errors
  2. Explanation — Simplify medical jargon
  3. Rephrase — Improve clarity while preserving meaning
- 📊 Transcription Confidence
  Displays accuracy level for each saved transcription.

---

## Technology Stack

### Backend — FastAPI

- Speech-to-Text: Deepgram Nova-2 (prerecorded API)
- Text Enhancements: Google Gemini 2.5 Flash
- TTS (optional): Deepgram Aura
- CORS configured for local development

### Frontend — React + Vite

- Framework: React 19 + Vite
- UI: Tailwind CSS with theme variables (light/dark)
- Audio: MediaRecorder API + HTML5 Audio
- HTTP Client: Axios

---

## 📂 Project Structure

```
healthcare_webApp/
├── backend/          # FastAPI backend
├── frontend/         # React + Vite frontend
└── README.md         # Project documentation
```

---

## Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-repo/healthcare-webapp.git
cd healthcare-webapp
```

### 2️⃣ Backend Setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3️⃣ Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

### 4️⃣ Environment Variables

Create `.env` files for both backend and frontend with your API keys:

```
DEEPGRAM_API_KEY=your-deepgram-key
GEMINI_API_KEY=your-gemini-key
```

---

## Notes for Production

- FastAPI backend is suitable for deployment on Railway, Render, or AWS.
- Vite frontend builds are ready for Vercel, Netlify, or any static host.
- Ensure proper CORS configuration and secure handling of API keys.

---

## Why This App Stands Out

- Product-ready — Built with a production-grade stack and clean architecture.
- Fast and Reliable — Deepgram + Gemini integration for speed and accuracy.
- Healthcare-Oriented — Focus on medical terminology and clarity.
- Beautifully Designed — Dual theme, mobile-first layout, refined interactions.

---

## License

MIT License — Free to use, modify, and distribute.

---

## 👨‍💻Contributors

- Lead Developer: You
- AI Enhancement Models: Deepgram & Google Gemini 2.5 Flash
- UI/UX Inspiration: Modern healthcare systems and accessibility-first principles.

---

If you’d like, we can add GitHub badges and a screenshots section to enhance the README’s presentation.
