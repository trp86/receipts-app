import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


def process_telegram_update(update_data: dict) -> dict:
    """
    Process incoming Telegram webhook update.

    Extracts chat_id and file_id if photo exists.
    Returns dict with extracted data or None values.
    """
    logger.info(f"Received update: {update_data}")

    # Check if message exists
    message = update_data.get("message")
    if not message:
        logger.warning("No 'message' field in update")
        return {"chat_id": None, "file_id": None}

    # Check if photo exists
    photo_array = message.get("photo")
    if not photo_array or len(photo_array) == 0:
        logger.info("No photo found in message")
        return {"chat_id": None, "file_id": None}

    logger.info("Photo detected in message")

    # Extract chat_id
    chat = message.get("chat", {})
    chat_id = chat.get("id")

    # Extract file_id from highest resolution photo (last element)
    highest_res_photo = photo_array[-1]
    file_id = highest_res_photo.get("file_id")

    logger.info(f"Extracted chat_id: {chat_id}")
    logger.info(f"Extracted file_id: {file_id}")

    return {
        "chat_id": chat_id,
        "file_id": file_id
    }
