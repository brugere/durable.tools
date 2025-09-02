# backend/Dockerfile
FROM python:3.12-slim

# No system dependencies needed for pre-compiled Python wheels

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=all -r requirements.txt

COPY app /code/app
COPY ingest /code/ingest
COPY data /code/data
COPY setup_database.py /code/setup_database.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

