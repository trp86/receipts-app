"""
Test script for quantity analytics endpoints.

Tests all 5 quantity analytics functions against the database.
"""

import sys
import logging
from analytics_quantity_service import (
    get_bulk_purchase_summary,
    get_top_bulk_items,
    get_avg_quantity_by_category,
    get_unit_price_insights,
    get_quantity_trends
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_bulk_summary():
    """Test bulk purchase summary."""
    logger.info("\n=== Testing Bulk Purchase Summary ===")
    try:
        data = get_bulk_purchase_summary()
        logger.info(f"✓ Items in bulk: {data['items_in_bulk']}")
        logger.info(f"✓ Total units: {data['total_units']}")
        logger.info(f"✓ Avg quantity: {data['avg_quantity']}×")
        logger.info(f"✓ Bulk percentage: {data['bulk_percentage']}%")
        return True
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        return False


def test_top_bulk_items():
    """Test top bulk items."""
    logger.info("\n=== Testing Top Bulk Items ===")
    try:
        data = get_top_bulk_items(limit=5)
        logger.info(f"✓ Found {len(data)} bulk items")
        for i, item in enumerate(data[:3], 1):
            logger.info(f"  {i}. {item['item_name']} - Avg: {item['avg_quantity']}× - Category: {item['category']}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        return False


def test_avg_quantity_by_category():
    """Test average quantity by category."""
    logger.info("\n=== Testing Avg Quantity by Category ===")
    try:
        data = get_avg_quantity_by_category()
        logger.info(f"✓ Found {len(data)} categories")
        for cat in data[:5]:
            logger.info(f"  {cat['category']}: {cat['avg_quantity']}× avg ({cat['purchase_count']} purchases)")
        return True
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        return False


def test_unit_price_insights():
    """Test unit price insights."""
    logger.info("\n=== Testing Unit Price Insights ===")
    try:
        data = get_unit_price_insights(limit=5)
        logger.info(f"✓ Found {len(data)} items with price variations")
        for item in data[:3]:
            logger.info(f"  {item['item_name']}")
            logger.info(f"    Best: €{item['best_price']} | Avg: €{item['avg_unit_price']} | High: €{item['highest_price']}")
            logger.info(f"    Potential savings: €{item['potential_savings']}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        return False


def test_quantity_trends():
    """Test quantity trends."""
    logger.info("\n=== Testing Quantity Trends ===")
    try:
        data = get_quantity_trends(months=3)
        logger.info(f"✓ Found {len(data)} data points")

        # Group by month
        months = {}
        for row in data:
            month = row['month']
            if month not in months:
                months[month] = []
            months[month].append(row)

        for month, rows in sorted(months.items())[:3]:
            logger.info(f"  {month}: {len(rows)} categories tracked")

        return True
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("╔════════════════════════════════════════════╗")
    logger.info("║  Quantity Analytics Backend Test Suite    ║")
    logger.info("╚════════════════════════════════════════════╝")

    tests = [
        test_bulk_summary,
        test_top_bulk_items,
        test_avg_quantity_by_category,
        test_unit_price_insights,
        test_quantity_trends
    ]

    results = [test() for test in tests]

    passed = sum(results)
    total = len(results)

    logger.info("\n" + "="*50)
    logger.info(f"Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.error(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
