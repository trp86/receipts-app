import logging
import sys
import json
import os
from PIL import Image
import io
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


def parse_receipt_image(image_bytes: bytes) -> dict:
    """
    Parse receipt image using Google Gemini 2.0 Flash vision model.

    Args:
        image_bytes: Receipt image as bytes

    Returns:
        dict: Structured receipt data
        {
            "store_name": "...",
            "total_amount": "...",
            "date": "YYYY-MM-DD",
            "items": [{"name": "...", "price": "..."}]
        }

    Raises:
        Exception: If parsing fails
    """
    logger.info("Starting receipt parsing with Google Gemini 2.0 Flash")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not set in environment")
        raise Exception("GOOGLE_API_KEY not configured")

    # Configure Gemini
    genai.configure(api_key=google_api_key)

    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Image loaded: {image.format} {image.size}")

    # Prompt for vision model
    prompt = """You are a receipt parser. Look at this receipt image and extract the following information. Return ONLY a valid JSON object (no markdown, no explanation):

{
  "store_name": "store name from receipt",
  "total_amount": "total amount as string with decimal",
  "date": "date in YYYY-MM-DD format",
  "items": [
    {"name": "item name", "price": "item price as string"}
  ]
}

Extract ALL items you can see. If you cannot find a field, use empty string "" or empty array [].

Return ONLY the JSON object, nothing else."""

    try:
        # Use Gemini 2.0 Flash
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("Calling Google Gemini 2.0 Flash...")

        response = model.generate_content([prompt, image])
        llm_output = response.text.strip()

        logger.info(f"Gemini response: {llm_output[:200]}...")

        # Parse JSON from response
        # Remove markdown code blocks if present
        if llm_output.startswith("```json"):
            llm_output = llm_output.replace("```json", "").replace("```", "").strip()
        elif llm_output.startswith("```"):
            llm_output = llm_output.replace("```", "").strip()

        parsed_data = json.loads(llm_output)
        logger.info(f"Parsed receipt data: {parsed_data}")

        # Validate structure
        required_keys = ["store_name", "total_amount", "date", "items"]
        for key in required_keys:
            if key not in parsed_data:
                parsed_data[key] = "" if key != "items" else []

        return parsed_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.error(f"Gemini output was: {llm_output}")
        raise Exception(f"JSON parsing failed: {e}")

    except Exception as e:
        logger.error(f"Receipt parsing failed: {e}")
        raise Exception(f"Receipt parsing failed: {e}")
