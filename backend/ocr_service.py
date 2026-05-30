import logging
import sys
from PIL import Image
import pytesseract
import io

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


def extract_text(image_bytes: bytes) -> str:
    """
    Extract text from image using Tesseract OCR.

    Args:
        image_bytes: Image data as bytes

    Returns:
        str: Extracted text (raw, unprocessed)

    Raises:
        Exception: If OCR fails
    """
    logger.info(f"Starting OCR on image ({len(image_bytes)} bytes)")

    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        logger.info(f"Image opened: {image.format} {image.size} {image.mode}")

        # Run Tesseract OCR
        text = pytesseract.image_to_string(image)

        # Log result
        text_length = len(text)
        text_preview = text[:100].replace('\n', ' ') if text else "(empty)"
        logger.info(f"OCR completed: {text_length} characters extracted")
        logger.info(f"Text preview: {text_preview}...")

        return text

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise Exception(f"OCR failed: {e}")
