"""
Quick OpenAI API key health check.

Usage:
    python test_api.py
    python test_api.py --model gpt-4o-mini
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI


def mask_key(key: str) -> str:
    if len(key) < 12:
        return "***"
    return f"{key[:8]}...{key[-4:]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.getenv("MODEL_NAME", "gpt-4o-mini"))
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        print("[FAIL] OPENAI_API_KEY is missing.")
        return 1

    print(f"[INFO] Key detected: {mask_key(api_key)}")
    print(f"[INFO] Testing model: {args.model}")

    try:
        client = OpenAI(api_key=api_key, timeout=20.0, max_retries=0)
        response = client.responses.create(
            model=args.model,
            input="Reply with exactly: API_OK",
            max_output_tokens=16,
        )
        text = (response.output_text or "").strip()
        print(f"[OK] API request succeeded. Response: {text!r}")
        return 0
    except Exception as exc:
        print(f"[FAIL] API request failed: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
