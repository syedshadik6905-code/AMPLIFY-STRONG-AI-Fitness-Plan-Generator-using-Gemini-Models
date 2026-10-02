
# app/gemini_flash_generator.py

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


def generate_nutrition_tip(user):
    prompt = f"""
You are FitBuddy AI, the nutrition assistant for AMPLIFY STRONG.

User details:
- Username: {user.username}
- Age: {user.age}
- Weight in kg: {user.weight}
- Fitness goal: {user.goal}
- Workout intensity: {user.intensity}

Provide practical, general nutrition guidance suitable for the user's
fitness goal. Include hydration, balanced meals, protein sources,
vegetables, and recovery nutrition.

Do not prescribe extreme diets, promise results, or make unsupported
medical claims. Keep the advice concise and easy to understand.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty nutrition tip.")

        return response.text

    except Exception as exc:
        raise RuntimeError(
            f"Gemini nutrition generation failed: {exc}"
        ) from exc
