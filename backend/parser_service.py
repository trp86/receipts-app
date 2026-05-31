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
    logger.info("Starting receipt parsing with Google Gemini 2.5 Flash")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not set in environment")
        raise Exception("GOOGLE_API_KEY not configured")

    # Configure Gemini
    genai.configure(api_key=google_api_key)

    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Image loaded: {image.format} {image.size}")

    # Step 1: Extract ALL text from image
    ocr_prompt = """You are an OCR text extraction system.

Extract ALL visible text from this receipt image.

IMPORTANT RULES:
- Capture EVERY piece of text visible in the image
- Do NOT summarize
- Do NOT interpret or structure the data
- Do NOT convert to JSON
- Preserve original layout as much as possible
- Keep line breaks
- Keep order of text as seen in the image
- Include ALL numbers, prices, totals, dates, IDs, addresses

If text is unclear, make the best possible guess, but DO NOT skip it.

Return ONLY the extracted raw text."""

    # Step 2: Parse extracted text to JSON
    parse_prompt = """You are a receipt parser. Take this raw receipt text and extract ALL available information into structured data.

Return ONLY a valid JSON object with EXACTLY this structure (use null for missing fields):

{
  "store": {
    "name": "store name",
    "address": {
      "street": "street address",
      "postal_code": "postal code",
      "city": "city",
      "country": "country"
    },
    "contact": {
      "phone": "phone number",
      "email": "email"
    },
    "tax_id": "tax ID"
  },
  "receipt": {
    "type": "receipt type (e.g., Kundenbeleg)",
    "date": "YYYY-MM-DD",
    "time": "HH:MM:SS",
    "receipt_number": "receipt number",
    "trace_number": "trace number",
    "market_number": "market/store number",
    "cash_register": "register number",
    "cashier_id": "cashier ID",
    "bon_number": "bon number"
  },
  "items": [
    {
      "name": "item name",
      "quantity": 1.0,
      "unit": "kg or Stk or null if not applicable",
      "unit_price": 1.99,
      "total_price": 1.99,
      "tax_code": "A or B or C"
    }
  ],
  "totals": {
    "currency": "EUR",
    "sum": 10.26,
    "paid_amount": 10.26,
    "payment_method": "Card or Cash or other"
  },
  "tax": {
    "vat_rate_percent": 7.0,
    "net_amount": 9.59,
    "tax_amount": 0.67,
    "gross_amount": 10.26
  },
  "loyalty": {
    "program": "loyalty program name",
    "earned_today": 0.10,
    "current_balance": 1.70
  }
}

CRITICAL INSTRUCTIONS:
- Extract EVERY item listed on the receipt
- For each item, extract: name, quantity (default 1 if not shown), unit (kg/Stk/null), unit_price (if shown), total_price, tax_code
- Extract store: full name, complete address (street, postal_code, city, country), phone, email, tax_id
- Extract receipt metadata: type, date (YYYY-MM-DD), time (HH:MM:SS), all numbers and IDs
- Extract totals: currency, sum, paid_amount, payment_method
- Extract tax: VAT rate %, net amount, tax amount, gross amount
- Extract loyalty: program name, points earned today, current balance
- Use null for missing fields, NOT empty strings
- Return numbers as numbers, not strings (e.g., 10.26 not "10.26")
- Return ONLY the JSON object, no markdown, no explanation."""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Step 1: Extract ALL text (API call 1)
        logger.info("Step 1: Extracting ALL text from image...")
        ocr_response = model.generate_content([ocr_prompt, image])
        raw_text = ocr_response.text.strip()
        logger.info(f"Extracted text ({len(raw_text)} chars):\n{raw_text[:500]}...")

        # Step 2: Parse text to JSON (API call 2)
        logger.info("Step 2: Parsing text to JSON...")
        parse_response = model.generate_content(f"{parse_prompt}\n\nReceipt text:\n{raw_text}")
        llm_output = parse_response.text.strip()

        logger.info(f"Gemini parse response: {llm_output[:200]}...")

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
