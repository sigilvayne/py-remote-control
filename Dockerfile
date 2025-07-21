FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY templates/ ./templates/
COPY static ./static
COPY scripts ./scripts

RUN mkdir -p /app/data

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api:app"]
