"""
MotherDuck (Cloud DuckDB) service for analytics data warehouse.

Responsibilities:
- Create star schema (fact + dimension tables)
- ETL from Neon PostgreSQL to MotherDuck
- Analytics queries for frontend
"""

import os
import duckdb
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# MotherDuck connection string
# Format: md:database_name or md: for default
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_motherduck_connection():
    """
    Connect to MotherDuck cloud database.

    Returns:
        DuckDB connection object
    """
    try:
        # Connect to MotherDuck
        # If MOTHERDUCK_TOKEN is set, DuckDB will use it automatically
        if MOTHERDUCK_TOKEN:
            # First connect to default database
            conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')

            # Create receipts_analytics database if it doesn't exist
            conn.execute("CREATE DATABASE IF NOT EXISTS receipts_analytics")

            # Switch to receipts_analytics database
            conn.execute("USE receipts_analytics")

            logger.info("MotherDuck connection established (receipts_analytics)")
        else:
            # For local development, use local DuckDB file
            conn = duckdb.connect('receipts_analytics.duckdb')
            logger.warning("MOTHERDUCK_TOKEN not set, using local DuckDB file")

        return conn
    except Exception as e:
        logger.error(f"MotherDuck connection failed: {e}")
        raise


def init_star_schema():
    """
    Initialize star schema in MotherDuck.

    Creates:
    - fact_receipts (fact table)
    - dim_date (date dimension)
    - dim_store (store dimension)
    - dim_categories (category dimension)
    - dim_items (item dimension with categories)
    """
    logger.info("Initializing star schema in MotherDuck")

    conn = get_motherduck_connection()

    try:
        # Dimension: Categories
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_categories (
                category_key INTEGER PRIMARY KEY,
                category_name VARCHAR,
                category_group VARCHAR
            )
        """)

        # Pre-populate categories
        conn.execute("""
            INSERT INTO dim_categories VALUES
                (1, 'Dairy Products', 'Food'),
                (2, 'Meat & Fish', 'Food'),
                (3, 'Fruits & Vegetables', 'Food'),
                (4, 'Bakery', 'Food'),
                (5, 'Beverages', 'Food'),
                (6, 'Snacks & Sweets', 'Food'),
                (7, 'Frozen Foods', 'Food'),
                (8, 'Pantry & Staples', 'Food'),
                (9, 'Household & Other', 'Non-Food')
            ON CONFLICT DO NOTHING
        """)

        # Dimension: Date
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_date (
                date_key INTEGER PRIMARY KEY,
                date DATE,
                year INTEGER,
                quarter INTEGER,
                month INTEGER,
                month_name VARCHAR,
                day INTEGER,
                day_of_week INTEGER,
                day_name VARCHAR,
                week_of_year INTEGER
            )
        """)

        # Dimension: Store
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_store (
                store_key INTEGER PRIMARY KEY,
                store_name VARCHAR,
                store_category VARCHAR
            )
        """)

        # Fact Table: Receipts
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_receipts (
                receipt_key INTEGER PRIMARY KEY,
                receipt_id INTEGER,
                user_id VARCHAR,
                date_key INTEGER,
                store_key INTEGER,

                -- Metrics
                total_amount DECIMAL(10,2),
                tax_amount DECIMAL(10,2),
                subtotal DECIMAL(10,2),
                item_count INTEGER,

                -- Timestamps
                receipt_date DATE,
                created_at TIMESTAMP
            )
        """)

        # Dimension: Items (with categories)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_items (
                item_key INTEGER PRIMARY KEY,
                receipt_key INTEGER,
                item_name VARCHAR,
                quantity DECIMAL(10,2),
                unit VARCHAR,
                unit_price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                category VARCHAR,
                subcategory VARCHAR,
                created_at TIMESTAMP
            )
        """)

        logger.info("Star schema initialized successfully")

    except Exception as e:
        logger.error(f"Star schema initialization failed: {e}")
        raise
    finally:
        conn.close()


def get_or_create_date_key(conn, date_str):
    """
    Get or create date dimension entry.

    Args:
        conn: DuckDB connection
        date_str: Date string in YYYY-MM-DD format

    Returns:
        date_key (INTEGER): YYYYMMDD format
    """
    if not date_str:
        return None

    try:
        # Parse date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_key = int(date_obj.strftime('%Y%m%d'))

        # Check if exists
        result = conn.execute(
            "SELECT date_key FROM dim_date WHERE date_key = ?",
            [date_key]
        ).fetchone()

        if result:
            return date_key

        # Create new entry
        conn.execute("""
            INSERT INTO dim_date VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            date_key,
            date_obj.date(),
            date_obj.year,
            (date_obj.month - 1) // 3 + 1,  # Quarter
            date_obj.month,
            date_obj.strftime('%B'),  # Month name
            date_obj.day,
            date_obj.weekday(),  # 0=Monday
            date_obj.strftime('%A'),  # Day name
            date_obj.isocalendar()[1]  # Week of year
        ])

        return date_key

    except Exception as e:
        logger.error(f"Date key creation failed: {e}")
        return None


