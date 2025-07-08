# backend/Dockerfile
FROM python:3.12-slim

# 1. Install system deps (psycopg binary needs gcc & libpq)
RUN apt-get update && apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source; will be over-mounted by the bind volume in dev
COPY app /code/app

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

