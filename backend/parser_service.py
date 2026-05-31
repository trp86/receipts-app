import logging
import sys
import json
import os
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


def parse_receipt_text(ocr_text: str) -> dict:
    """
    Parse OCR text into structured JSON using OpenRouter LLM.

    Args:
        ocr_text: Raw text extracted from receipt image

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
    logger.info("Starting receipt parsing with OpenRouter")

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not set in environment")
        raise Exception("OPENROUTER_API_KEY not configured")

    # Prompt for LLM
    prompt = f"""You are a receipt parser. Extract the following information from this receipt text and return ONLY a valid JSON object (no markdown, no explanation):

{{
  "store_name": "store name from receipt",
  "total_amount": "total amount as string with decimal",
  "date": "date in YYYY-MM-DD format",
  "items": [
    {{"name": "item name", "price": "item price as string"}}
  ]
}}

If you cannot find a field, use empty string "" or empty array [].

Receipt text:
{ocr_text}

Return ONLY the JSON object, nothing else."""

    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://receipts-app-v1co.onrender.com",
        "X-Title": "Receipt Processing App"
    }

    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }

    try:
        # Call OpenRouter API
        logger.info(f"Calling OpenRouter with model: {payload['model']}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        # Log response details for debugging
        logger.info(f"OpenRouter response status: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"OpenRouter error response: {response.text}")

        response.raise_for_status()

        response_data = response.json()
        llm_output = response_data["choices"][0]["message"]["content"].strip()

        logger.info(f"LLM raw response: {llm_output[:200]}...")

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
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"LLM output was: {llm_output}")
        raise Exception(f"JSON parsing failed: {e}")

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        raise Exception(f"OpenRouter API request failed: {e}")

    except Exception as e:
        logger.error(f"Receipt parsing failed: {e}")
        raise Exception(f"Receipt parsing failed: {e}")
