"""
Test script for uploading a receipt image to the backend.

Usage:
    python test_upload.py <path_to_receipt_image.jpg>
"""

import sys
import requests

def test_upload(image_path, user_id="test_user_123"):
    """
    Test receipt upload endpoint.

    Args:
        image_path: Path to receipt image
        user_id: User identifier for testing
    """
    print(f"Testing upload with image: {image_path}")
    print(f"User ID: {user_id}")
    print("-" * 50)

    # Read image file
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        print(f"✓ Image loaded: {len(image_data)} bytes")
    except Exception as e:
        print(f"✗ Failed to read image: {e}")
        return

    # Upload to backend
    try:
        url = "http://localhost:8000/api/upload"
        files = {'file': ('receipt.jpg', image_data, 'image/jpeg')}
        data = {'user_id': user_id}

        print(f"Uploading to {url}...")
        response = requests.post(url, files=files, data=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print("✓ Upload successful!")
            print("-" * 50)
            print("Response:")
            print(f"  Receipt ID: {result.get('receipt_id')}")
            print(f"  Success: {result.get('success')}")
            print()
            print("Data:")
            data = result.get('data', {})
            print(f"  Store: {data.get('store_name')}")
            print(f"  Date: {data.get('date')}")
            print(f"  Total: €{data.get('total_amount')}")
            print()
            print(f"  Items ({len(data.get('items', []))}):")
            for item in data.get('items', [])[:5]:
                category = item.get('category', 'N/A')
                subcategory = item.get('subcategory', '')
                cat_info = f" [{category}/{subcategory}]" if category else ""
                print(f"    - {item.get('name')}: €{item.get('price')}{cat_info}")

            if len(data.get('items', [])) > 5:
                print(f"    ... and {len(data.get('items', [])) - 5} more items")

        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"✗ Upload error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_upload.py <path_to_receipt_image>")
        print()
        print("Example:")
        print("  python test_upload.py receipt.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    test_upload(image_path)
