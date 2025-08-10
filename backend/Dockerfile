# backend/Dockerfile
FROM python:3.12-slim

# Install minimal system deps (no Postgres client needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app /code/app
COPY ingest /code/ingest
COPY data /code/data
COPY setup_database.py /code/setup_database.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

