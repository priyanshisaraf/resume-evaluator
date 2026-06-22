"""Small manual Gemini connectivity check.

Run with: GEMINI_API_KEY=... python test.py
"""

import json
import os

import requests


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Set GEMINI_API_KEY before running this check.")

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json={"contents": [{"parts": [{"text": "Return a JSON greeting."}]}]},
        timeout=30,
    )
    print("Status Code:", response.status_code)
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
