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

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Step 1: Create base table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                store_name VARCHAR(255),
                total_amount DECIMAL(10,2),
                date DATE,
                raw_json JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Step 2: Add new columns if they don't exist
        cursor.execute("""
            DO $$
            BEGIN
                -- Add user_id column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='receipts' AND column_name='user_id') THEN
                    ALTER TABLE receipts ADD COLUMN user_id VARCHAR(255);
                END IF;

                -- Add synced_to_dwh column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='receipts' AND column_name='synced_to_dwh') THEN
                    ALTER TABLE receipts ADD COLUMN synced_to_dwh BOOLEAN DEFAULT FALSE;
                END IF;

                -- Add synced_at column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name='receipts' AND column_name='synced_at') THEN
                    ALTER TABLE receipts ADD COLUMN synced_at TIMESTAMP;
                END IF;
            END $$;
        """)

        # Step 3: Make chat_id nullable (remove NOT NULL constraint)
        cursor.execute("""
            ALTER TABLE receipts ALTER COLUMN chat_id DROP NOT NULL;
        """)

        # Step 4: Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON receipts(chat_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON receipts(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON receipts(date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_store ON receipts(store_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_synced ON receipts(synced_to_dwh);")

        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def insert_receipt(user_id, receipt_json):
    """
    Insert parsed receipt into database.

    Args:
        user_id: User identifier (web user ID or chat ID for legacy)
        receipt_json: Parsed receipt dictionary (nested structure)

    Returns:
        Receipt ID if successful, None otherwise
    """
    logger.info(f"Inserting receipt for user_id: {user_id}")
    logger.info(f"Receipt data keys: {receipt_json.keys()}")

    insert_sql = """
    INSERT INTO receipts (user_id, store_name, total_amount, date, raw_json)
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
            (user_id, store_name, total_amount, date, Json(receipt_json))
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
