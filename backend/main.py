from fastapi import FastAPI, Request
from telegram_handler import process_telegram_update
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    """
    Telegram webhook endpoint.

    Receives photo updates from Telegram bot.
    Logs payload and extracts photo metadata.
    """
    logger.info("=== WEBHOOK CALLED ===")
    update_data = await request.json()
    logger.info(f"Received update_id: {update_data.get('update_id')}")

    # Process the update
    extracted_data = process_telegram_update(update_data)
    logger.info(f"Extraction result: {extracted_data}")

    # Acknowledge receipt to Telegram
    return {"status": "ok"}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Receipt Processing Backend"}
