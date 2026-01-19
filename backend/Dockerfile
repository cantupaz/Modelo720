FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Modelo720 library first (dependency)
COPY Modelo720/ /modelo720-lib/Modelo720/

# Copy application code
COPY backend/app/ ./app/

# Set Python path to find library
ENV PYTHONPATH=/modelo720-lib:$PYTHONPATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
