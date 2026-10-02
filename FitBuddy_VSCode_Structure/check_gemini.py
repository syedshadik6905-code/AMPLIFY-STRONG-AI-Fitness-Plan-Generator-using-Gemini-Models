import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("FAIL: GEMINI_API_KEY is missing.")
    raise SystemExit(1)

print("PASS: API key is configured.")
print("Testing Gemini connection...")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Reply with exactly GEMINI_OK"
    )
    print("PASS: Gemini responded.")
    print("Response:", response.text)

except Exception as exc:
    print("FAIL: Gemini request failed.")
    print("Error type:", type(exc).__name__)
    print("Error:", str(exc))
