from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from parser_service import parse_receipt_image, parse_receipt_images_multi
from db_service import init_database, insert_receipt
from motherduck_service import init_star_schema
from etl_job import run_etl
from analytics_service import (
    get_user_summary,
    get_spending_by_category,
    get_spending_by_month,
    get_top_stores,
    get_recent_receipts
)
from typing import List, Optional
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
async def upload_receipt(
    files: List[UploadFile] = File(None),
    file: UploadFile = File(None),
    user_id: str = Form(None)
):
    """
    Web frontend upload endpoint (supports multiple images for long receipts).

    Accepts one or more image files, processes with Gemini Vision,
    stores in database, and returns structured data.

    Backward compatible: accepts both 'file' (single) and 'files' (multiple)
    """
    logger.info("=== WEB UPLOAD CALLED ===")
    logger.info(f"User ID: {user_id}")

    try:
        # Collect all uploaded files
        upload_files = []
        if files and files[0]:  # New format: multiple files
            upload_files = files
        elif file:  # Old format: single file
            upload_files = [file]
        else:
            raise HTTPException(status_code=400, detail="No image files provided")

        logger.info(f"Number of images: {len(upload_files)}")

        # Read all image bytes
        images_bytes = []
        for f in upload_files:
            image_bytes = await f.read()
            images_bytes.append(image_bytes)
            logger.info(f"Image received: {len(image_bytes)} bytes")

        # Parse images with Gemini Vision
        if len(images_bytes) == 1:
            # Single image - use original method
            receipt_data = parse_receipt_image(images_bytes[0])
        else:
            # Multiple images - merge data
            receipt_data = parse_receipt_images_multi(images_bytes)

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
                        "quantity": item.get("quantity", 1.0),
                        "unit": item.get("unit", ""),
                        "unit_price": str(item.get("unit_price", 0.0)),
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


@app.post("/api/admin/init-star-schema")
async def admin_init_star_schema():
    """
    Admin endpoint to initialize MotherDuck star schema.
    Call this once after deployment.
    """
    logger.info("=== ADMIN: Initializing star schema ===")
    try:
        init_star_schema()
        return {"success": True, "message": "Star schema initialized"}
    except Exception as e:
        logger.error(f"Star schema initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/run-etl")
async def admin_run_etl():
    """
    Admin endpoint to manually trigger ETL job.
    Syncs unsynced receipts from Neon to MotherDuck.
    """
    logger.info("=== ADMIN: Running ETL job ===")
    try:
        synced_count = run_etl()
        return {
            "success": True,
            "message": f"ETL complete: {synced_count} receipts synced"
        }
    except Exception as e:
        logger.error(f"ETL job failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Detailed health check with service status.
    """
    import psycopg2

    health = {
        "status": "healthy",
        "services": {}
    }

    # Check Neon database
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM receipts")
        receipt_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        health["services"]["neon_db"] = {
            "status": "connected",
            "receipt_count": receipt_count
        }
    except Exception as e:
        health["services"]["neon_db"] = {
            "status": "error",
            "error": str(e)
        }
        health["status"] = "degraded"

    # Check MotherDuck token
    MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
    if MOTHERDUCK_TOKEN:
        health["services"]["motherduck"] = {
            "status": "token_configured"
        }
    else:
        health["services"]["motherduck"] = {
            "status": "token_missing",
            "note": "Using local DuckDB"
        }

    # Check Gemini API key
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        health["services"]["gemini_api"] = {
            "status": "configured"
        }
    else:
        health["services"]["gemini_api"] = {
            "status": "missing"
        }
        health["status"] = "degraded"

    return health


# Analytics Endpoints

@app.get("/api/analytics/summary")
async def analytics_summary(user_id: Optional[str] = Query(None)):
    """Get overall spending summary."""
    try:
        data = get_user_summary(user_id)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Analytics summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/by-category")
async def analytics_by_category(user_id: Optional[str] = Query(None)):
    """Get spending breakdown by category."""
    try:
        data = get_spending_by_category(user_id)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Analytics by category failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/by-month")
async def analytics_by_month(
    user_id: Optional[str] = Query(None),
    months: int = Query(6, ge=1, le=24)
):
    """Get monthly spending trend."""
    try:
        data = get_spending_by_month(user_id, months)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Analytics by month failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/top-stores")
async def analytics_top_stores(
    user_id: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=20)
):
    """Get top stores by spending."""
    try:
        data = get_top_stores(user_id, limit)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Analytics top stores failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/recent")
async def analytics_recent(
    user_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get recent receipts."""
    try:
        data = get_recent_receipts(user_id, limit)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Analytics recent receipts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
