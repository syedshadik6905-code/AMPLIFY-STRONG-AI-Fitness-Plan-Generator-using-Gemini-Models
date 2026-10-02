
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env
load_dotenv()

# Gemini model that we successfully tested
MODEL_NAME = "gemini-3.5-flash-lite"

# Read the API key from .env
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

# Create the Gemini client
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=30000),
)


def generate_workout_plan(user):
    """Generate a personalized workout plan."""

    prompt = f"""
You are FitBuddy AI, the fitness coach for AMPLIFY STRONG.

Create a practical workout plan using these details:

Username: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Fitness goal: {user.goal}
Workout intensity: {user.intensity}

Requirements:
1. Include a weekly workout schedule.
2. List exercises, sets, and repetitions.
3. Include warm-up and cool-down guidance.
4. Include rest and recovery advice.
5. Make the plan clear and easy to follow.
6. Avoid guaranteed-result claims.
7. Include a safety note about stopping if exercise causes pain.

Return readable plain text with headings.
"""

    last_error = None

    for attempt in range(3):
        try:
            print(
                f"Workout: sending request to {MODEL_NAME} "
                f"(attempt {attempt + 1}/3)...",
                flush=True,
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if response.text and response.text.strip():
                print("Workout: generation successful.", flush=True)
                return response.text.strip()

            raise RuntimeError("Gemini returned an empty workout plan.")

        except Exception as exc:
            last_error = exc
            print(f"Workout request failed: {exc}", flush=True)

            if attempt < 2:
                time.sleep(2 * (attempt + 1))

    raise RuntimeError(
        f"Workout generation failed after 3 attempts: {last_error}"
    )


def generate_nutrition_tip(user):
    """Generate concise, general nutrition guidance."""

    prompt = f"""
You are FitBuddy AI for AMPLIFY STRONG.

Give one concise, general nutrition guide for this user.

Age: {user.age}
Weight: {user.weight} kg
Fitness goal: {user.goal}

Requirements:
- Recommend balanced meals and adequate hydration.
- Mention recovery and adequate protein from suitable food sources.
- Avoid extreme diets and unsupported supplement claims.
- Do not prescribe a medical diet.
- Keep the response under 100 words.

Return plain text only.
"""

    print("Nutrition: sending request to Gemini...", flush=True)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if response.text and response.text.strip():
            print("Nutrition: generation successful.", flush=True)
            return response.text.strip()

        print("Nutrition: Gemini returned an empty response.", flush=True)

    except Exception as exc:
        # Keep the workout result available if nutrition generation fails.
        print(
            f"Nutrition generation failed: {type(exc).__name__}: {exc}",
            flush=True,
        )

    return (
        "Nutrition tip: Eat balanced meals with suitable protein sources, "
        "include fruits and vegetables, drink enough water, and allow "
        "time for recovery. Adjust your food intake to your individual "
        "needs and seek professional advice for medical dietary concerns."
    )
