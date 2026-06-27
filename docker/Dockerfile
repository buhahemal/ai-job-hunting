# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

FROM base AS backend
COPY backend/requirements.txt backend/requirements.txt
COPY scraper/requirements.txt scraper/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -r scraper/requirements.txt
COPY backend/ backend/
COPY scraper/ scraper/
EXPOSE 3000
CMD ["python3", "backend/server.py"]
