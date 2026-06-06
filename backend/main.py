from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser_service import parse_receipt_image
from db_service import init_database, insert_receipt
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

app = FastAPI()

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://app-receiptscan.netlify.app",
        "http://app-receiptscan.netlify.app",
        "https://lovely-selkie-5a9946.netlify.app",
        "http://lovely-selkie-5a9946.netlify.app"
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


@app.post("/api/upload")
async def upload_receipt(file: UploadFile = File(...), user_id: str = None):
    """
    Web frontend upload endpoint.

    Accepts image file, processes with Gemini Vision,
    stores in database, and returns structured data.
    """
    logger.info("=== WEB UPLOAD CALLED ===")
    logger.info(f"User ID: {user_id}")

    try:
        # Read image bytes
        image_bytes = await file.read()
        logger.info(f"Image received: {len(image_bytes)} bytes")

        # Parse image with Gemini Vision (now includes categories)
        receipt_data = parse_receipt_image(image_bytes)
        logger.info(f"Vision parsing complete!")
        logger.info(f"Structured receipt data: {receipt_data}")

        # Store in database (use provided user_id or 'anonymous')
        if receipt_data:
            user_identifier = user_id if user_id else 'anonymous'
            receipt_id = insert_receipt(user_identifier, receipt_data)
            logger.info(f"Receipt stored in database with ID: {receipt_id}")

            # Transform data for frontend compatibility
            frontend_data = {
                "store_name": receipt_data.get("store", {}).get("name", ""),
                "date": receipt_data.get("receipt", {}).get("date", ""),
                "total_amount": str(receipt_data.get("totals", {}).get("sum", 0.0)),
                "items": [
                    {
                        "name": item.get("name", ""),
                        "price": str(item.get("total_price", 0.0)),
                        "category": item.get("category", ""),
                        "subcategory": item.get("subcategory", "")
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
