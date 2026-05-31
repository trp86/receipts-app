#!/bin/bash
# Install tesseract if not already installed
if ! command -v tesseract &> /dev/null; then
    echo "Installing tesseract-ocr..."
    apt-get update && apt-get install -y tesseract-ocr
fi

# Start the application
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
