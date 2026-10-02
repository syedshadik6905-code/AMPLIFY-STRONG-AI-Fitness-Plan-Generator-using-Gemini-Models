
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routes import router
import app.models


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="AMPLIFY STRONG")

# Serve CSS, images, and other static files
app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

# Serve the AMPLIFY STRONG PNG logo as the favicon
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    icon_path = STATIC_DIR / "favicon.png"

    if icon_path.is_file():
        return FileResponse(
            path=str(icon_path),
            media_type="image/png",
        )

    return {
        "message": "Favicon image not found. Place favicon.png inside the static folder."
    }

# Register existing application routes
app.include_router(router)
