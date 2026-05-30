from fastapi import FastAPI, Request
from telegram_handler import process_telegram_update
from image_service import download_image
from ocr_service import extract_text
import logging
import sys
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in environment")

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    """
    Telegram webhook endpoint.

    Receives photo updates from Telegram bot.
    Downloads image and processes it.
    """
    logger.info("=== WEBHOOK CALLED ===")
    update_data = await request.json()
    logger.info(f"Received update_id: {update_data.get('update_id')}")

    # Extract chat_id and file_id
    extracted_data = process_telegram_update(update_data)
    logger.info(f"Extraction result: {extracted_data}")

    # Download image if photo exists
    if extracted_data.get("file_id"):
        try:
            image_bytes = download_image(TELEGRAM_BOT_TOKEN, extracted_data["file_id"])
            logger.info(f"Image downloaded successfully: {len(image_bytes)} bytes")

            # Extract text using OCR
            text = extract_text(image_bytes)
            logger.info(f"OCR extraction complete: {len(text)} characters")
            logger.info(f"Full extracted text:\n{text}")

        except Exception as e:
            logger.error(f"Processing failed: {e}")
    else:
        logger.info("No photo to download")

    # Acknowledge receipt to Telegram
    return {"status": "ok"}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Receipt Processing Backend"}
