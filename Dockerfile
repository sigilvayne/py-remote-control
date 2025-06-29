FROM python:3.13-slim

WORKDIR /app

COPY /app/ ./app/

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.api:app"]



