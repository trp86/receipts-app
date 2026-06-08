"""
Quantity Analytics Service - Bulk purchase insights from MotherDuck.

Provides analytics for:
- Bulk purchase summary
- Top bulk items
- Average quantity by category
- Unit price comparison
- Quantity trends over time
"""

import os
import duckdb
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")


def get_motherduck_connection():
    """Connect to MotherDuck or local DuckDB."""
    try:
        if MOTHERDUCK_TOKEN:
            conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
            conn.execute("USE receipts_analytics")
        else:
            conn = duckdb.connect('receipts_analytics.duckdb')
            logger.warning("Using local DuckDB (MOTHERDUCK_TOKEN not set)")

        return conn
    except Exception as e:
        logger.error(f"MotherDuck connection failed: {e}")
        raise


def get_bulk_purchase_summary(user_id: str = None):
    """
    Get overall bulk purchase summary.

    Returns:
        dict: {
            items_in_bulk: int,
            total_units: int,
            avg_quantity: float,
            bulk_percentage: float
        }
    """
    logger.info(f"Getting bulk purchase summary for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        # Get bulk statistics
        query = """
            SELECT
                COUNT(DISTINCT CASE WHEN i.quantity > 1 THEN i.item_name END) as items_in_bulk,
                SUM(i.quantity) as total_units,
                AVG(i.quantity) as avg_quantity,
                COUNT(DISTINCT i.item_name) as total_items
            FROM dim_items i
        """

        if user_id:
            query += f"""
                JOIN fact_receipts f ON i.receipt_key = f.receipt_key
                WHERE f.user_id = '{user_id}'
            """

        result = conn.execute(query).fetchone()

        items_in_bulk = int(result[0]) if result[0] else 0
        total_units = float(result[1]) if result[1] else 0.0
        avg_quantity = float(result[2]) if result[2] else 0.0
        total_items = int(result[3]) if result[3] else 0

        bulk_percentage = (items_in_bulk / total_items * 100) if total_items > 0 else 0.0

        return {
            "items_in_bulk": items_in_bulk,
            "total_units": total_units,
            "avg_quantity": round(avg_quantity, 1),
            "bulk_percentage": round(bulk_percentage, 1)
        }

    finally:
        conn.close()


def get_top_bulk_items(user_id: str = None, limit: int = 10):
    """
    Get top items bought in bulk.

    Returns:
        list: [{
            item_name: str,
            category: str,
            avg_quantity: float,
            times_purchased: int,
            total_units: int,
            total_spent: float
        }]
    """
    logger.info(f"Getting top bulk items for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                i.item_name,
                i.category,
                AVG(i.quantity) as avg_quantity,
                COUNT(*) as times_purchased,
                SUM(i.quantity) as total_units,
                SUM(i.total_price) as total_spent
            FROM dim_items i
        """

        if user_id:
            query += f"""
                JOIN fact_receipts f ON i.receipt_key = f.receipt_key
                WHERE f.user_id = '{user_id}' AND i.quantity > 1
            """
        else:
            query += " WHERE i.quantity > 1"

        query += f"""
            GROUP BY i.item_name, i.category
            ORDER BY avg_quantity DESC
            LIMIT {limit}
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "item_name": row[0],
                "category": row[1] or "Other",
                "avg_quantity": round(float(row[2]), 1) if row[2] else 0.0,
                "times_purchased": int(row[3]) if row[3] else 0,
                "total_units": float(row[4]) if row[4] else 0.0,
                "total_spent": round(float(row[5]), 2) if row[5] else 0.0
            }
            for row in results
        ]

    finally:
        conn.close()


def get_avg_quantity_by_category(user_id: str = None):
    """
    Get average quantity purchased by category.

    Returns:
        list: [{
            category: str,
            avg_quantity: float,
            total_units: int,
            purchase_count: int
        }]
    """
    logger.info(f"Getting average quantity by category for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                i.category,
                AVG(i.quantity) as avg_quantity,
                SUM(i.quantity) as total_units,
                COUNT(*) as purchase_count
            FROM dim_items i
        """

        if user_id:
            query += f"""
                JOIN fact_receipts f ON i.receipt_key = f.receipt_key
                WHERE f.user_id = '{user_id}'
            """

        query += """
            GROUP BY i.category
            ORDER BY avg_quantity DESC
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "category": row[0] or "Other",
                "avg_quantity": round(float(row[1]), 1) if row[1] else 0.0,
                "total_units": float(row[2]) if row[2] else 0.0,
                "purchase_count": int(row[3]) if row[3] else 0
            }
            for row in results
        ]

    finally:
        conn.close()


def get_unit_price_insights(user_id: str = None, limit: int = 10):
    """
    Get unit price comparison for frequently purchased items.

    Returns:
        list: [{
            item_name: str,
            category: str,
            avg_unit_price: float,
            best_price: float,
            highest_price: float,
            price_variation: float,
            times_purchased: int,
            potential_savings: float
        }]
    """
    logger.info(f"Getting unit price insights for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                i.item_name,
                i.category,
                AVG(i.unit_price) as avg_unit_price,
                MIN(i.unit_price) as best_price,
                MAX(i.unit_price) as highest_price,
                COUNT(*) as times_purchased,
                SUM(i.quantity) as total_units
            FROM dim_items i
        """

        if user_id:
            query += f"""
                JOIN fact_receipts f ON i.receipt_key = f.receipt_key
                WHERE f.user_id = '{user_id}'
                    AND i.unit_price > 0
            """
        else:
            query += " WHERE i.unit_price > 0"

        query += f"""
            GROUP BY i.item_name, i.category
            HAVING COUNT(*) > 1
            ORDER BY (MAX(i.unit_price) - MIN(i.unit_price)) DESC
            LIMIT {limit}
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "item_name": row[0],
                "category": row[1] or "Other",
                "avg_unit_price": round(float(row[2]), 2) if row[2] else 0.0,
                "best_price": round(float(row[3]), 2) if row[3] else 0.0,
                "highest_price": round(float(row[4]), 2) if row[4] else 0.0,
                "price_variation": round((float(row[4]) - float(row[3])), 2) if row[3] and row[4] else 0.0,
                "times_purchased": int(row[5]) if row[5] else 0,
                "potential_savings": round((float(row[2]) - float(row[3])) * float(row[6]), 2) if row[2] and row[3] and row[6] else 0.0
            }
            for row in results
        ]

    finally:
        conn.close()


def get_quantity_trends(user_id: str = None, months: int = 6):
    """
    Get quantity trends over time by category.

    Returns:
        list: [{
            month: str,
            category: str,
            avg_quantity: float,
            total_units: int
        }]
    """
    logger.info(f"Getting quantity trends for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                DATE_TRUNC('month', f.receipt_date) as month,
                i.category,
                AVG(i.quantity) as avg_quantity,
                SUM(i.quantity) as total_units
            FROM dim_items i
            JOIN fact_receipts f ON i.receipt_key = f.receipt_key
        """

        where_clauses = []
        if user_id:
            where_clauses.append(f"f.user_id = '{user_id}'")

        if months:
            where_clauses.append(f"f.receipt_date >= CURRENT_DATE - INTERVAL '{months} months'")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += """
            GROUP BY month, i.category
            ORDER BY month ASC, i.category ASC
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "month": row[0].strftime("%Y-%m") if row[0] else None,
                "category": row[1] or "Other",
                "avg_quantity": round(float(row[2]), 1) if row[2] else 0.0,
                "total_units": float(row[3]) if row[3] else 0.0
            }
            for row in results
        ]

    finally:
        conn.close()
