
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is missing.")
    raise SystemExit(1)

try:
    client = genai.Client(api_key=api_key)

    print("Testing gemini-3.5-flash-lite...", flush=True)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with exactly: GEMINI WORKS"
    )

    print("SUCCESS!")
    print("Gemini response:", response.text, flush=True)

except Exception as exc:
    print("FAIL: Gemini request failed.")
    print("Error type:", type(exc).__name__)
    print("Error:", str(exc), flush=True)
