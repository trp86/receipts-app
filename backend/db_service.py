"""
Database service for storing receipt data in Neon PostgreSQL.

Responsibilities:
- Connect to Neon database
- Create tables if not exist
- Insert parsed receipt JSON
"""

import os
import psycopg2
from psycopg2.extras import Json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL not set in environment")


def get_connection():
    """
    Create database connection.

    Returns:
        Connection object
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def init_database():
    """
    Initialize database schema.
    Creates receipts table if it doesn't exist.
    """
    logger.info("Initializing database schema")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS receipts (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT NOT NULL,
        store_name VARCHAR(255),
        total_amount DECIMAL(10,2),
        date DATE,
        raw_json JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_chat_id ON receipts(chat_id);
    CREATE INDEX IF NOT EXISTS idx_date ON receipts(date);
    CREATE INDEX IF NOT EXISTS idx_store ON receipts(store_name);
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def insert_receipt(chat_id, receipt_json):
    """
    Insert parsed receipt into database.

    Args:
        chat_id: Telegram chat ID
        receipt_json: Parsed receipt dictionary (nested structure)

    Returns:
        Receipt ID if successful, None otherwise
    """
    logger.info(f"Inserting receipt for chat_id: {chat_id}")
    logger.info(f"Receipt data keys: {receipt_json.keys()}")

    insert_sql = """
    INSERT INTO receipts (chat_id, store_name, total_amount, date, raw_json)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """

    try:
        # Extract key fields from nested structure
        store_name = None
        total_amount = None
        date = None

        # Extract store name from nested structure
        if "store" in receipt_json and isinstance(receipt_json["store"], dict):
            store_name = receipt_json["store"].get("name")

        # Extract total amount from nested structure
        if "totals" in receipt_json and isinstance(receipt_json["totals"], dict):
            total_amount = receipt_json["totals"].get("sum")

        # Extract date from nested structure
        if "receipt" in receipt_json and isinstance(receipt_json["receipt"], dict):
            date = receipt_json["receipt"].get("date")

        logger.info(f"Extracted: store={store_name}, total={total_amount}, date={date}")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            insert_sql,
            (chat_id, store_name, total_amount, date, Json(receipt_json))
        )
        receipt_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Receipt inserted successfully with ID: {receipt_id}")
        return receipt_id

    except Exception as e:
        logger.error(f"Receipt insertion failed: {e}")
        raise
