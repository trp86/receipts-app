"""
Test script to check database contents.

Usage:
    python test_database.py
"""

import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_database():
    """Check receipts in database."""
    print("=== Database Test ===")
    print("-" * 50)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM receipts")
        total = cursor.fetchone()[0]
        print(f"Total receipts: {total}")
        print()

        # Get recent receipts
        cursor.execute("""
            SELECT id, user_id, store_name, total_amount, date,
                   synced_to_dwh, created_at, raw_json
            FROM receipts
            ORDER BY created_at DESC
            LIMIT 5
        """)

        receipts = cursor.fetchall()

        if receipts:
            print(f"Recent receipts (last {len(receipts)}):")
            print("-" * 50)

            for receipt in receipts:
                receipt_id, user_id, store_name, total_amount, date, synced, created_at, raw_json = receipt

                print(f"\nReceipt #{receipt_id}")
                print(f"  User ID: {user_id}")
                print(f"  Store: {store_name}")
                print(f"  Total: €{total_amount}")
                print(f"  Date: {date}")
                print(f"  Synced to DWH: {synced}")
                print(f"  Created: {created_at}")

                # Parse JSON to check for categories
                if raw_json:
                    data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                    items = data.get('items', [])
                    print(f"  Items: {len(items)}")

                    # Show first item with category
                    if items and len(items) > 0:
                        first_item = items[0]
                        category = first_item.get('category', 'N/A')
                        subcategory = first_item.get('subcategory', 'N/A')
                        print(f"    Example: {first_item.get('name')} -> {category}/{subcategory}")

        else:
            print("No receipts found in database")

        # Check for unsynced receipts
        cursor.execute("""
            SELECT COUNT(*) FROM receipts
            WHERE synced_to_dwh = FALSE OR synced_to_dwh IS NULL
        """)
        unsynced = cursor.fetchone()[0]
        print()
        print(f"Unsynced receipts: {unsynced}")

        cursor.close()
        conn.close()

        print("-" * 50)
        print("✓ Database test complete")

    except Exception as e:
        print(f"✗ Database test failed: {e}")


if __name__ == "__main__":
    test_database()
