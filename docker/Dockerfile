# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

FROM base AS api
COPY apps/api/requirements.txt apps/api/requirements.txt
COPY scraper/requirements.txt scraper/requirements.txt
COPY packages/ai_engine/requirements.txt packages/ai_engine/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt -r scraper/requirements.txt
COPY apps/ apps/
COPY packages/ packages/
COPY scraper/ scraper/
COPY scanners/ scanners/
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python3", "apps/api/server.py"]
