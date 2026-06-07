"""
Analytics Service - Query MotherDuck for insights.

Provides analytics queries for:
- Spending summary
- Category breakdown
- Monthly trends
- Top stores
- Recent receipts
"""

import os
import duckdb
import logging
from datetime import datetime, timedelta
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


def get_user_summary(user_id: str = None):
    """
    Get overall spending summary for user.

    Returns:
        dict: total_spent, receipt_count, avg_receipt, date_range
    """
    logger.info(f"Getting summary for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                COUNT(*) as receipt_count,
                SUM(total_amount) as total_spent,
                AVG(total_amount) as avg_receipt,
                MIN(receipt_date) as first_receipt,
                MAX(receipt_date) as last_receipt
            FROM fact_receipts
        """

        if user_id:
            query += f" WHERE user_id = '{user_id}'"

        result = conn.execute(query).fetchone()

        return {
            "receipt_count": int(result[0]) if result[0] else 0,
            "total_spent": float(result[1]) if result[1] else 0.0,
            "avg_receipt": float(result[2]) if result[2] else 0.0,
            "first_receipt": str(result[3]) if result[3] else None,
            "last_receipt": str(result[4]) if result[4] else None
        }

    finally:
        conn.close()


def get_spending_by_category(user_id: str = None):
    """
    Get spending breakdown by category.

    Returns:
        list: [{category, total_spent, item_count, receipt_count, avg_price}]
    """
    logger.info(f"Getting spending by category for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                i.category,
                SUM(i.total_price) as total_spent,
                COUNT(*) as item_count,
                COUNT(DISTINCT i.receipt_key) as receipt_count,
                AVG(i.total_price) as avg_price
            FROM dim_items i
        """

        if user_id:
            query += f"""
                JOIN fact_receipts f ON i.receipt_key = f.receipt_key
                WHERE f.user_id = '{user_id}'
            """

        query += """
            GROUP BY i.category
            ORDER BY total_spent DESC
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "category": row[0] or "Other",
                "total_spent": float(row[1]) if row[1] else 0.0,
                "item_count": int(row[2]) if row[2] else 0,
                "receipt_count": int(row[3]) if row[3] else 0,
                "avg_price": float(row[4]) if row[4] else 0.0
            }
            for row in results
        ]

    finally:
        conn.close()


def get_spending_by_month(user_id: str = None, months: int = 6):
    """
    Get monthly spending trend.

    Returns:
        list: [{month, total_spent, receipt_count}]
    """
    logger.info(f"Getting monthly spending for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                DATE_TRUNC('month', receipt_date) as month,
                SUM(total_amount) as total_spent,
                COUNT(*) as receipt_count
            FROM fact_receipts
        """

        where_clauses = []
        if user_id:
            where_clauses.append(f"user_id = '{user_id}'")

        if months:
            where_clauses.append(f"receipt_date >= CURRENT_DATE - INTERVAL '{months} months'")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += """
            GROUP BY month
            ORDER BY month ASC
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "month": row[0].strftime("%Y-%m") if row[0] else None,
                "total_spent": float(row[1]) if row[1] else 0.0,
                "receipt_count": int(row[2]) if row[2] else 0
            }
            for row in results
        ]

    finally:
        conn.close()


def get_top_stores(user_id: str = None, limit: int = 5):
    """
    Get top stores by spending.

    Returns:
        list: [{store_name, total_spent, receipt_count, avg_receipt}]
    """
    logger.info(f"Getting top stores for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                s.store_name,
                SUM(f.total_amount) as total_spent,
                COUNT(*) as receipt_count,
                AVG(f.total_amount) as avg_receipt
            FROM fact_receipts f
            JOIN dim_store s ON f.store_key = s.store_key
        """

        if user_id:
            query += f" WHERE f.user_id = '{user_id}'"

        query += f"""
            GROUP BY s.store_name
            ORDER BY total_spent DESC
            LIMIT {limit}
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "store_name": row[0],
                "total_spent": float(row[1]) if row[1] else 0.0,
                "receipt_count": int(row[2]) if row[2] else 0,
                "avg_receipt": float(row[3]) if row[3] else 0.0
            }
            for row in results
        ]

    finally:
        conn.close()


def get_recent_receipts(user_id: str = None, limit: int = 10):
    """
    Get recent receipts.

    Returns:
        list: [{receipt_id, store_name, date, total_amount, item_count}]
    """
    logger.info(f"Getting recent receipts for user: {user_id}")

    conn = get_motherduck_connection()

    try:
        query = """
            SELECT
                f.receipt_id,
                s.store_name,
                f.receipt_date,
                f.total_amount,
                f.item_count
            FROM fact_receipts f
            JOIN dim_store s ON f.store_key = s.store_key
        """

        if user_id:
            query += f" WHERE f.user_id = '{user_id}'"

        query += f"""
            ORDER BY f.receipt_date DESC
            LIMIT {limit}
        """

        results = conn.execute(query).fetchall()

        return [
            {
                "receipt_id": int(row[0]) if row[0] else 0,
                "store_name": row[1],
                "date": str(row[2]) if row[2] else None,
                "total_amount": float(row[3]) if row[3] else 0.0,
                "item_count": int(row[4]) if row[4] else 0
            }
            for row in results
        ]

    finally:
        conn.close()
