"""
Test database connection and table creation
"""
import sys
sys.path.append('backend')

from db_service import init_database, insert_receipt

print("Testing database connection...")

# Test 1: Initialize schema
try:
    init_database()
    print("[OK] Database schema initialized")
except Exception as e:
    print(f"[ERROR] Schema initialization failed: {e}")
    exit(1)

# Test 2: Insert test receipt with NESTED structure (like real parser output)
test_receipt = {
    "store": {
        "name": "Test Store Netto"
    },
    "receipt": {
        "date": "2026-06-02"
    },
    "totals": {
        "sum": 99.99,
        "currency": "EUR"
    },
    "items": [
        {"name": "Test Item", "price": 99.99}
    ]
}

try:
    receipt_id = insert_receipt(123456789, test_receipt)
    print(f"[OK] Test receipt inserted with ID: {receipt_id}")
except Exception as e:
    print(f"[ERROR] Insert failed: {e}")
    exit(1)

print("\n[SUCCESS] All database tests passed!")
