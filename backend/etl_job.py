"""
ETL Job: Neon PostgreSQL → MotherDuck Analytics

This job syncs unsynced receipts from Neon to MotherDuck star schema.

Can be run:
- As a cron job (scheduled)
- Manually via CLI
- Triggered after each receipt upload
"""

import os
import sys
import psycopg2
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from motherduck_service import sync_receipt_to_motherduck, init_star_schema

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_unsynced_receipts():
    """
    Get all receipts from Neon that haven't been synced to MotherDuck.

    Returns:
        List of receipt tuples: (id, user_id, raw_json)
    """
    logger.info("Fetching unsynced receipts from Neon")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_id, raw_json
            FROM receipts
            WHERE synced_to_dwh = FALSE OR synced_to_dwh IS NULL
            ORDER BY created_at ASC
        """)

        receipts = cursor.fetchall()
        cursor.close()
        conn.close()

        logger.info(f"Found {len(receipts)} unsynced receipts")
        return receipts

    except Exception as e:
        logger.error(f"Failed to fetch unsynced receipts: {e}")
        return []


def mark_receipt_synced(receipt_id):
    """
    Mark a receipt as synced in Neon database.

    Args:
        receipt_id: Receipt ID to mark
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE receipts
            SET synced_to_dwh = TRUE,
                synced_at = %s
            WHERE id = %s
        """, (datetime.now(), receipt_id))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Receipt {receipt_id} marked as synced")

    except Exception as e:
        logger.error(f"Failed to mark receipt {receipt_id} as synced: {e}")


def run_etl():
    """
    Run ETL process: Sync all unsynced receipts from Neon to MotherDuck.

    Returns:
        Number of receipts synced
    """
    logger.info("=== Starting ETL Job ===")

    try:
        # Initialize star schema if needed
        init_star_schema()

        # Get unsynced receipts
        receipts = get_unsynced_receipts()

        if not receipts:
            logger.info("No receipts to sync")
            return 0

        # Sync each receipt
        synced_count = 0

        for receipt_id, user_id, raw_json in receipts:
            try:
                # Parse JSON
                receipt_data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json

                # Sync to MotherDuck
                success = sync_receipt_to_motherduck(receipt_id, user_id, receipt_data)

                if success:
                    # Mark as synced in Neon
                    mark_receipt_synced(receipt_id)
                    synced_count += 1
                    logger.info(f"✓ Receipt {receipt_id} synced ({synced_count}/{len(receipts)})")
                else:
                    logger.error(f"✗ Receipt {receipt_id} failed to sync")

            except Exception as e:
                logger.error(f"Error syncing receipt {receipt_id}: {e}")
                continue

        logger.info(f"=== ETL Complete: {synced_count}/{len(receipts)} receipts synced ===")
        return synced_count

    except Exception as e:
        logger.error(f"ETL job failed: {e}")
        return 0


if __name__ == "__main__":
    """
    Run ETL job from command line:
    python etl_job.py
    """
    print("🚀 Starting ETL Job: Neon → MotherDuck")
    print("-" * 50)

    synced = run_etl()

    print("-" * 50)
    print(f"✅ ETL Complete: {synced} receipts synced")
