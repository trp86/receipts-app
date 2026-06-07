#!/bin/bash
# Test receipt upload with categories

# Usage: ./test_upload_curl.sh path/to/receipt.jpg

if [ -z "$1" ]; then
  echo "Usage: ./test_upload_curl.sh path/to/receipt.jpg"
  exit 1
fi

RECEIPT_IMAGE="$1"

echo "🚀 Uploading receipt to production backend..."
echo "File: $RECEIPT_IMAGE"
echo ""

curl -X POST https://receipts-app-v1co.onrender.com/api/upload \
  -F "file=@$RECEIPT_IMAGE" \
  -F "user_id=test_user_$(date +%s)" \
  | python -m json.tool

echo ""
echo "✅ Upload complete!"
echo ""
echo "Check if items have 'category' and 'subcategory' fields!"
