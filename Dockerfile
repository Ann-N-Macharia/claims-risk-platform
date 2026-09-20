FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m scripts.train

EXPOSE 8000
CMD ["uvicorn", "claims_platform.api:app", "--host", "0.0.0.0", "--port", "8000"]
