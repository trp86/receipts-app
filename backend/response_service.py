"""
Response service for sending parsed receipt data back to Telegram.

Responsibilities:
- Format receipt JSON into readable message
- Send message to Telegram chat via Bot API
"""

import requests
import logging

logger = logging.getLogger(__name__)


def format_receipt_message(receipt_data, receipt_id):
    """
    Format parsed receipt data into user-friendly message.

    Args:
        receipt_data: Parsed receipt dictionary
        receipt_id: Database receipt ID

    Returns:
        Formatted message string
    """
    logger.info("Formatting receipt message")

    # Extract key information
    store_name = receipt_data.get('store', {}).get('name', 'Unknown Store')
    total = receipt_data.get('totals', {}).get('sum', 0)
    currency = receipt_data.get('totals', {}).get('currency', 'EUR')
    date = receipt_data.get('receipt', {}).get('date', 'N/A')
    payment_method = receipt_data.get('totals', {}).get('payment_method', 'N/A')

    # Start building message
    message = f"Receipt Processed!\n\n"
    message += f"Store: {store_name}\n"
    message += f"Total: {total} {currency}\n"
    message += f"Date: {date}\n"

    # Add items
    items = receipt_data.get('items', [])
    if items:
        message += f"\nItems ({len(items)}):\n"
        for item in items[:10]:  # Limit to 10 items to avoid message too long
            name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 1)
            price = item.get('total_price', 0)
            message += f"- {name} x{quantity} - {price}{currency}\n"

        if len(items) > 10:
            message += f"... and {len(items) - 10} more items\n"

    # Add payment info
    payment = receipt_data.get('payment', {})
    if payment and payment.get('type'):
        payment_type = payment.get('type', '')
        card_scheme = payment.get('card_scheme', '')
        if card_scheme:
            message += f"\nPayment: {payment_type} ({card_scheme})\n"
        else:
            message += f"\nPayment: {payment_method}\n"
    else:
        message += f"\nPayment: {payment_method}\n"

    # Add receipt ID
    message += f"\nReceipt ID: #{receipt_id}"

    return message


def send_telegram_message(bot_token, chat_id, message):
    """
    Send message to Telegram chat.

    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        message: Message text to send

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Sending message to chat_id: {chat_id}")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Allow basic formatting
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        logger.info(f"Message sent successfully to chat {chat_id}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def send_receipt_response(bot_token, chat_id, receipt_data, receipt_id):
    """
    Format and send receipt data to Telegram user.

    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        receipt_data: Parsed receipt dictionary
        receipt_id: Database receipt ID

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Preparing receipt response for chat_id: {chat_id}, receipt_id: {receipt_id}")

    try:
        # Format message
        message = format_receipt_message(receipt_data, receipt_id)
        logger.info(f"Formatted message length: {len(message)} chars")

        # Send to Telegram
        success = send_telegram_message(bot_token, chat_id, message)

        if success:
            logger.info("Receipt response sent successfully")
        else:
            logger.error("Receipt response failed to send")

        return success

    except Exception as e:
        logger.error(f"Error in send_receipt_response: {e}")
        return False
