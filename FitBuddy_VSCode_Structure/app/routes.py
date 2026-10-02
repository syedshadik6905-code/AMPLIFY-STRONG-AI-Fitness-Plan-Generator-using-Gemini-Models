
import traceback

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WorkoutPlan
from app.gemini_generator import (
    generate_workout_plan,
    generate_nutrition_tip,
)
from app.updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def fallback_nutrition_tip():
    return (
        "Stay hydrated and eat balanced meals with suitable protein, "
        "carbohydrates, healthy fats, fruits, and vegetables. Allow "
        "enough time for recovery."
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    user_id: str = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    stage = "starting"

    try:
        print(
            "\n========== GENERATE DIAGNOSTICS ==========",
            flush=True,
        )

        stage = "looking up user"
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        stage = "saving user"

        if user:
            user.username = username
            user.age = age
            user.weight = weight
            user.goal = goal
            user.intensity = intensity
        else:
            user = User(
                user_id=user_id,
                username=username,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        print("User saved.", flush=True)

        stage = "generating workout"
        print("Calling generate_workout_plan...", flush=True)

        original_plan = generate_workout_plan(user)

        if not original_plan:
            raise RuntimeError(
                "Workout generator returned an empty response."
            )

        print("Workout generated.", flush=True)

        stage = "generating nutrition tip"
        print("Calling generate_nutrition_tip...", flush=True)

        try:
            nutrition_tip = generate_nutrition_tip(user)

            if not nutrition_tip:
                nutrition_tip = fallback_nutrition_tip()

        except Exception as exc:
            print(
                "Nutrition generation failed; using fallback: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )
            traceback.print_exc()
            nutrition_tip = fallback_nutrition_tip()

        print("Nutrition tip ready.", flush=True)

        stage = "saving workout plan"

        plan = WorkoutPlan(
            user_id=user.user_id,
            original_plan=str(original_plan),
            updated_plan=str(original_plan),
            nutrition_tip=str(nutrition_tip),
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        print("Plan saved.", flush=True)

        stage = "rendering result.html"

        response = templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "workout_plan": plan.updated_plan,
                "nutrition_tip": plan.nutrition_tip,
            },
        )

        print(
            "========== GENERATE SUCCESS ==========\n",
            flush=True,
        )

        return response

    except Exception as exc:
        db.rollback()

        print("\n========== GENERATE FAILED ==========", flush=True)
        print(f"Failed stage: {stage}", flush=True)
        print(
            f"Exception: {type(exc).__name__}: {exc}",
            flush=True,
        )
        traceback.print_exc()
        print(
            "========== END DIAGNOSTICS ==========\n",
            flush=True,
        )

        raise


@router.post("/feedback/{plan_id}", response_class=HTMLResponse)
def feedback(
    plan_id: int,
    request: Request,
    feedback_text: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        plan = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.id == plan_id)
            .first()
        )

        if plan is None:
            return HTMLResponse(
                "Workout plan not found.",
                status_code=404,
            )

        user = (
            db.query(User)
            .filter(User.user_id == plan.user_id)
            .first()
        )

        if user is None:
            return HTMLResponse(
                "User associated with this plan was not found.",
                status_code=404,
            )

        updated = update_workout_plan(
            user=user,
            current_plan=plan.updated_plan or plan.original_plan,
            feedback=feedback_text,
        )

        if not updated:
            raise RuntimeError(
                "Plan update generator returned an empty response."
            )

        plan.updated_plan = str(updated)

        db.commit()
        db.refresh(plan)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "workout_plan": plan.updated_plan,
                "nutrition_tip": plan.nutrition_tip,
            },
        )

    except Exception:
        db.rollback()

        print("\n========== FEEDBACK FAILED ==========", flush=True)
        traceback.print_exc()
        print(
            "========== END FEEDBACK DIAGNOSTICS ==========\n",
            flush=True,
        )

        raise


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    users = db.query(User).all()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )


@router.post("/delete-user/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    try:
        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if user is None:
            return HTMLResponse(
                "User not found.",
                status_code=404,
            )

        # Delete the user's plans before deleting the user.
        db.query(WorkoutPlan).filter(
            WorkoutPlan.user_id == user.user_id
        ).delete(synchronize_session=False)

        db.delete(user)
        db.commit()

        return RedirectResponse(
            url="/view-all-users",
            status_code=303,
        )

    except Exception:
        db.rollback()
        print("\n========== DELETE USER FAILED ==========", flush=True)
        traceback.print_exc()
        raise
