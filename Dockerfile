FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for sqlite)
# sqlite3 is usually included in python images, but we ensure it works
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY *.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/data/keystone.db

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
