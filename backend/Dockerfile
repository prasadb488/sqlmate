FROM python:3.11-slim

WORKDIR /app
COPY . .

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir fastapi uvicorn ollama pydantic httpx psycopg2-binary

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
