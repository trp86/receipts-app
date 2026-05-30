import logging
import sys
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


def download_image(bot_token: str, file_id: str) -> bytes:
    """
    Download image from Telegram using file_id.

    Returns image as bytes (in-memory, no file persistence).

    Args:
        bot_token: Telegram bot token
        file_id: File ID from Telegram photo message

    Returns:
        bytes: Image data

    Raises:
        Exception: If download fails
    """
    logger.info(f"Starting image download for file_id: {file_id[:20]}...")

    # Step 1: Get file path from Telegram API
    get_file_url = f"https://api.telegram.org/bot{bot_token}/getFile"
    params = {"file_id": file_id}

    try:
        response = requests.get(get_file_url, params=params, timeout=10)
        response.raise_for_status()
        file_data = response.json()

        if not file_data.get("ok"):
            error_msg = f"Telegram API error: {file_data}"
            logger.error(error_msg)
            raise Exception(error_msg)

        file_path = file_data["result"]["file_path"]
        logger.info(f"Got file_path: {file_path}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get file path: {e}")
        raise Exception(f"Failed to get file path: {e}")

    # Step 2: Download the actual file
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    try:
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        image_bytes = response.content

        logger.info(f"Downloaded image successfully: {len(image_bytes)} bytes")
        return image_bytes

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image: {e}")
        raise Exception(f"Failed to download image: {e}")
