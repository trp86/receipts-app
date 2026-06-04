from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from telegram_handler import process_telegram_update
from image_service import download_image
from parser_service import parse_receipt_image
from db_service import init_database, insert_receipt
from response_service import send_receipt_response
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

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://app-receiptscan.netlify.app",
        "http://app-receiptscan.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database schema")
    try:
        init_database()
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


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

            # Parse image with Gemini Vision model
            receipt_data = parse_receipt_image(image_bytes)
            logger.info(f"Vision parsing complete!")
            logger.info(f"Structured receipt data: {receipt_data}")

            # Store in database
            chat_id = extracted_data.get("chat_id")
            if chat_id and receipt_data:
                receipt_id = insert_receipt(chat_id, receipt_data)
                logger.info(f"Receipt stored in database with ID: {receipt_id}")

                # Send response back to Telegram
                send_receipt_response(TELEGRAM_BOT_TOKEN, chat_id, receipt_data, receipt_id)

        except Exception as e:
            logger.error(f"Processing failed: {e}")
    else:
        logger.info("No photo to download")

    # Acknowledge receipt to Telegram
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """
    Web frontend upload endpoint.

    Accepts image file, processes with Gemini Vision,
    stores in database, and returns structured data.
    """
    logger.info("=== WEB UPLOAD CALLED ===")

    try:
        # Read image bytes
        image_bytes = await file.read()
        logger.info(f"Image received: {len(image_bytes)} bytes")

        # Parse image with Gemini Vision
        receipt_data = parse_receipt_image(image_bytes)
        logger.info(f"Vision parsing complete!")
        logger.info(f"Structured receipt data: {receipt_data}")

        # Store in database (use 0 as chat_id for web uploads)
        if receipt_data:
            receipt_id = insert_receipt(0, receipt_data)
            logger.info(f"Receipt stored in database with ID: {receipt_id}")

            # Transform data for frontend compatibility
            frontend_data = {
                "store_name": receipt_data.get("store", {}).get("name", ""),
                "date": receipt_data.get("receipt", {}).get("date", ""),
                "total_amount": str(receipt_data.get("totals", {}).get("sum", 0.0)),
                "items": [
                    {
                        "name": item.get("name", ""),
                        "price": str(item.get("total_price", 0.0))
                    }
                    for item in receipt_data.get("items", [])
                ]
            }

            logger.info(f"Frontend data: {frontend_data}")

            # Return parsed data
            return {
                "success": True,
                "receipt_id": receipt_id,
                "data": frontend_data
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to parse receipt")

    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Receipt Processing Backend"}
