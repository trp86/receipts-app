from fastapi import FastAPI, Request
from telegram_handler import process_telegram_update
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    """
    Telegram webhook endpoint.

    Receives photo updates from Telegram bot.
    Logs payload and extracts photo metadata.
    """
    update_data = await request.json()

    # Process the update
    extracted_data = process_telegram_update(update_data)

    # Acknowledge receipt to Telegram
    return {"status": "ok"}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Receipt Processing Backend"}
