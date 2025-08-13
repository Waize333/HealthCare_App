# Frontend build
FROM node:18-slim AS fe
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Backend runtime
FROM python:3.11-slim AS be
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# System deps (if you need ffmpeg/sox/etc, add here)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
# Python deps
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
# Copy backend
COPY backend ./backend
# Copy built frontend
COPY --from=fe /app/frontend/dist ./frontend_dist

# Launch FastAPI on HF’s provided $PORT
ENV PORT=7860
EXPOSE 7860
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}