FROM python:3.11-slim

WORKDIR /app

COPY backend ./backend
COPY frontend ./frontend

RUN pip install --no-cache-dir -r backend/requirements.txt

WORKDIR /app/backend

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"
