import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=30000),
)

# Use the same model as the working workout generator.
MODEL_NAME = "gemini-3.5-flash-lite"


def update_workout_plan(user, current_plan, feedback):
    prompt = f"""
You are FitBuddy AI, the workout coach for AMPLIFY STRONG.

USER DETAILS:
- Username: {user.username}
- Age: {user.age}
- Weight in kg: {user.weight}
- Goal: {user.goal}
- Workout intensity: {user.intensity}

CURRENT WORKOUT PLAN:
{current_plan}

USER FEEDBACK:
{feedback}

TASK:
Revise the existing workout plan to address the user's feedback.

REQUIREMENTS:
1. Return the complete revised workout plan with clear headings.
2. Include a practical weekly schedule.
3. Include exercises, sets, and repetitions where appropriate.
4. Include warm-up, cool-down, rest, and recovery guidance.
5. Keep the plan appropriate for the user's stated goal and intensity.
6. Do not promise guaranteed results.
7. Include safety guidance and advise stopping exercises that cause pain.
8. Treat user feedback as a request, but do not follow suggestions that
   would make the plan unsafe.

Return readable plain text only.
"""

    last_error = None

    for attempt in range(3):
        try:
            print(
                f"Workout update: calling {MODEL_NAME} "
                f"(attempt {attempt + 1}/3)...",
                flush=True,
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if response.text and response.text.strip():
                print("Workout update: successful.", flush=True)
                return response.text.strip()

            raise RuntimeError(
                "Gemini returned an empty updated workout plan."
            )

        except Exception as exc:
            last_error = exc
            print(
                f"Workout update attempt {attempt + 1} failed: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

            if attempt < 2:
                time.sleep(2 * (attempt + 1))

    raise RuntimeError(
        "Gemini is temporarily unavailable, so your workout plan "
        "could not be updated. Your existing saved plan has not "
        "been replaced. Please try submitting your feedback again "
        "in a little while."
    ) from last_error