def get_or_create_store_key(conn, store_name):
    """
    Get or create store dimension entry.

    Args:
        conn: DuckDB connection
        store_name: Store name

    Returns:
        store_key (INTEGER)
    """
    if not store_name:
        return None

    try:
        # Check if exists
        result = conn.execute(
            "SELECT store_key FROM dim_store WHERE store_name = ?",
            [store_name]
        ).fetchone()

        if result:
            return result[0]

        # Create new entry - get max key + 1
        max_key = conn.execute("SELECT COALESCE(MAX(store_key), 0) FROM dim_store").fetchone()[0]
        new_key = max_key + 1

        conn.execute("""
            INSERT INTO dim_store VALUES (?, ?, ?)
        """, [
            new_key,
            store_name,
            'Supermarket'  # Default category
        ])

        return new_key

    except Exception as e:
        logger.error(f"Store key creation failed: {e}")
        return None


def sync_receipt_to_motherduck(receipt_id, user_id, receipt_data):
    """
    Sync a single receipt from Neon to MotherDuck star schema.

    Args:
        receipt_id: Receipt ID from Neon
        user_id: User identifier
        receipt_data: Parsed receipt JSON

    Returns:
        True if successful
    """
    logger.info(f"Syncing receipt {receipt_id} to MotherDuck")

    conn = get_motherduck_connection()

    try:
        # Extract data
        store_name = receipt_data.get("store", {}).get("name", "Unknown")
        receipt_date = receipt_data.get("receipt", {}).get("date")
        total_amount = receipt_data.get("totals", {}).get("sum", 0.0)
        tax_amount = receipt_data.get("tax", {}).get("tax_amount", 0.0)
        subtotal = receipt_data.get("tax", {}).get("net_amount", total_amount - tax_amount)
        items = receipt_data.get("items", [])

        # Get dimension keys
        date_key = get_or_create_date_key(conn, receipt_date)
        store_key = get_or_create_store_key(conn, store_name)

        # Insert fact_receipts
        conn.execute("""
            INSERT INTO fact_receipts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            receipt_id,  # receipt_key
            receipt_id,  # receipt_id
            user_id,
            date_key,
            store_key,
            total_amount,
            tax_amount,
            subtotal,
            len(items),  # item_count
            receipt_date,
            datetime.now()
        ])

        # Insert items
        for idx, item in enumerate(items):
            item_key = int(f"{receipt_id}{idx:03d}")  # Combine receipt_id + item index

            conn.execute("""
                INSERT INTO dim_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                item_key,
                receipt_id,
                item.get("name", ""),
                item.get("quantity", 1.0),
                item.get("unit", ""),
                item.get("unit_price", 0.0),
                item.get("total_price", 0.0),
                item.get("category", "Household & Other"),
                item.get("subcategory", ""),
                datetime.now()
            ])

        logger.info(f"Receipt {receipt_id} synced successfully")
        return True

    except Exception as e:
        logger.error(f"Receipt sync failed: {e}")
        return False
    finally:
        conn.close()
