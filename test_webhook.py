"""
Test script for Telegram webhook endpoint.

Usage:
1. Start backend: cd backend && uvicorn main:app --reload
2. Run this script: python test_webhook.py
"""

import requests

WEBHOOK_URL = "http://localhost:8080/webhook"


def test_with_photo():
    """Test webhook with photo message"""
    print("\n=== Test 1: Message with photo ===")

    payload = {
        "update_id": 123456789,
        "message": {
            "message_id": 456,
            "from": {
                "id": 987654321,
                "first_name": "Test User"
            },
            "chat": {
                "id": 987654321,
                "type": "private"
            },
            "date": 1622548800,
            "photo": [
                {
                    "file_id": "AgACAgIAAxkBAATestLowRes",
                    "file_size": 1024,
                    "width": 320,
                    "height": 240
                },
                {
                    "file_id": "AgACAgIAAxkBAATestHighRes",
                    "file_size": 5120,
                    "width": 1280,
                    "height": 720
                }
            ]
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


def test_without_photo():
    """Test webhook with text message (no photo)"""
    print("\n=== Test 2: Message without photo ===")

    payload = {
        "update_id": 123456790,
        "message": {
            "message_id": 457,
            "from": {
                "id": 987654321,
                "first_name": "Test User"
            },
            "chat": {
                "id": 987654321,
                "type": "private"
            },
            "date": 1622548800,
            "text": "Hello bot!"
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


def test_health_check():
    """Test root endpoint"""
    print("\n=== Test 3: Health check ===")

    try:
        response = requests.get("http://localhost:8080/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Starting webhook tests...")
    print("Make sure backend is running: cd backend && uvicorn main:app --reload")

    test_health_check()
    test_with_photo()
    test_without_photo()

    print("\n=== Tests complete ===")
    print("Check backend terminal for logged output")
