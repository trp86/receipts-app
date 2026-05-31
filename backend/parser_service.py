import logging
import sys
import json
import os
import requests
import time
import base64

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)


def parse_receipt_image(image_bytes: bytes) -> dict:
    """
    Parse receipt image directly using vision-capable LLM.

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
    logger.info("Starting receipt parsing with vision model")

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not set in environment")
        raise Exception("OPENROUTER_API_KEY not configured")

    # Convert image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    logger.info(f"Image encoded to base64 ({len(image_base64)} chars)")

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

    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://receipts-app-v1co.onrender.com",
        "X-Title": "Receipt Processing App"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }

    try:
        # Call OpenRouter API with retry logic
        max_retries = 2
        retry_count = 0

        while retry_count <= max_retries:
            logger.info(f"Calling OpenRouter with model: {payload['model']} (attempt {retry_count + 1})")
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Log response details for debugging
            logger.info(f"OpenRouter response status: {response.status_code}")

            if response.status_code == 429:
                # Rate limited - check retry-after
                error_data = response.json()
                retry_after = error_data.get("error", {}).get("metadata", {}).get("retry_after_seconds", 15)

                if retry_count < max_retries:
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    retry_count += 1
                    continue
                else:
                    logger.error(f"Max retries reached. OpenRouter error: {response.text}")
                    response.raise_for_status()

            if response.status_code != 200:
                logger.error(f"OpenRouter error response: {response.text}")

            response.raise_for_status()
            break

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
