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
    logger.info("Starting receipt parsing with Google Gemini 2.5 Flash (single call)")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not set in environment")
        raise Exception("GOOGLE_API_KEY not configured")

    # Configure Gemini
    genai.configure(api_key=google_api_key)

    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Image loaded: {image.format} {image.size}")

    # Single prompt: Extract data from image and return JSON directly
    prompt = """You are a German receipt parser with intelligent error correction. Look at this receipt image and extract ALL information directly into structured JSON.

LANGUAGE & INTELLIGENT CORRECTION:
- This is a GERMAN receipt from Germany
- Receipt text is in German language
- If text is unclear, blurry, or has OCR-like errors, use your intelligence to correct it
- Apply German language knowledge to fix typos and errors:
  * "apppl" or "aple" → "Apfel"
  * "mlch" or "milch" → "Milch"
  * "brot" variations → "Brot"
  * "kase" or "käse" → "Käse"
  * "zwiebel" or "zwieb3l" → "Zwiebel"
  * "tomate" or "tomat3" → "Tomate"
- Common German grocery items: Apfel, Banane, Kartoffel, Zwiebel, Tomate, Milch, Brot, Käse, Butter, Eier, Gurke, Paprika
- Use context from store name and other items to make smart corrections
- If you see numbers/letters mixed incorrectly (like "3" for "E", "0" for "O"), correct them intelligently
- Preserve original spelling if you're confident it's correct, even if unusual
- Use common sense: a grocery receipt won't have random gibberish

Return ONLY a valid JSON object with EXACTLY this structure (use null for missing fields):

{
  "store": {
    "name": "store name",
    "address": {
      "street": "street address",
      "postal_code": "postal code",
      "city": "city",
      "country": "Germany"
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
      "name": "corrected item name in German",
      "quantity": 1.0,
      "unit": "kg or Stk or null",
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

EXTRACTION INSTRUCTIONS:
- Read the receipt image carefully
- Extract EVERY item listed on the receipt
- For each item: name (corrected), quantity (default 1), unit (kg/Stk/null), unit_price, total_price, tax_code
- Extract store: full name, complete address, phone, email, tax_id
- Extract receipt metadata: type, date (YYYY-MM-DD), time (HH:MM:SS), all IDs
- Extract totals: currency, sum, paid_amount, payment_method
- Extract tax: VAT rate %, net, tax, gross amounts
- Extract loyalty: program, earned today, current balance
- Use null for missing fields
- Return numbers as numbers (10.26 not "10.26")
- Return ONLY the JSON object, no markdown, no explanation."""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Single API call: Read image and return JSON directly with German language intelligence
        logger.info("Calling Gemini to extract receipt data with German language correction...")
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
