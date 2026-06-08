#!/bin/bash
# Test script for quantity analytics API endpoints

BASE_URL="http://localhost:8000"

echo "╔════════════════════════════════════════════╗"
echo "║  Quantity Analytics API Test Suite        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

echo "=== Testing: GET /api/analytics/quantity/summary ==="
curl -s "$BASE_URL/api/analytics/quantity/summary" | jq '.'
echo ""

echo "=== Testing: GET /api/analytics/quantity/bulk-items ==="
curl -s "$BASE_URL/api/analytics/quantity/bulk-items?limit=5" | jq '.'
echo ""

echo "=== Testing: GET /api/analytics/quantity/by-category ==="
curl -s "$BASE_URL/api/analytics/quantity/by-category" | jq '.'
echo ""

echo "=== Testing: GET /api/analytics/quantity/unit-prices ==="
curl -s "$BASE_URL/api/analytics/quantity/unit-prices?limit=5" | jq '.'
echo ""

echo "=== Testing: GET /api/analytics/quantity/trends ==="
curl -s "$BASE_URL/api/analytics/quantity/trends?months=3" | jq '.'
echo ""

echo "✓ All API endpoints tested!"
