"""
ETL Status Checker

Quick script to check ETL sync status between Neon and MotherDuck.
"""

import os
import psycopg2
import duckdb
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")


def check_neon_status():
    """Check Neon database status."""
    print("=" * 50)
    print("📊 Neon PostgreSQL Status")
    print("=" * 50)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Total receipts
        cursor.execute("SELECT COUNT(*) FROM receipts")
        total = cursor.fetchone()[0]
        print(f"Total receipts: {total}")

        # Synced receipts
        cursor.execute("SELECT COUNT(*) FROM receipts WHERE synced_to_dwh = TRUE")
        synced = cursor.fetchone()[0]
        print(f"Synced receipts: {synced}")

        # Unsynced receipts
        cursor.execute("SELECT COUNT(*) FROM receipts WHERE synced_to_dwh = FALSE OR synced_to_dwh IS NULL")
        unsynced = cursor.fetchone()[0]
        print(f"Unsynced receipts: {unsynced}")

        if unsynced > 0:
            print(f"\n⚠️  {unsynced} receipts waiting to be synced")
            cursor.execute("""
                SELECT id, store_name, total_amount, date, created_at
                FROM receipts
                WHERE synced_to_dwh = FALSE OR synced_to_dwh IS NULL
                ORDER BY created_at DESC
                LIMIT 5
            """)
            print("\nRecent unsynced receipts:")
            for row in cursor.fetchall():
                print(f"  - ID {row[0]}: {row[1]} - €{row[2]} ({row[3]})")
        else:
            print("\n✅ All receipts are synced!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error checking Neon: {e}")


def check_motherduck_status():
    """Check MotherDuck status."""
    print("\n" + "=" * 50)
    print("🦆 MotherDuck Analytics Status")
    print("=" * 50)

    try:
        if MOTHERDUCK_TOKEN:
            conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
            conn.execute("USE receipts_analytics")
        else:
            conn = duckdb.connect('receipts_analytics.duckdb')
            print("⚠️  Using local DuckDB (MOTHERDUCK_TOKEN not set)")

        # Fact receipts
        result = conn.execute("SELECT COUNT(*) FROM fact_receipts").fetchone()
        print(f"Fact receipts: {result[0]}")

        # Items
        result = conn.execute("SELECT COUNT(*) FROM dim_items").fetchone()
        print(f"Items: {result[0]}")

        # Stores
        result = conn.execute("SELECT COUNT(*) FROM dim_store").fetchone()
        print(f"Stores: {result[0]}")

        # Categories
        result = conn.execute("SELECT COUNT(*) FROM dim_categories").fetchone()
        print(f"Categories: {result[0]}")

        # Recent receipts
        print("\nRecent receipts in analytics:")
        result = conn.execute("""
            SELECT
                f.receipt_id,
                s.store_name,
                f.total_amount,
                f.receipt_date
            FROM fact_receipts f
            JOIN dim_store s ON f.store_key = s.store_key
            ORDER BY f.receipt_date DESC
            LIMIT 5
        """).fetchall()

        for row in result:
            print(f"  - ID {row[0]}: {row[1]} - €{row[2]} ({row[3]})")

        conn.close()

    except Exception as e:
        print(f"❌ Error checking MotherDuck: {e}")


def check_sync_consistency():
    """Check if Neon and MotherDuck are in sync."""
    print("\n" + "=" * 50)
    print("🔄 Sync Consistency Check")
    print("=" * 50)

    try:
        # Get Neon synced count
        neon_conn = psycopg2.connect(DATABASE_URL)
        cursor = neon_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM receipts WHERE synced_to_dwh = TRUE")
        neon_synced = cursor.fetchone()[0]
        cursor.close()
        neon_conn.close()

        # Get MotherDuck count
        if MOTHERDUCK_TOKEN:
            md_conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
            md_conn.execute("USE receipts_analytics")
        else:
            md_conn = duckdb.connect('receipts_analytics.duckdb')

        md_count = md_conn.execute("SELECT COUNT(*) FROM fact_receipts").fetchone()[0]
        md_conn.close()

        print(f"Neon synced receipts: {neon_synced}")
        print(f"MotherDuck receipts: {md_count}")

        if neon_synced == md_count:
            print("\n✅ Databases are in sync!")
        else:
            diff = abs(neon_synced - md_count)
            print(f"\n⚠️  Difference: {diff} receipts")
            if neon_synced > md_count:
                print("   → Some synced receipts may be missing in MotherDuck")
            else:
                print("   → MotherDuck has more receipts than marked synced in Neon")

    except Exception as e:
        print(f"❌ Error checking consistency: {e}")


if __name__ == "__main__":
    print("\nETL Status Check\n")
    check_neon_status()
    check_motherduck_status()
    check_sync_consistency()
    print("\n" + "=" * 50)
    print("Status check complete!")
    print("=" * 50 + "\n")
