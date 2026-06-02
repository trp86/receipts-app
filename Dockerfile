# Use Python 3.11 (more stable than 3.14)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
# RUN apt-get update && apt-get install -y \
#     <package-name> \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 10000

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
